from slimit          import ast
from slimit.parser   import Parser
from slimit.visitors import nodevisitor
from bs4             import BeautifulSoup
from datetime        import datetime, timedelta

from schedule import WeeklyEvent

# A simple decorator which creates an in-memory cache over a given function.
def MemoryCache(f):
    cache = {}
    def wrap(*args):
        if args in cache:
            return cache[args]
        ret = f(*args)
        cache[args] = ret
        return ret
    return wrap

# Given a beautiful soup form element, return a dictionary of name => value
# for all input tags within the form.
def ExtractFormData(form):
    return {e['name']: e.get('value', '') \
            for e in form.find_all("input", {'name': True})}

# Given a javascript object AST node, parse out all assignments from its
# children.
# TODO(quinny) better explain and provide example.
def ParseAssignments(object_node):
    def RemoveSingleQuotes(string):
        return string.replace("'", "")
    return {RemoveSingleQuotes(getattr(child.left, 'value', '')):\
            RemoveSingleQuotes(getattr(child.right, 'value', ''))\
            for child in object_node.children() if isinstance(child, ast.Assign)}

# TODO(quinny) provide example and document.
def ParseObjectAssignments(js_code):
    parser = Parser()
    tree = parser.parse(js_code)
    return [ParseAssignments(node) \
            for node in nodevisitor.visit(tree) if isinstance(node, ast.Object)]

# TODO(quinny) document
def ParseCoursesFromSchedulePage(schedule_page_html):
    def IsClassObject(obj):
        return "title" in obj and "start" in obj and "end" in obj \
                and "url" in obj

    soup = BeautifulSoup(schedule_page_html, "html.parser")
    # TODO(quinny) This is probably flakey, fix it.
    js_code = soup.find_all("script")[15].string
    all_objects = ParseObjectAssignments(js_code)
    return filter(IsClassObject, all_objects)

# Given a course description page, return the name of a course.  Cached for
# repeated courses.
@MemoryCache
def GetCourseName(course_description_html):
    soup = BeautifulSoup(course_description_html, "html.parser")
    title = soup.h1.string
    return title[0:title.find(" Section")]

@MemoryCache
def GetCourseLocation(course_description_html):
    soup = BeautifulSoup(course_description_html, "html.parser")
    body = soup.p.div.get_text()
    return body[body.find("in ") + 3:-1]

def FirstWeekdayAfter(after, day):
    while after.weekday() != day:
        after += timedelta(1)
    return after

def ToDateTime(class_time):
    return datetime.strptime(class_time, "%Y-%m-%d %H:%M")

def ClassToWeeklyEvent(class_object, course_name, location):
    start_datetime = ToDateTime(class_object["start"])
    end_datetime = ToDateTime(class_object["end"])
    september_first = datetime(datetime.now().year, 9, 1)

    first_event_start = FirstWeekdayAfter(september_first,
            start_datetime.weekday()).replace(hour = start_datetime.hour,
            minute = start_datetime.minute)

    first_event_end = first_event_start.replace(hour = end_datetime.hour,
            minute = end_datetime.minute)

    # 1 count for testing, should change to 14ish for a semester.
    return WeeklyEvent(course_name, first_event_start, first_event_end, location, 1)
