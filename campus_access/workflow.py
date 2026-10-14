def approve_request(request, approver_name):
    """Approve an access-card request."""

    if request["status"] != "requested":
        raise ValueError("Only requested cards can be approved.")

    if not approver_name.strip():
        raise ValueError("Approver name is required.")

    request["status"] = "approved"
    request["approved_by"] = approver_name.strip()

    return request


def issue_card(request):
    """Issue an approved access card."""

    if request["status"] != "approved":
        raise ValueError("Only approved cards can be issued.")

    request["status"] = "issued"

    return request


def return_card(request):
    """Record the return of an issued access card."""

    if request["status"] != "issued":
        raise ValueError("Only issued cards can be returned.")

    request["status"] = "returned"

    return request