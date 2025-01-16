import cv2
import numpy as np
import torch
from torchvision import models, transforms
from torchvision.models.detection import ssdlite320_mobilenet_v3_large
from torchvision.models.detection.ssdlite import SSDLite320_MobileNet_V3_Large_Weights
import time
from tools import tools
from app import app, db
from model.people_counter import people_counter


# Check if a GPU is available and set the device accordingly
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Load a pre-trained SSD model for person detection and move it to the GPU if available
model = ssdlite320_mobilenet_v3_large(weights=SSDLite320_MobileNet_V3_Large_Weights.DEFAULT)
model.to(device)
model.eval()

# Define the transformation to apply to the input frames
transform = transforms.Compose([
    transforms.ToTensor()
])

def main():
    # Define a single line for counting entries and exits as a percentage of the frame height
    count_line_percentage = 0.5  # 50% from the top
    entry_count = 0
    exit_count = 0
    script_start_time = tools.now()

    # Initialize a dictionary to store the centroids and their states
    centroid_dict = {}
    next_object_id = 0
    stale_threshold = 0.5  # Time in seconds to consider a centroid as stale

    # Initialize a list to store the times of people entering and exiting
    people_in_to_save = []
    people_out_to_save = []

    loop_count = 1

    # Open a connection to the webcam
    cap = cv2.VideoCapture(0)

    # Get the frame rate of the webcam
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Frame rate: {fps} FPS")

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break

        # Calculate the count line based on the frame height
        frame_height = frame.shape[0]
        count_line = int(frame_height * count_line_percentage)

        # Measure time taken for model inference
        start_time = time.time()

        # Convert the frame to a tensor and move it to the GPU if available
        frame_tensor = transform(frame).to(device)
        with torch.no_grad():
            predictions = model([frame_tensor])[0]

        inference_time = time.time() - start_time
        # print(f"Inference time: {inference_time:.4f} seconds")

        # Initialize a list to store the new centroids
        new_centroids = []

        # Draw bounding boxes around detected people and track their movement
        for box, label, score in zip(predictions['boxes'], predictions['labels'], predictions['scores']):
            if label == 1 and score > 0.5:  # Label 1 is for person
                x1, y1, x2, y2 = box.int().cpu().numpy()
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                new_centroids.append((center_x, center_y))

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Update the centroids and count entries/exits
        current_time = time.time()
        for new_centroid in new_centroids:
            matched = False
            for object_id, (old_centroid, timestamp, state) in centroid_dict.items():
                if old_centroid is not None and np.linalg.norm(np.array(new_centroid) - np.array(old_centroid)) < 50:
                    centroid_dict[object_id] = (new_centroid, current_time, state)
                    matched = True
                    break
            if not matched:
                centroid_dict[next_object_id] = (new_centroid, current_time, 'new')
                next_object_id += 1

        # Check if any centroids crossed the count line
        for object_id, (centroid, timestamp, state) in list(centroid_dict.items()):
            if state == 'new':
                if centroid[1] < count_line:
                    centroid_dict[object_id] = (centroid, timestamp, 'above')
                else:
                    centroid_dict[object_id] = (centroid, timestamp, 'below')
            elif state == 'above' and centroid[1] >= count_line:
                entry_count += 1
                centroid_dict[object_id] = (centroid, timestamp, 'Enter')
                people_in_to_save.append(tools.now())  # for the moment we will only save the time of entry
            elif state == 'below' and centroid[1] <= count_line:
                exit_count += 1
                centroid_dict[object_id] = (centroid, timestamp, 'Exit')
                people_out_to_save.append(tools.now())  # for the moment we will only save the time of exit
            # Draw the centroid state
            if state == 'Enter':
                text_to_display = f'Entry {current_time - timestamp:.1f}s'
                cv2.putText(frame, text_to_display, (centroid[0] + 10, centroid[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            elif state == 'Exit':
                text_to_display = f'Exit {current_time - timestamp:.1f}s'
                cv2.putText(frame, text_to_display, (centroid[0] + 10, centroid[1] + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

        # Remove stale centroids
        for object_id, (centroid, timestamp, state) in list(centroid_dict.items()):
            if current_time - timestamp > stale_threshold:
                del centroid_dict[object_id]

        # Draw the count line
        cv2.line(frame, (0, count_line), (frame.shape[1], count_line), (0, 255, 0), 2)

        # Display the script_start_time in left upper corner
        cv2.putText(frame, f'Start Time: {script_start_time}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        # Display the exit count in the left upper corner
        cv2.putText(frame, f'Exit Count: {exit_count}', (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        # Display the entry count in the left bottom corner
        cv2.putText(frame, f'Entry Count: {entry_count}', (10, frame_height - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow('Frame', frame)
        cv2.waitKey(1)  # Wait for 1ms to allow the frame to be displayed

        # Save the people_in_to_save and people_out_to_save lists to the database every 10 loops
        if loop_count % (fps * 10) == 0:  # 300 loops at 30 FPS is 10 seconds
            with app.app_context():
                for timestamp in people_in_to_save:
                    people_counter.add_entry(db, timestamp)
                for timestamp in people_out_to_save:
                    people_counter.add_exit(db, timestamp)
                people_in_to_save = []
                people_out_to_save = []
                db.session.commit()
            loop_count = 0
            print("Saved entries and exits to the database at", tools.now())

        loop_count += 1

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()