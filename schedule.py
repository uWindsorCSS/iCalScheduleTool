from datetime import datetime
from jinja2 import Template

ICAL_DATE_FORMAT = "%Y%m%dT%H%M%S"

class WeeklyEvent:
    def __init__(self, title, start_time, end_time, location, count):
        self.title = title
        self.start_time = start_time.strftime(ICAL_DATE_FORMAT)
        self.end_time = end_time.strftime(ICAL_DATE_FORMAT)
        self.location = location
        self.count = count
        self.stamp = datetime.now().strftime(ICAL_DATE_FORMAT)

class Schedule:
    def __init__(self):
        self.events = []

    def AddEvent(self, event):
        self.events.append(event)

    def RenderICal(self):
        template = Template(open("./ical_template").read())
        rendered = template.render(**self.__dict__)
        return rendered
