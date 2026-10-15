import re

from campus_access.storage import (
    save_requests as save_to_storage,
    load_requests as load_from_storage,
)


CARD_TYPES = {"visitor", "student", "staff"}
STATUSES = {"requested", "approved", "issued", "returned"}

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

    # Generate a unique request ID.
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
    """Find a request by its ID."""
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
    """Return copies of all requests."""
    return [request.copy() for request in _requests.values()]


def update_request(request_id, **changes):
    """Validate and update an existing request."""
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

    # Validate a copy before changing the stored request.
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


def save_requests(path):
    """Save requests through the central storage module."""
    save_to_storage(_requests, path)


def load_requests(path):
    """Load requests through the central storage module."""
    global _next_id

    # Load and validate the complete file before changing memory.
    loaded_requests = load_from_storage(path)

    _requests.clear()
    _requests.update(
        {
            request_id: request.copy()
            for request_id, request in loaded_requests.items()
        }
    )

    # Continue numbering after the highest ID loaded.
    highest_number = max(
        (int(request_id[1:]) for request_id in _requests),
        default=0,
    )

    _next_id = highest_number + 1

    return len(_requests)