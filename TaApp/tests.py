from django.test import TestCase
from TaApp.models import *
from TaApp.DjangoModelInterface import DjangoModelInterface
import hashlib


class DjangoModelInterfaceTests(TestCase):
    def setUp(self):
        self.di = DjangoModelInterface()

    @staticmethod
    def hashed_password(password):
        h = hashlib.new("md5")
        h.update(f"{password}".encode("ascii"))
        return h.hexdigest()

    def test_create_account(self):
        name = "account"
        password = "pass"
        role = "role"

        self.di.create_account(name, password, role)

        account = Account.objects.get(name=name)
        self.assertEqual(account.name,name)
        self.assertEqual(account.password, self.hashed_password(password))
        self.assertEqual(account.role, role)

    def test_delete_account(self):
        name = "account2delete"
        self.di.create_account("account", "pass", "role")
        self.di.create_account(name, "pass", "role")
        self.di.delete_account("account")

        self.di.delete_account(name)

        self.assertEqual(len(Account.objects.filter(name=name)), 0)

    def test_update_account(self):
        name = "account"
        new_pass = "newpass"
        new_role = "newrole"
        self.di.create_account(name, "pass", "role")
        self.di.update_account(name, new_pass, new_role)

        account = Account.objects.get(name=name)
        self.assertEqual(account.password, self.hashed_password(new_pass))
        self.assertEqual(account.role, new_role)

    def test_get_accounts(self):
        password1 = "pass"
        password2 = "pass2"

        self.di.create_account("account", password1, "role")
        self.di.create_account("account2", password2, "role2")

        accounts = self.di.get_accounts()

        self.assertEqual(accounts, [{"name":"account", "password":self.hashed_password(password1), "role":"role"},
                                    {"name":"account2","password":self.hashed_password(password2), "role":"role2"}])

    def test_get_set_logged_in(self):
        self.di.create_account("account", "pass", "TA")
        self.di.set_logged_in("account")

        response = self.di.get_logged_in()

        self.assertEqual(response, "account")

    def test_set_logged_in_set_logged_out(self):
        self.di.create_account("account", "pass", "TA")
        self.di.set_logged_in("account")

        response = self.di.get_logged_in()
        self.assertEqual(response, "account")

        self.di.set_logged_out()

        response = self.di.get_logged_in()
        self.assertEqual(response, "")

    def test_create_course_get_courses(self):
        number = "361"
        name = "CompSci361"
        self.di.create_course(number, name)

        self.assertIsNotNone(Course.objects.filter(number=number, name=name).first())

    def test_create_set_course_instructor(self):
        number = "361"
        instructor_name = "jayson"

        self.di.create_course(number, "CompSci")
        self.di.create_account(instructor_name, "pass", "instructor")
        self.di.set_course_instructor(number, instructor_name)

        course = Course.objects.get(number=number)
        self.assertEqual(course.instructor.first().name, instructor_name)

    def test_create_lab_get_labs(self):
        course_number = "361"
        lab_number = "801"
        self.di.create_course(course_number, "courseName")
        self.di.create_lab(course_number, lab_number)

        lab = Course.objects.get(number=course_number, labs__number=lab_number)

        self.assertIsNotNone(lab)

    def test_assign_lab(self):
        course_number = "361"
        lab_number = "801"
        ta_name = "apoorv"
        self.di.create_course(course_number, "courseName")
        self.di.create_lab(course_number, lab_number)
        self.di.create_account(ta_name, "pass", "TA")

        self.di.set_lab_assignment(course_number, lab_number, ta_name)
        lab = Course.objects.get(number=course_number).labs.get(number=lab_number)

        self.assertEqual(lab.ta.name, ta_name)

    def test_get_user_exists(self):
        self.di.create_account("root", "root", "administrator")
        self.assertIsNotNone(self.di.get_user("root"))

    def test_get_user_doesnt_exist(self):
        self.assertIsNone(self.di.get_user("nonexistent"))

    # Course Test cases
    def test_get_course_exists(self):
        self.di.create_course("123", "test_course")
        self.assertIsNotNone(self.di.course_exists("123"))

    def test_get_course_doesnt_exist(self):
        self.assertIsNotNone(self.di.course_exists("000"))

    def test_get_course_assigned(self):
        self.di.create_account("teacher", "root", "instructor")
        self.di.create_course("123", "test_course")
        self.di.set_course_instructor("123", "teacher")
        self.assertTrue(self.di.is_course_assigned("123"))

    def test_get_course_not_assigned(self):
        self.di.create_course("000", "test_course")
        self.assertFalse(self.di.is_course_assigned("000"))

    def test_get_lab_exists(self):
        self.di.create_course("123", "test_course")
        self.di.create_lab("123", "001")
        self.assertTrue(self.di.lab_exists("123", "001"))

    def test_get_lab_doesnt_exist(self):
        self.di.create_course("123", "test_course")
        self.assertFalse(self.di.lab_exists("123", "1231231"))

    def test_get_lab_assigned(self):
        self.di.create_account("ta", "pass", "TA")
        self.di.create_course("123", "test_course")
        self.di.create_lab("123", "001")
        self.di.set_lab_assignment("123", "001", "ta")
        self.assertTrue(self.di.is_lab_assigned("123", "001"))

    def test_get_lab_not_assigned(self):
        self.di.create_course("234", "test_course2")
        self.di.create_lab("234", "000")
        self.assertFalse(self.di.is_lab_assigned("234", "000"))

    def test_valid_role_admin(self):
        self.assertTrue(self.di.is_valid_role("administrator"))

    def test_valid_role_supervisor(self):
        self.assertTrue(self.di.is_valid_role("supervisor"))

    def test_valid_role_instructor(self):
        self.assertTrue(self.di.is_valid_role("instructor"))

    def test_valid_role_TA(self):
        self.assertTrue(self.di.is_valid_role("TA"))

    def test_invalid_role(self):
        self.assertFalse(self.di.is_valid_role("invalid"))

