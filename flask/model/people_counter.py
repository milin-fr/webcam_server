from sqlalchemy import text

class PeopleCounter:
    def add_entry(self, db, timestamp):
        db.session.execute(text("""
            INSERT INTO
                people_counter_in
            (
                timestamp
            )
            VALUES
            (
                :timestamp
            )
        """), {"timestamp": timestamp}, bind_arguments={"bind": db.engines["people_counter_database"]})

    def add_exit(self, db, timestamp):
        db.session.execute(text("""
            INSERT INTO
                people_counter_out
            (
                timestamp
            )
            VALUES
            (
                :timestamp
            )
        """), {"timestamp": timestamp}, bind_arguments={"bind": db.engines["people_counter_database"]})

    def get_entry_timestamp_list_since_timestamp(self, db, timestamp):
        query = text("""
            SELECT
                timestamp
            FROM
                people_counter_in
            WHERE
                timestamp >= :timestamp
            ORDER BY
                timestamp ASC
        """)
        execution = db.session.execute(query, {"timestamp": timestamp}, bind_arguments={"bind": db.engines["people_counter_database"]})
        data = execution.fetchall()
        return data

    def get_exit_timestamp_list_since_timestamp(self, db, timestamp):
        query = text("""
            SELECT
                timestamp
            FROM
                people_counter_out
            WHERE
                timestamp >= :timestamp
            ORDER BY
                timestamp ASC
        """)
        execution = db.session.execute(query, {"timestamp": timestamp}, bind_arguments={"bind": db.engines["people_counter_database"]})
        data = execution.fetchall()
        return data


people_counter = PeopleCounter()
