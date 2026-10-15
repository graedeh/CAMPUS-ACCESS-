from pathlib import Path

from campus_access.requests import (
    create_request,
    list_requests,
    get_request,
    save_requests,
    load_requests,
)
from campus_access.workflow import (
    approve_request,
    issue_card,
    return_card,
)


DATA_FILE = Path(__file__).parent / "data" / "requests.json"


def display_requests():
    """Display all access-card requests."""

    requests = list_requests()

    if not requests:
        print("\nNo access-card requests found.")
        return

    print("\n--- Access-Card Requests ---")

    for request in requests:
        print(f"\nRequest ID: {request['id']}")
        print(f"Fellow ID: {request['fellow_id']}")
        print(f"Card Type: {request['card_type']}")
        print(f"Status: {request['status']}")
        print(f"Approved By: {request['approved_by']}")


def save_data():
    """Save the current requests."""

    save_requests(DATA_FILE)


def create_new_request():
    """Create and save a new access-card request."""

    fellow_id = input("Enter fellow ID: ")
    card_type = input("Enter card type (visitor/student/staff): ")

    request = create_request(fellow_id, card_type)
    save_data()

    print(f"\nRequest created successfully. ID: {request['id']}")


def approve_existing_request():
    """Approve a request by ID."""

    request_id = input("Enter request ID: ")
    approver_name = input("Enter approver name: ")

    approve_request(request_id, approver_name)
    save_data()

    print("Request approved successfully.")


def issue_existing_card():
    """Issue an approved card."""

    request_id = input("Enter request ID: ")

    issue_card(request_id)
    save_data()

    print("Card issued successfully.")


def return_existing_card():
    """Record a card return."""

    request_id = input("Enter request ID: ")

    return_card(request_id)
    save_data()

    print("Card returned successfully.")


def display_one_request():
    """Find and display a request by ID."""

    request_id = input("Enter request ID: ")
    request = get_request(request_id)

    if request is None:
        print("Request not found.")
        return

    print(f"\nRequest ID: {request['id']}")
    print(f"Fellow ID: {request['fellow_id']}")
    print(f"Card Type: {request['card_type']}")
    print(f"Status: {request['status']}")
    print(f"Approved By: {request['approved_by']}")


def run_menu():
    """Run the Campus Access command-line application."""

    while True:
        print("\n===== CAMPUS ACCESS =====")
        print("1. Create_access_card: ")
        print("2. View_all_requests: ")
        print("3. Find_request by ID: ")
        print("4. Approve_request: ")
        print("5. Issue_card: ")
        print("6. Return_card: ")
        print("7. Save_requests: ")
        print("0. Exit: ")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                create_new_request()

            elif choice == "2":
                display_requests()

            elif choice == "3":
                display_one_request()

            elif choice == "4":
                approve_existing_request()

            elif choice == "5":
                issue_existing_card()

            elif choice == "6":
                return_existing_card()

            elif choice == "7":
                save_data()
                print("Requests saved successfully.")

            elif choice == "0":
                save_data()
                print("Campus Access closed.")
                break

            else:
                print("Invalid choice. Please choose an available option.")

        except ValueError as error:
            print(f"Error: {error}")

        except OSError as error:
            print(f"Storage error: {error}")


def main():
    """Load saved data and start the application."""

    if DATA_FILE.exists():
        try:
            load_requests(DATA_FILE)

        except (ValueError, OSError) as error:
            print(f"Could not load saved requests: {error}")
            print("Please check the data file before continuing.")
            return

    run_menu()


if __name__ == "__main__":
    main()