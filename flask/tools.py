import json
import uuid
from PIL import Image
from io import BytesIO
import base64
from generic_tools import GenericTools
from PIL import Image


class Tools(GenericTools):
    def to_dictionary(self, data):
        """making sure that data retrieved from db is compatible with json format"""
        if isinstance(data, list):
            results = []
            for row in data:
                to_dictionary = dict(row._mapping)
                for key, value in to_dictionary.items():
                    try:
                        to_dictionary[key] = value.decode('cp1252')
                    except:
                        pass
                to_json = json.dumps(to_dictionary, default=str)
                results.append(json.loads(to_json))
        else:
            to_dictionary = dict(data._mapping)
            for key, value in to_dictionary.items():
                try:
                    to_dictionary[key] = value.decode('cp1252')
                except:
                    pass
            to_json = json.dumps(to_dictionary, default=str)
            results = json.loads(to_json)
        return results

    def get_unique_token(self):
        return str(uuid.uuid1().int)

    def get_unique_string_token(self):
        return str(uuid.uuid1())

    def get_resized_b64_image(self, b64_image, max_length):
        try:
            image_to_resize = Image.open(BytesIO(base64.b64decode(b64_image)))
            image_width, image_height = image_to_resize.size
            if image_width > image_height:
                ratio = max_length / float(image_width)
                new_height = int((float(image_height) * float(ratio)))
                resized_image = image_to_resize.resize((max_length, new_height), Image.NEAREST)
            else:
                ratio = max_length / float(image_height)
                new_width = int((float(image_width) * float(ratio)))
                resized_image = image_to_resize.resize((new_width, max_length), Image.NEAREST)
            buffer = BytesIO()
            resized_image = resized_image.convert("RGB")
            resized_image.save(buffer, "webp")
            resized_b64_image_bytes = base64.b64encode(buffer.getvalue())
            resized_b64_image = resized_b64_image_bytes.decode("utf-8")
        except Exception as e:
            resized_b64_image = None
        return resized_b64_image

    def image_bytes_to_base64_string(self, image_bytes):
        image = BytesIO(image_bytes)
        b64_image_bytes = base64.b64encode(image.read())
        b64_image = b64_image_bytes.decode("utf-8")
        return b64_image

    def get_image_from_b64(self, b64_image):
        try:
            image = BytesIO(base64.b64decode(b64_image))
        except Exception as e:
            image = None
        return image

    def upload_is_image(self, file):
        allowed_extentions = ["png", "jpeg", "jpg"]
        filename = ""
        if hasattr(file, 'filename'):
            filename = file.filename
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extentions

    def pillow_image_to_b64(self, pillow_image, width=1024):
        b64_image = ""
        image_width, image_height = pillow_image.size
        if image_width > width:
            ratio = width / float(image_width)
            new_height = int((float(image_height) * float(ratio)))
            resized_image = pillow_image.resize((width, new_height), Image.NEAREST)
        else:
            resized_image = pillow_image
        buffer = BytesIO()
        resized_image = resized_image.convert("RGB")
        resized_image.save(buffer, format="JPEG")
        resized_b64_image_bytes = base64.b64encode(buffer.getvalue())
        b64_image = resized_b64_image_bytes.decode("utf-8")
        return b64_image

    def image_to_base64(self, image, max_length=1024):
        resized_b64_image = ""
        if self.upload_is_image(image):
            image_to_resize = Image.open(image)
            image_width, image_height = image_to_resize.size
            if image_width > image_height:
                ratio = max_length / float(image_width)
                new_height = int((float(image_height) * float(ratio)))
                resized_image = image_to_resize.resize((max_length, new_height), Image.NEAREST)
            else:
                ratio = max_length / float(image_height)
                new_width = int((float(image_width) * float(ratio)))
                resized_image = image_to_resize.resize((new_width, max_length), Image.NEAREST)
            buffer = BytesIO()
            resized_image = resized_image.convert("RGB")
            resized_image.save(buffer, format="JPEG")
            resized_b64_image_bytes = base64.b64encode(buffer.getvalue())
            resized_b64_image = resized_b64_image_bytes.decode("utf-8")
        return resized_b64_image

    def pdf_to_base64(self, pdf):
        b64_pdf = ""
        if pdf:
            pdf_to_encode = pdf.read()
            b64_pdf = base64.b64encode(pdf_to_encode)
        return b64_pdf

    def get_file_object_from_blob(self, blob):
        if isinstance(blob, str):  # file was stored as base64 string
            blob = base64.b64decode(blob)
        file_object = BytesIO(blob)
        return file_object

    def resize_pillow_image(self, pillow_image, max_length=1024):
        resized_image = ""
        image_width, image_height = pillow_image.size
        if image_width > image_height:
            ratio = max_length / float(image_width)
            new_height = int((float(image_height) * float(ratio)))
            resized_image = pillow_image.resize((max_length, new_height), Image.NEAREST)
        else:
            ratio = max_length / float(image_height)
            new_width = int((float(image_width) * float(ratio)))
            resized_image = pillow_image.resize((new_width, max_length), Image.NEAREST)
        return resized_image

    def pil_image_to_bytes(self, image):
        image_bytes = BytesIO()
        image = image.convert("RGB")  # this is to avoid issues with images that have transparency
        image.save(image_bytes, format="JPEG")
        image_bytes = image_bytes.getvalue()
        return image_bytes

    def pil_image_from_bytes(self, image_bytes):
        image = Image.open(BytesIO(image_bytes))
        return image


tools = Tools()

if __name__ == "__main__":
    print(tools.get_paris_datetime())
    print(tools.get_paris_datetime(-60))

