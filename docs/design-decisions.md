# Campus Access — Design Decisions

## 1. Purpose

This document records the technical decisions guiding the
development of Campus Access.

It explains how the application is organized, how access-card
requests are represented, how workflow rules are enforced, and
how request records are stored and tested.

The document provides a shared reference for all team members.

## 2. Application Type

### Decision

Campus Access will be implemented as a Python command-line
application.

### Reason

A command-line application is suitable for the required operations
and allows the team to focus on request management, validation,
workflow rules, and data persistence without introducing an
unnecessary web framework.

The application will use Python's standard library.

## 3. Modular Project Structure

### Decision

The application will separate request management, workflow logic,
data persistence, and user interaction.

### Implementation

- `campus_access/requests.py` handles request creation, identifiers,
  and validation.
- `campus_access/workflow.py` handles approval, issuance, returns,
  and status transitions.
- `storage.py` handles JSON data persistence.
- `main.py` provides the command-line interface and connects the
  application components.

### Reason

Separating responsibilities makes the code easier to understand,
test, maintain, and debug.

It also allows team members to work on separate components while
reducing unnecessary conflicts.

## 4. Request Data Structure

### Decision

Each access-card request will be represented by a Python dictionary.

### Required Fields

Each request will contain:

- `id`
- `fellow_id`
- `card_type`
- `status`
- `approved_by`

### Reason

A dictionary provides a straightforward way to represent a record
using named fields.

The structure is also easy to serialize to JSON and restore when
the application starts.

The field names must remain consistent across the request,
workflow, storage, and testing modules.

## 5. Request Identifiers

### Decision

Request identifiers will follow the required format, beginning
with `A001` and continuing with unique identifiers such as `A002`
and `A003`.

Identifiers must remain unique across program restarts.

### Reason

Unique identifiers allow each request to be located independently
of the requester's identity or the request's position in a list.

### Implementation Considerations

The application must determine the next available identifier
without reusing an identifier already assigned to a saved request.

Identifiers must be validated against the required format.

## 6. Supported Card Types

### Decision

The supported card types are:

- `visitor`
- `student`
- `staff`

### Reason

Restricting card types to the supported values prevents inconsistent
records and makes validation predictable.

Unsupported card types must be rejected before a request is created.

## 7. Request Status Workflow

### Decision

Requests must follow this sequence:

    requested -> approved -> issued -> returned

### Rules

1. Every new request begins with the status `requested`.
2. A request must be approved before its card can be issued.
3. Approval must identify the approver.
4. Only an approved request can be issued.
5. Only an issued card can be returned.
6. A returned request cannot be issued again under the initial workflow.
7. Unsupported and repeated transitions must be rejected.

### Reason

A controlled workflow prevents cards from being issued without
approval and keeps request records consistent.

## 8. Validation Before Modification

### Decision

An operation must be validated before the affected request is
modified.

### Reason

If a request is modified before validation finishes, a failed
operation could leave it in an inconsistent state.

Validation must therefore happen before the status or other
request fields are changed.

### Example

If a request has the status `requested`, an attempt to issue its
card must be rejected.

The request must remain unchanged after the failed operation.

An approval attempt with a blank approver identifier must also
be rejected without modifying the request.

## 9. Workflow Functions

### Decision

Workflow operations will be implemented as separate functions.

The required Engineer B interfaces are:

- `approve_request(request_id, approved_by)`
- `issue_card(request_id)`
- `return_card(request_id)`
- `run_menu()`

### Reason

Functions with clear responsibilities are easier to understand,
test, and maintain than a single large function.

The workflow functions must use the shared request and storage
interfaces agreed upon by the team.

The CLI must call the workflow functions instead of duplicating
the workflow rules.

## 10. JSON Data Persistence

### Decision

Request records will be stored using JSON.

### Reason

JSON is human-readable and supported by Python's standard library.
It provides a simple way to preserve request data between program
runs.

### Storage Responsibilities

The storage component must:

