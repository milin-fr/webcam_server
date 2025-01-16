from flask import (
    render_template
)
from app import app, db
from tools import tools
from model.people_counter import people_counter


@app.route('/')
def index():
    today_at_8 = tools.get_paris_datetime_at_hour(8)
    today_at_8_string = tools.get_string_from_datetime(today_at_8)
    entry_timestamp_list = people_counter.get_entry_timestamp_list_since_timestamp(db, today_at_8_string)
    exit_timestamp_list = people_counter.get_exit_timestamp_list_since_timestamp(db, today_at_8_string)
    entry_count_by_timelapse_list = []
    # sort quantity of entries by x minutes
    start_time = today_at_8
    end_time = tools.increment_time_by_minutes(start_time, 60)
    while start_time < tools.get_paris_datetime():
        entry_count_by_timelapse_list.append(
            {
                "start_time": start_time.strftime("%H:%M:%S"),
                "end_time": end_time.strftime("%H:%M:%S"),
                "entry_count": 0,
                "exit_count": 0
            }
        )
        entry_count = 0
        for timestamp in entry_timestamp_list:
            if start_time <= tools.get_datetime_from_string(timestamp[0]) < end_time:
                entry_count += 1
        exit_count = 0
        for timestamp in exit_timestamp_list:
            if start_time <= tools.get_datetime_from_string(timestamp[0]) < end_time:
                exit_count += 1
        entry_count_by_timelapse_list[-1]["entry_count"] = entry_count
        entry_count_by_timelapse_list[-1]["exit_count"] = exit_count
        start_time = end_time
        end_time = tools.increment_time_by_minutes(start_time, 60)
    return render_template('index.html', entry_count_by_timelapse_list=entry_count_by_timelapse_list)
