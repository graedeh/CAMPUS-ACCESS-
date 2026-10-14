import unittest

from campus_access.workflow import (
    approve_request,
    issue_card,
    return_card,
)


class TestWorkflow(unittest.TestCase):

    def setUp(self):
        """Create a fresh request for each test."""

        self.request = {
            "id": "REQ-001",
            "requester": "Grace",
            "purpose": "Library access",
            "status": "requested",
            "approved_by": None,
        }

    def test_approve_request(self):
        approve_request(self.request, "Admin")

        self.assertEqual(self.request["status"], "approved")
        self.assertEqual(self.request["approved_by"], "Admin")

    def test_approval_requires_approver_name(self):
        with self.assertRaises(ValueError):
            approve_request(self.request, "")

    def test_cannot_issue_unapproved_request(self):
        with self.assertRaises(ValueError):
            issue_card(self.request)

    def test_issue_approved_request(self):
        approve_request(self.request, "Admin")

        issue_card(self.request)

        self.assertEqual(self.request["status"], "issued")

    def test_cannot_return_unissued_card(self):
        with self.assertRaises(ValueError):
            return_card(self.request)

    def test_return_issued_card(self):
        approve_request(self.request, "Admin")
        issue_card(self.request)

        return_card(self.request)

        self.assertEqual(self.request["status"], "returned")


if __name__ == "__main__":
    unittest.main()