- Save request records.
- Load saved request records.
- Validate loaded records.
- Preserve records between program runs.
- Report malformed or invalid saved data clearly.

## 11. Safe Loading and Saving

### Decision

The application must not silently overwrite existing saved data
when loading fails because the data is malformed or invalid.

### Reason

Replacing an unreadable data file with an empty collection could
cause existing records to be lost.

### Expected Behavior

If the saved JSON cannot be loaded and validated, the application
must report the problem clearly.

It must not continue as if the file were empty and then overwrite
the existing records.

The storage component must validate the expected request fields
and supported values before accepting saved records.

## 12. Error Handling

### Decision

Invalid inputs and unsupported operations must produce clear
error messages.

### Examples

The application must handle:

- Unknown request identifiers.
- Blank fellow identifiers.
- Unsupported card types.
- Invalid request identifier formats.
- Duplicate request identifiers.
- Blank approver identifiers.
- Attempts to issue unapproved requests.
- Attempts to return cards that have not been issued.
- Attempts to issue returned cards.
- Invalid menu choices.
- Malformed or invalid JSON data.

### Reason

Clear error messages help users understand why an operation failed.

Failed operations must not partially modify request records.

## 13. Command-Line Interface

### Decision

The CLI will provide a menu for the required operations:

- Create an access-card request.
- View requests.
- Approve a request.
- Issue an approved card.
- Record a card return.
- Save and load request data.
- Exit the application.

### Reason

A menu-driven interface allows users to interact with the
application without needing to call Python functions directly.

Invalid menu choices should produce a clear message and allow
the user to try again.

## 14. Testing Strategy

### Decision

Automated tests will use Python's `unittest` module.

### Test Responsibilities

`tests/test_requests.py` will test request creation, identifiers,
and validation.

`tests/test_workflow.py` will test approval, issuance, returns,
and invalid status transitions.

Storage behavior must also be tested to verify that data can be
saved and loaded safely.

### Important Test Cases

Tests should verify that:

- Valid requests can be created.
- Invalid request data is rejected.
- Request identifiers are unique.
- Requests can be approved with valid approver information.
- Blank approver information is rejected.
- Unapproved requests cannot be issued.
- Approved requests can be issued.
- Unissued cards cannot be returned.
- Issued cards can be returned.
- Returned cards cannot be issued again.
- Failed operations leave requests unchanged.
- Saved data can be loaded after restarting the program.
- Invalid JSON does not silently destroy existing records.

### Reason

Automated tests provide repeatable evidence that the application
follows its requirements and help prevent regressions.

## 15. Team Responsibilities

### Engineer A

Responsible for the request-related implementation and storage
components assigned by the team.

### Engineer B

Responsible for workflow operations and CLI interaction, including:

- `approve_request(request_id, approved_by)`
- `issue_card(request_id)`
- `return_card(request_id)`
- `run_menu()`

Engineer B is also responsible for workflow tests and coordinating
with Engineer A to ensure that both parts integrate correctly.

### Collaboration Decision

Both engineers must agree on shared function interfaces, request
field names, and error-handling expectations.

Changes should be developed on the appropriate feature branches
and submitted through pull requests for review.

Feature work should not be pushed directly to the main branch.

## 16. Code Readability and Maintainability

### Decision

The project will use straightforward and readable Python code.

### Principles

- Use meaningful function and variable names.
- Keep functions focused on one responsibility.
- Avoid unnecessary complexity.
- Validate inputs explicitly.
- Keep workflow rules in the workflow module.
- Keep JSON operations in the storage module.
- Write tests for important behavior.
- Document significant technical decisions.

### Reason

Readable code is easier for teammates to review, understand,
debug, and maintain.

The goal is to satisfy the project requirements without introducing
unnecessary abstractions.

## 17. Current Project Status

The initial project structure has been created and pushed to GitHub.

The decisions documented here describe the intended design.
They do not mean that all application features have already been
implemented or tested.

A feature will be considered complete only after its implementation
satisfies the requirements and its relevant tests pass.