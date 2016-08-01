import requests
import getpass
from bs4 import BeautifulSoup

import constants
import utils
from schedule import Schedule

class UWindsorClient:
    # Initializes the request session that will be used to persist login state
    # between requests.
    def __init__(self):
        self.session_ = requests.Session()

    # Prompts the user for login information and makes the authentication
    # request.
    def PromptLogin(self):
        login_page = self.session_.get("https://my.uwindsor.ca/").text
        login_form = BeautifulSoup(login_page, "html.parser").form
        login_url = login_form["action"]
        input_data = utils.ExtractFormData(login_form)
        input_data[constants.USERNAME_INPUT_NAME] = \
                raw_input("UWindsor ID: ")
        input_data[constants.PASSWORD_INPUT_NAME] = \
                getpass.getpass("Password: ")
        self.session_.post(login_url, data = input_data)
        # TODO(quinny) Check for incorrect login.

    def GetCurrentSchedule(self):
        schedule_page_html = self.session_.get(\
                "https://my.uwindsor.ca/web/uw/my-timetable").text
        return utils.ParseCoursesFromSchedulePage(schedule_page_html)

    def GenerateICalFile(self):
        raw_schedule = self.GetCurrentSchedule()
        schedule = Schedule()
        for class_object in raw_schedule:
            description_page = self.session_.get(class_object["url"]).text
            course_name = utils.GetCourseName(description_page)
            location = utils.GetCourseLocation(description_page)
            schedule.AddEvent(utils.ClassToWeeklyEvent(class_object, course_name,
                location))

        file_contents = schedule.RenderICal()
        with open("uwindsor_schedule.ics", "w") as f:
            f.write(file_contents)
        print "schedule written to ./uwindsor_schedule.ics"
