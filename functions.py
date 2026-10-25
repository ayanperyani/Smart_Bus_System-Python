from database import routes
from state import bookings, supported_cities
from helpers import find_route, generate_booking_id, get_int_input, print_route_line


def view_available_routes():
    print("\n--- AVAILABLE BUS ROUTES ---")
    print(f"{'No.':<4}{'Route':<6}{'Journey':<35}{'Depart':<11}{'Fare':<9}{'Seats':<10}{'Status'}")
    print("-" * 95)

    available_only = input("Show only routes with seats available? (y/n): ").strip().lower()

    count = 0
    for i, route in enumerate(routes, start=1):
        if available_only == "y":
            if route["available_seats"] == 0:
                continue
        print_route_line(route, i)
        count += 1

    if count == 0:
        print("No available routes found.")


def search_route():
    print("\n--- SEARCH FOR A ROUTE ---")
    term = input("Enter route ID, departure city, or destination city: ").strip()
    if not term:
        print("Empty search term.")
        return

    term_lower = term.lower()
    found = False

    if term_lower.startswith("r"):
        for route in routes:
            if route["route_id"].lower() == term_lower:
                print("\nMatch found:")
                print_route_line(route)
                found = True
                break
        else:
            print("No match found for that route ID.")

    if not found:
        print("\nMatches:")
        for route in routes:
            if term_lower in route["departure"].lower() or term_lower in route["destination"].lower():
                print_route_line(route)
                found = True

        if not found:
            print(f"No routes matched '{term}'.")


def book_ticket():
    print("\n--- BOOK A TICKET ---")
    name = input("Passenger name: ").strip()
    if not name:
        print("Error: Passenger name cannot be blank.")
        return

    age = get_int_input("Passenger age: ")
    if age is None or age <= 0:
        print("Error: Age must be a positive integer.")
        return

    route_id = input("Route ID (e.g., R101): ").strip()
    route = find_route(route_id)
    if route is None:
        print(f"Error: Route '{route_id}' does not exist.")
        return

    seats = get_int_input("Number of seats: ")
    if seats is None or seats <= 0:
        print("Error: Seat quantity must be a positive integer.")
        return

    if seats > route["available_seats"]:
        print(f"Error: Only {route['available_seats']} seat(s) available on {route['route_id']}.")
        return

    booking_id = generate_booking_id()
    total_fare = route["fare"] * seats
    booking = {
        "booking_id": booking_id,
        "passenger_name": name,
        "passenger_age": age,
        "route_id": route["route_id"],
        "seats": seats,
        "total_fare": total_fare,
        "status": "Confirmed",
    }
    bookings.append(booking)
    route["available_seats"] -= seats

    print("\n===== BOOKING CONFIRMED =====")
    print(f"Booking ID     : {booking_id}")
    print(f"Passenger      : {name} (age {age})")
    print(f"Route          : {route['route_id']} {route['departure']} -> {route['destination']}")
    print(f"Departure Time : {route['departure_time']}")
    print(f"Seats          : {seats}")
    print(f"Total Fare     : Rs. {total_fare}")
    print(f"Remaining Seats: {route['available_seats']}/{route['total_seats']}")


def view_bookings():
    print("\n--- ALL BOOKINGS ---")
    if not bookings:
        print("No bookings found.")
        return

    for i, b in enumerate(bookings, start=1):
        route = find_route(b["route_id"])
        journey = f"{route['departure']} -> {route['destination']}" if route else "N/A"
        print(f"{i}. {b['booking_id']} | {b['passenger_name']} (age {b['passenger_age']}) | "
              f"{b['route_id']} {journey} | Seats: {b['seats']} | "
              f"Fare: Rs. {b['total_fare']} | Status: {b['status']}")


def cancel_booking():
    print("\n--- CANCEL A BOOKING ---")
    booking_id = input("Enter booking ID to cancel: ").strip().upper()

    for b in bookings:
        if b["booking_id"] == booking_id:
            if b["status"] == "Cancelled":
                print(f"Booking {booking_id} is already cancelled.")
                return

            route = find_route(b["route_id"])
            if route is not None:
                route["available_seats"] += b["seats"]
                restored = b["seats"]
            else:
                restored = 0

            b["status"] = "Cancelled"
            print(f"Booking {booking_id} has been cancelled.")
            print(f"Seats restored: {restored}")
            if route:
                print(f"Route {route['route_id']} available seats: {route['available_seats']}/{route['total_seats']}")
            return

    print(f"Booking {booking_id} not found.")


def view_seat_availability():
    print("\n--- SEAT AVAILABILITY ---")
    filter_choice = input("Show only routes with seats available? (y/n): ").strip().lower()

    for route in routes:
        if filter_choice == "y" and route["available_seats"] == 0:
            continue

        avail = route["available_seats"]
        total = route["total_seats"]
        if avail == total:
            status = "Available"
        elif avail == 0:
            status = "Fully Booked"
        else:
            status = "Partially Booked"

        print(f"{route['route_id']} | {route['departure']} -> {route['destination']:15} | "
              f"Available: {avail}/{total} | Status: {status}")


def generate_report():
    print("\n--- BOOKING REPORT ---")

    total_bookings = len(bookings)
    confirmed = 0
    cancelled = 0
    reserved_seats = 0
    confirmed_revenue = 0

    for b in bookings:
        if b["status"] == "Confirmed":
            confirmed += 1
        elif b["status"] == "Cancelled":
            cancelled += 1

    for route in routes:
        for b in bookings:
            if b["route_id"] == route["route_id"] and b["status"] == "Confirmed":
                reserved_seats += b["seats"]
                confirmed_revenue += b["total_fare"]

    fully_booked = 0
    for route in routes:
        if route["available_seats"] == 0:
            fully_booked += 1

    print(f"Total bookings created  : {total_bookings}")
    print(f"Confirmed bookings      : {confirmed}")
    print(f"Cancelled bookings      : {cancelled}")
    print(f"Seats currently reserved: {reserved_seats}")
    print(f"Confirmed revenue       : Rs. {confirmed_revenue}")
    print(f"Fully booked routes     : {fully_booked}")


def route_schedule():
    print("\n=== ROUTE SCHEDULE BY DEPARTURE CITY ===")
    for city in supported_cities:
        print(f"\n{city}")
        found = False
        for route in routes:
            if route["departure"].lower() == city.lower():
                print(f"  {route['route_id']} -> {route['destination']} | {route['departure_time']}")
                found = True
        if not found:
            print("  No scheduled departures.")
