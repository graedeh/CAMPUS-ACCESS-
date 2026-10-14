import json
import os
import re
import tempfile
from pathlib import Path


# Allowed access-card types
VALID_CARD_TYPES = {"visitor", "student", "staff"}

# Allowed request statuses
VALID_STATUSES = {"requested", "approved", "issued", "returned"}

# Every request must contain these fields
REQUIRED_FIELDS = {
    "id",
    "fellow_id",
    "card_type",
    "status",
    "approved_by",
}


def validate_requests(requests):
    """Validate all requests before saving or accepting loaded data."""

    if not isinstance(requests, dict):
        raise ValueError("Requests data must be a dictionary.")

    seen_ids = set()

    for request_id, request in requests.items():

        # Check that each request is a dictionary
        if not isinstance(request, dict):
            raise ValueError(
                f"Request {request_id!r} must be a dictionary."
            )

        # Check that all required fields exist
        if set(request.keys()) != REQUIRED_FIELDS:
            raise ValueError(
                f"Request {request_id!r} has missing or unexpected fields."
            )

        # Validate request ID using ASCII digits only
        if not isinstance(request_id, str) or not re.fullmatch(
            r"A[0-9]{3,}", request_id
        ):
            raise ValueError(f"Invalid request ID: {request_id!r}")

        # The ID in the record must match its dictionary key
        if request["id"] != request_id:
            raise ValueError(
                f"Request ID does not match its key: {request_id}"
            )

        # Check for duplicate IDs
        if request_id in seen_ids:
            raise ValueError(f"Duplicate request ID: {request_id}")

        seen_ids.add(request_id)

        # Validate fellow ID
        fellow_id = request["fellow_id"]

        if not isinstance(fellow_id, str) or not fellow_id.strip():
            raise ValueError(
                f"Request {request_id} has an invalid fellow ID."
            )

        # Validate card type
        if (
            not isinstance(request["card_type"], str)
            or request["card_type"] not in VALID_CARD_TYPES
        ):
            raise ValueError(
                f"Request {request_id} has an invalid card type."
            )

        # Validate status
        if request["status"] not in VALID_STATUSES:
            raise ValueError(
                f"Request {request_id} has an invalid status."
            )

        # Validate approver
        approved_by = request["approved_by"]

        if approved_by is not None and (
            not isinstance(approved_by, str) or not approved_by.strip()
        ):
            raise ValueError(
                f"Request {request_id} has an invalid approver."
            )

        # Only requested records may have no approver.
        # Approved, issued and returned records must have one.
        if request["status"] == "requested" and approved_by is not None:
            raise ValueError(
                f"Requested record {request_id} cannot have an approver."
            )

        if request["status"] != "requested" and approved_by is None:
            raise ValueError(
                f"Record {request_id} must have an approver."
            )


def save_requests(requests, path):
    """
    Save requests to JSON.

    Validate the data first and replace the destination only after
    the complete temporary file has been written successfully.
    """

    validate_requests(requests)

    destination = Path(path)

    # The destination directory must already exist.
    if not destination.parent.is_dir():
        raise FileNotFoundError(
            f"Directory does not exist: {destination.parent}"
        )

    temporary_path = None

    try:
        # Create a temporary file in the same directory.
        # This helps make the final replacement atomic.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:

            temporary_path = Path(temporary_file.name)

            json.dump(
                requests,
                temporary_file,
                indent=4,
                ensure_ascii=False,
            )

            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        # Replace the destination only after writing succeeds.
        os.replace(temporary_path, destination)

    finally:
        # Remove an unfinished temporary file if one remains.
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def load_requests(path):
    """
    Load and validate requests from JSON.

    Return the loaded dictionary.
    Never treat a missing or invalid file as an empty database.
    """

    source = Path(path)

    # A missing file must be reported, not silently replaced.
    if not source.is_file():
        raise FileNotFoundError(
            f"Request data file not found: {source}"
        )

    try:
        with source.open("r", encoding="utf-8") as file:
            requests = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid JSON in {source}: {error}"
        ) from error

    except UnicodeDecodeError as error:
        raise ValueError(
            f"The file {source} is not valid UTF-8 text."
        ) from error

    # Validate loaded data before returning it.
    validate_requests(requests)

    return requests