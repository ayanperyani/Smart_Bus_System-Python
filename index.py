# from main_menu import main
import functions as fun


"""
SMART BUS TICKET BOOKING & RESERVATION SYSTEM
Python 3 Console Application
PRD-compliant implementation
"""


def display_menu():
    print("\n" + "=" * 40)
    print(" SMART BUS RESERVATION SYSTEM")
    print("=" * 40)
    print(" 1. View Available Routes")
    print(" 2. Search for a Route")
    print(" 3. Book a Ticket")
    print(" 4. View My Bookings")
    print(" 5. Cancel a Booking")
    print(" 6. View Seat Availability")
    print(" 7. Generate Booking Report")
    print(" 8. View Route Schedule")
    print(" 9. Exit")
    print("=" * 40)


def main():
    while True:
        display_menu()
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            fun.view_available_routes()
        elif choice == "2":
            fun.search_route()
        elif choice == "3":
            fun.book_ticket()
        elif choice == "4":
            fun.view_bookings()
        elif choice == "5":
            fun.cancel_booking()
        elif choice == "6":
            fun.view_seat_availability()
        elif choice == "7":
            fun.generate_report()
        elif choice == "8":
            fun.route_schedule()
        elif choice == "0":
            print("Thank you for using the Smart Bus Reservation System. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 9.")


main()

