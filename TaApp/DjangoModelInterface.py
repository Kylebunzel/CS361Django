from TaCLI.DataInterface import DataInterface
import TaCLI.User
from TaApp.models import *
import hashlib


class DjangoModelInterface(DataInterface):

    def __init__(self):
        pass

    def create_account(self, account_name, password, role):
        h = hashlib.new("md5")
        h.update(f"{password}".encode("ascii"))
        hashed_password = h.hexdigest()
        Account.objects.create(name=account_name, password=hashed_password, role=role)

    def delete_account(self, account_name):
        Account.objects.filter(name=account_name).delete()

    def update_account(self, account_name, password, role):
        pass

    def get_accounts(self):
        accounts = []
        account_objs = Account.objects.all()
        for acct in account_objs:
            accounts.append({"name": acct.name, "password": acct.password, "role": acct.role})
        return accounts

    def get_logged_in(self):
        logged_in = LoggedIn.objects.first()
        if logged_in is None:
            return ""
        return logged_in.account.name

    def set_logged_in(self, account_name):
        acct = Account.objects.filter(name=account_name).first()
        LoggedIn.objects.create(account=acct)

    def set_logged_out(self):
        LoggedIn.objects.all().delete()

    def create_course(self, course_number, course_name, ):
        Course.objects.create(number=course_number, name=course_name)

    def get_courses(self):
        courses = []
        for c in Course.objects.all():
            courses.append({"course_number": str(c.number), "course_name": c.name})
        return courses

    def set_course_assignment(self, course_number, instructor_name):
        instructor = Account.objects.filter(name=instructor_name).first()
        course = Course.objects.filter(number=course_number)
        course.instructor.add(instructor)

    def get_course_assignments(self):
        return []

    def create_lab(self, course_number, lab_number):
        course = Course.objects.filter(number=course_number).first()
        lab = Lab.objects.create(number=lab_number)
        course.labs.add(lab)

    def get_labs(self):
        labs = []
        for lab in Lab.objects.all():
            course = Course.objects.filter(labs__id=lab.id).first()
            labs.append({"course_number": course.number, "lab_number": lab.number})
        return labs

    def set_lab_assignment(self, course_number, lab_number, ta_name):
        pass

    def get_lab_assignments(self):
        return []

    def get_user(self, user_name):
        userobj = Account.objects.filter(name=user_name).first()
        if userobj is None:
            return None
        return TaCLI.User.User(userobj.name, userobj.role, userobj.password)

    def course_exists(self, course_number):
        course = Course.objects.filter(number=course_number).first()
        return course is not None

    def is_course_assigned(self, course_number):
        course = Course.objects.filter(number=course_number).first()
        return course is not None and course.instructor is not None

    def lab_exists(self, course_number, lab_number):
        lab = Lab.objects.filter(number=lab_number, course__number=course_number).first()
        return lab is not None

    def is_lab_assigned(self, course_number, lab_number):
        lab = Lab.objects.filter(number=lab_number, course__number=course_number).first()
        return lab is not None and lab.ta is not None

    def is_valid_role(self, role):
        return role in ["administrator", "supervisor", "instructor", "TA"]
