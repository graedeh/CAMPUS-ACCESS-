from campus_access.requests import get_request, update_request


def approve_request(request_id, approver_name):
    """Approve an existing access-card request."""

    request = get_request(request_id)

    if request is None:
        raise ValueError("Request not found.")

    if request["status"] != "requested":
        raise ValueError("Only requested cards can be approved.")

    if not isinstance(approver_name, str) or not approver_name.strip():
        raise ValueError("Approver name is required.")

    return update_request(
        request_id,
        status="approved",
        approved_by=approver_name.strip(),
    )


def issue_card(request_id):
    """Issue an approved access card."""

    request = get_request(request_id)

    if request is None:
        raise ValueError("Request not found.")

    if request["status"] != "approved":
        raise ValueError("Only approved cards can be issued.")

    return update_request(
        request_id,
        status="issued",
    )


def return_card(request_id):
    """Record the return of an issued access card."""

    request = get_request(request_id)

    if request is None:
        raise ValueError("Request not found.")

    if request["status"] != "issued":
        raise ValueError("Only issued cards can be returned.")

    return update_request(
        request_id,
        status="returned",
    )