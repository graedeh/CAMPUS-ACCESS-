import json
import os
import re
import tempfile
from pathlib import Path


CARD_TYPES = {"visitor", "student", "staff"}
STATUSES = {"requested", "approved", "issued", "returned"}

REQUEST_FIELDS = {
    "id",
    "fellow_id",
    "card_type",
    "status",
    "approved_by",
}

_requests = {}
_next_id = 1


def reset_requests():
    """Reset in-memory data for testing."""
    global _next_id

    _requests.clear()
    _next_id = 1


def create_request(fellow_id, card_type):
    """Validate and create a new access-card request."""
    global _next_id

    if not isinstance(fellow_id, str):
        raise ValueError("Fellow ID must be text.")

    fellow_id = fellow_id.strip()

    if not fellow_id:
        raise ValueError("Fellow ID cannot be empty.")

    if not isinstance(card_type, str):
        raise ValueError("Card type must be text.")

    card_type = card_type.strip().lower()

    if card_type not in CARD_TYPES:
        raise ValueError(
            "Invalid card type. Use visitor, student, or staff."
        )

    # Generate a unique ID.
    while True:
        request_id = f"A{_next_id:03d}"
        _next_id += 1

        if request_id not in _requests:
            break

    request = {
        "id": request_id,
        "fellow_id": fellow_id,
        "card_type": card_type,
        "status": "requested",
        "approved_by": None,
    }

    _requests[request_id] = request

    return request.copy()


def get_request(request_id):
    """Look up a request without exposing the stored dictionary."""
    if not isinstance(request_id, str):
        raise ValueError("Request ID must be text.")

    request_id = request_id.strip()

    if not re.fullmatch(r"A[0-9]{3,}", request_id):
        raise ValueError("Malformed request ID. Example: A001.")

    request = _requests.get(request_id)

    if request is None:
        return None

    return request.copy()


def list_requests():
    """Return copies of all stored requests."""
    return [request.copy() for request in _requests.values()]


def update_request(request_id, **changes):
    """
    Safely update workflow fields.

    Engineer B must validate legal state transitions before
    using this function.
    """
    if not isinstance(request_id, str):
        raise ValueError("Request ID must be text.")

    request_id = request_id.strip()

    if not re.fullmatch(r"A[0-9]{3,}", request_id):
        raise ValueError("Malformed request ID.")

    current = _requests.get(request_id)

    if current is None:
        raise ValueError("Request does not exist.")

    allowed_changes = {"status", "approved_by"}

    if not changes:
        raise ValueError("No changes supplied.")

    if not set(changes).issubset(allowed_changes):
        raise ValueError("Unsupported request field.")

    # Validate a copy before modifying stored data.
    candidate = current.copy()
    candidate.update(changes)

    if (
        not isinstance(candidate["status"], str)
        or candidate["status"] not in STATUSES
    ):
        raise ValueError("Invalid request status.")

    approver = candidate["approved_by"]

    if approver is not None:
        if not isinstance(approver, str) or not approver.strip():
            raise ValueError("Approver cannot be empty.")

        candidate["approved_by"] = approver.strip()

    if candidate["status"] == "requested":
        if candidate["approved_by"] is not None:
            raise ValueError(
                "A requested card cannot have an approver."
            )
    elif not candidate["approved_by"]:
        raise ValueError(
            "Non-requested cards must have an approver."
        )

    _requests[request_id] = candidate

    return candidate.copy()


def _validate_loaded_request(record):
    """Validate one request loaded from JSON."""
    if not isinstance(record, dict):
        raise ValueError("Each saved request must be a dictionary.")

    if set(record.keys()) != REQUEST_FIELDS:
        raise ValueError(
            "A saved request has missing or unexpected fields."
        )

    request_id = record["id"]

    if not isinstance(request_id, str):
        raise ValueError("Saved request ID must be text.")

    if not re.fullmatch(r"A[0-9]{3,}", request_id):
        raise ValueError(f"Malformed saved ID: {request_id}")

    fellow_id = record["fellow_id"]

    if not isinstance(fellow_id, str) or not fellow_id.strip():
        raise ValueError("Saved fellow ID cannot be empty.")

    card_type = record["card_type"]

    if not isinstance(card_type, str) or card_type not in CARD_TYPES:
        raise ValueError(f"Invalid saved card type: {card_type}")

    status = record["status"]

    if not isinstance(status, str) or status not in STATUSES:
        raise ValueError(f"Invalid saved status: {status}")

    approver = record["approved_by"]

    if approver is not None:
        if not isinstance(approver, str) or not approver.strip():
            raise ValueError("Saved approver must be text or null.")

    if status == "requested" and approver is not None:
        raise ValueError(
            "Requested records must have a null approver."
        )

    if status != "requested" and not approver:
        raise ValueError(
            "Non-requested records must have an approver."
        )

    cleaned = record.copy()
    cleaned["fellow_id"] = fellow_id.strip()

    if approver is not None:
        cleaned["approved_by"] = approver.strip()

    return cleaned


def save_requests(path):
    """Save requests using a temporary file."""
    destination = Path(path)
    temporary_path = None

    try:
        destination.parent.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name

            json.dump(list_requests(), temporary_file, indent=4)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        # Replace the destination only after writing succeeds.
        os.replace(temporary_path, destination)

    except (OSError, TypeError, ValueError) as error:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass

        raise ValueError(f"Could not save requests: {error}") from error


def load_requests(path):
    """Validate a JSON file before replacing existing records."""
    global _next_id

    try:
        with open(path, "r", encoding="utf-8") as file:
            saved_data = json.load(file)

    except FileNotFoundError as error:
        raise ValueError(
            f"Saved requests file does not exist: {path}"
        ) from error

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Saved requests file contains invalid JSON: {error}"
        ) from error

    except OSError as error:
        raise ValueError(
            f"Could not read saved requests: {error}"
        ) from error

    if not isinstance(saved_data, list):
        raise ValueError("Expected a JSON list of requests.")

    # Validate everything before changing current storage.
    validated = {}

    for record in saved_data:
        cleaned = _validate_loaded_request(record)
        request_id = cleaned["id"]

        if request_id in validated:
            raise ValueError(
                f"Duplicate request ID: {request_id}"
            )

        validated[request_id] = cleaned

    _requests.clear()
    _requests.update(validated)

    highest_number = max(
        (int(request_id[1:]) for request_id in validated),
        default=0,
    )

    _next_id = highest_number + 1

    return len(_requests)