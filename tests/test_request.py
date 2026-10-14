import json
import tempfile
import unittest
from pathlib import Path

import requests as access_requests


class TestAccessRequests(unittest.TestCase):

    def setUp(self):
        # Reset request data before each test.
        access_requests.reset_requests()

        # Create a temporary folder for test files.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "requests.json"

    def tearDown(self):
        # Clean up temporary files and reset request data.
        self.temp_dir.cleanup()
        access_requests.reset_requests()

    def test_create_request(self):
        # Test that a request is created with the correct details.
        request = access_requests.create_request("F001", "visitor")

        self.assertEqual(request["id"], "A001")
        self.assertEqual(request["fellow_id"], "F001")
        self.assertEqual(request["card_type"], "visitor")
        self.assertEqual(request["status"], "requested")
        self.assertIsNone(request["approved_by"])

    def test_reject_blank_fellow_id(self):
        # Reject requests with an empty fellow ID.
        with self.assertRaises(ValueError):
            access_requests.create_request("   ", "visitor")

        self.assertEqual(access_requests.list_requests(), [])

    def test_reject_invalid_card_type(self):
        # Reject card types that are not supported.
        with self.assertRaises(ValueError):
            access_requests.create_request("F001", "guest")

        self.assertEqual(access_requests.list_requests(), [])

    def test_reject_wrong_input_type(self):
        # Reject a fellow ID that is not a string.
        with self.assertRaises(ValueError):
            access_requests.create_request(123, "visitor")

        self.assertEqual(access_requests.list_requests(), [])

    def test_unique_ids(self):
        # Ensure each new request receives a unique ID.
        first = access_requests.create_request("F001", "visitor")
        second = access_requests.create_request("F002", "student")

        self.assertEqual(first["id"], "A001")
        self.assertEqual(second["id"], "A002")

    def test_malformed_id(self):
        # Reject request IDs with an invalid format.
        with self.assertRaises(ValueError):
            access_requests.get_request("AABC")

    def test_unknown_id(self):
        # Return None when a request ID does not exist.
        self.assertIsNone(access_requests.get_request("A999"))

    def test_lookup_returns_copy(self):
        # Ensure changing a returned record does not change stored data.
        access_requests.create_request("F001", "visitor")

        result = access_requests.get_request("A001")
        result["status"] = "returned"

        stored = access_requests.get_request("A001")
        self.assertEqual(stored["status"], "requested")

    def test_save_and_reload(self):
        # Verify requests can be saved and restored from JSON.
        access_requests.create_request("F001", "visitor")
        access_requests.save_requests(self.file_path)

        # Clear memory and reload the saved request.
        access_requests.reset_requests()
        count = access_requests.load_requests(self.file_path)

        self.assertEqual(count, 1)
        self.assertEqual(
            access_requests.get_request("A001")["fellow_id"],
            "F001",
        )

        # Ensure IDs continue correctly after reloading.
        second = access_requests.create_request("F002", "student")
        self.assertEqual(second["id"], "A002")

    def test_corrupted_json_preserves_existing_data(self):
        # Reject corrupted JSON without deleting existing requests.
        access_requests.create_request("F001", "visitor")

        self.file_path.write_text(
            '{"invalid":',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            access_requests.load_requests(self.file_path)

        self.assertIsNotNone(access_requests.get_request("A001"))

    def test_duplicate_ids_in_json_are_rejected(self):
        # Reject JSON containing duplicate request IDs.
        record = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "requested",
            "approved_by": None,
        }

        self.file_path.write_text(
            json.dumps([record, record]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            access_requests.load_requests(self.file_path)

        self.assertEqual(access_requests.list_requests(), [])

    def test_missing_fields_are_rejected(self):
        # Reject records that do not contain all required fields.
        self.file_path.write_text(
            json.dumps([{"id": "A001"}]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            access_requests.load_requests(self.file_path)

    def test_invalid_status_in_json_is_rejected(self):
        # Reject records containing unsupported statuses.
        record = {
            "id": "A001",
            "fellow_id": "F001",
            "card_type": "visitor",
            "status": "cancelled",
            "approved_by": None,
        }

        self.file_path.write_text(
            json.dumps([record]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            access_requests.load_requests(self.file_path)

    def test_failed_update_preserves_record(self):
        # Ensure a failed update does not change the original record.
        access_requests.create_request("F001", "visitor")
        original = access_requests.get_request("A001")

        with self.assertRaises(ValueError):
            access_requests.update_request(
                "A001",
                status="returned",
                approved_by=None,
            )

        self.assertEqual(
            access_requests.get_request("A001"),
            original,
        )


if __name__ == "__main__":
    # Run all tests when this file is executed directly.
    unittest.main()