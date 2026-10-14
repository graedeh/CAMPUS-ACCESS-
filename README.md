# Campus Access

## Project Overview

Campus Access is a Python command-line application for managing
campus access-card requests.

The application allows users to create access-card requests, view
requests, approve requests, issue approved access cards, and record
returned cards.

It follows a controlled workflow to ensure that an access card
cannot be issued before its request has been approved.

The application uses JSON to store request records so that data
can be preserved between program runs.

## Problem Statement

Managing campus access-card requests requires a reliable way to
record requests, track their status, and ensure that the required
approval process is followed.

Without a structured system, requests may be issued without
approval, records may become inconsistent, and it may be difficult
to determine the current status of a request.

Campus Access provides a simple and organized process for managing
access-card requests and tracking their progress.

## Project Objectives

The objectives of Campus Access are to:

- Create access-card requests.
- Assign each request a unique identifier.
- Validate request information.
- Display existing requests and their statuses.
- Approve requests and record the approver.
- Issue access cards only after approval.
- Record the return of issued access cards.
- Reject invalid workflow transitions.
- Save and load request records using JSON.
- Handle invalid input and corrupted storage data safely.
- Test the application's behavior using automated tests.

## Technologies Used

- Python 3
- JSON for data persistence
- `unittest` for automated testing
- Git for version control
- GitHub for collaboration

The application is designed to use Python's standard library.

## Access-Card Request Structure

Each access-card request contains the following fields:

| Field | Description |
|---|---|
| `id` | Unique request identifier |
| `fellow_id` | Identifier of the fellow requesting the card |
| `card_type` | Type of access card requested |
| `status` | Current status of the request |
| `approved_by` | Identifier or name of the person who approved the request |

Example request:

    {
        "id": "A001",
        "fellow_id": "F001",
        "card_type": "student",
        "status": "requested",
        "approved_by": null
    }

The supported card types are:

- `visitor`
- `student`
- `staff`

Request identifiers must follow the required format, beginning
with `A001` and continuing with unique identifiers such as `A002`
and `A003`.

Identifiers must remain unique across program restarts.

## Request Workflow

Access-card requests follow this sequence:

    requested -> approved -> issued -> returned

### Requested

The request has been created and is awaiting approval.

### Approved

The request has been approved by an identified approver.

### Issued

The access card has been issued after approval.

### Returned

The issued access card has been returned.

The application must reject invalid transitions. For example,
a request cannot move directly from `requested` to `issued`.

A returned request cannot be issued again under the initial workflow.

Failed operations must leave the affected request unchanged.

## Main Features

The application is intended to support the following operations:

1. Create an access-card request.
2. View an individual request or list existing requests.
3. Approve a request.
4. Issue an approved access card.
5. Record the return of an issued access card.
6. Save request records.
7. Load previously saved records.
8. Exit the application.

## Validation and Error Handling

The application must reject invalid input and unsupported operations.

Examples include:

- Missing or blank required information.
- Invalid request identifiers.
- Duplicate request identifiers.
- Unsupported card types.
- Unknown request IDs.
- Blank approver information.
- Attempts to issue an unapproved request.
- Attempts to return a card that has not been issued.
- Attempts to issue a returned card.
- Invalid or corrupted saved JSON data.

The application must report errors clearly and avoid changing
request data when an operation fails.

## Data Persistence

Campus Access uses JSON for data persistence.

The application must save request records and load them when
it starts.

The storage component must validate loaded data and handle
missing or corrupted files safely.

If existing JSON data is malformed or invalid, the application
must not silently replace it with an empty collection.

## Project Structure

    CAMPUS-ACCESS-/
    ├── campus_access/
    │   ├── __init__.py
    │   ├── requests.py
    │   └── workflow.py
    ├── tests/
    │   ├── __init__.py
    │   ├── test_requests.py
    │   └── test_workflow.py
    ├── docs/
    │   ├── ai-learning-log.md
    │   └── design-decisions.md
    ├── main.py
    ├── storage.py
    ├── README.md
    └── .gitignore

### File Responsibilities

- `main.py`: Application entry point and command-line interface.
- `storage.py`: Saves and loads request records using JSON.
- `campus_access/requests.py`: Handles request creation, identifiers, and validation.
- `campus_access/workflow.py`: Handles approvals, card issuance, returns, and status transitions.
- `tests/test_requests.py`: Tests request creation and validation.
- `tests/test_workflow.py`: Tests workflow behavior.
- `docs/ai-learning-log.md`: Records relevant AI assistance and learning activities.
- `docs/design-decisions.md`: Documents technical decisions.
- `README.md`: Explains the project and how to use it.
- `.gitignore`: Specifies files Git should ignore.

## Requirements

- Python 3
- A terminal or command-line environment
- Git for version control

No external Python packages are required by the project specification.

## How to Run the Application

Clone the repository:

    git clone https://github.com/graedeh/CAMPUS-ACCESS-.git

Enter the project directory:

    cd CAMPUS-ACCESS-

Run the application:

    python3 main.py

The CLI will provide access to the application's supported operations
once the implementation is complete.

## How to Run the Tests

From the project root, run:

    python3 -m unittest discover -s tests -v

This command discovers and runs the automated tests in the `tests`
directory.

The tests should cover request creation, validation, workflow
transitions, and other required behavior.

## Team Responsibilities

### Engineer A

Responsible for the request-related implementation and storage
components assigned by the team.

### Engineer B

Responsible for the access-request workflow and command-line
interface, including:

- `approve_request(request_id, approved_by)`
- `issue_card(request_id)`
- `return_card(request_id)`
- `run_menu()`

Engineer B also develops workflow tests and coordinates with
Engineer A to ensure that the modules work together correctly.

## Testing and Completion

The project structure has been created and pushed to GitHub.

The application is considered complete only when the required
features have been implemented, the workflow rules are enforced,
data is stored safely, and the relevant automated tests pass.

## Documentation

Additional project documentation is available in:

- `docs/design-decisions.md`
- `docs/ai-learning-log.md`