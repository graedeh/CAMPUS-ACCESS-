import unittest

from campus_access import requests as access_requests
from campus_access.workflow import (
    approve_request,
    issue_card,
    return_card,
)


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        access_requests.reset_requests()
        access_requests.create_request("F001", "student")

    def tearDown(self):
        access_requests.reset_requests()

    def test_approve_request(self):
        approve_request("A001", "Admin")

        request = access_requests.get_request("A001")

        self.assertEqual(request["status"], "approved")
        self.assertEqual(request["approved_by"], "Admin")

    def test_approval_requires_approver_name(self):
        with self.assertRaises(ValueError):
            approve_request("A001", "")

        request = access_requests.get_request("A001")
        self.assertEqual(request["status"], "requested")

    def test_unknown_request_cannot_be_approved(self):
        with self.assertRaises(ValueError):
            approve_request("A999", "Admin")

    def test_cannot_issue_unapproved_request(self):
        with self.assertRaises(ValueError):
            issue_card("A001")

    def test_issue_approved_request(self):
        approve_request("A001", "Admin")
        issue_card("A001")

        request = access_requests.get_request("A001")
        self.assertEqual(request["status"], "issued")

    def test_cannot_return_unissued_card(self):
        with self.assertRaises(ValueError):
            return_card("A001")

    def test_return_issued_card(self):
        approve_request("A001", "Admin")
        issue_card("A001")
        return_card("A001")

        request = access_requests.get_request("A001")
        self.assertEqual(request["status"], "returned")

    def test_cannot_approve_twice(self):
        approve_request("A001", "Admin")

        with self.assertRaises(ValueError):
            approve_request("A001", "Another Admin")

    def test_cannot_issue_twice(self):
        approve_request("A001", "Admin")
        issue_card("A001")

        with self.assertRaises(ValueError):
            issue_card("A001")

    def test_cannot_return_twice(self):
        approve_request("A001", "Admin")
        issue_card("A001")
        return_card("A001")

        with self.assertRaises(ValueError):
            return_card("A001")


if __name__ == "__main__":
    unittest.main()