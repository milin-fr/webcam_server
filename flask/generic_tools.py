from pytz import timezone as pytz_timezone
from datetime import datetime, timezone, timedelta
import babel


class GenericTools:
    def today(self):
        """shorthand to get current paris time in Y-m-d format"""
        return self.get_paris_datetime().strftime("%Y-%m-%d")

    def now(self):
        """shorthand to get current paris time in Y-m-d H:M:S format, consistant with mysql datetime str representation"""
        return self.get_string_from_datetime(self.get_paris_datetime())

    def get_paris_datetime(self, timedelta_minutes=0):
        paris_timezone = pytz_timezone('Europe/Paris')
        now_utc = datetime.now(timezone.utc)
        if timedelta_minutes:
            if timedelta_minutes > 0:
                now_utc = now_utc + timedelta(minutes=timedelta_minutes)
            else:
                now_utc = now_utc - timedelta(minutes=abs(timedelta_minutes))
        paris_datetime = now_utc.astimezone(paris_timezone)
        return paris_datetime

    def get_paris_datetime_at_hour(self, hour, minute=0, second=0):
        paris_datetime = self.get_paris_datetime()
        paris_datetime = paris_datetime.replace(hour=hour, minute=minute, second=second)
        return paris_datetime

    def increment_time_by_minutes(self, datetime_obj, minutes):
        return datetime_obj + timedelta(minutes=minutes)

    def get_string_from_datetime(self, date):
        """Y-m-d H:M:S format, consistant with mysql datetime str representation"""
        return date.strftime("%Y-%m-%d %H:%M:%S")

    def get_datetime_from_string(self, datetime_string):
        """
            Y-m-d H:M:S format, consistant with mysql datetime str representation, striped of miliseconds
            returns a timezone aware datetime object in 'Europe/Paris' timezone
        """
        datetime_string = datetime_string.split(".")[0]  # strip miliseconds
        return datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S").replace(tzinfo=pytz_timezone('Europe/Paris'))

    def get_datetime_from_date_string(self, date_string):
        """Y-m-d format"""
        return datetime.strptime(date_string, "%Y-%m-%d").replace(tzinfo=pytz_timezone('Europe/Paris'))

    def format_datetime(self, data, format="datetime"):
        date = self.get_datetime_from_string(data)
        if format == "date":
            format = "dd/MM/yyyy"
        elif format == "time":
            format = "HH:mm:ss"
        elif format == "full":
            return babel.dates.format_datetime(date, locale="fr_FR")
        elif format == "datetime":
            format = "dd/MM/yyyy HH:mm:ss"
        else:
            format = "dd/MM/yyyy 'à' HH:mm:ss"
        return babel.dates.format_datetime(date, format)


generic_tools = GenericTools()


if __name__ == "__main__":
    # debug only
    print(generic_tools.get_paris_datetime())
    print(generic_tools.get_paris_datetime(0))
    print(generic_tools.get_paris_datetime(60))
    print(generic_tools.get_paris_datetime(-60))
    print(generic_tools.get_paris_datetime(-60 * 24))
    print(generic_tools.now())
