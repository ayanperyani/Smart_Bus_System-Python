import state
from database import routes


def find_route(route_id):
    """Return route dict if found, else None."""
    for route in routes:
        if route["route_id"].lower() == route_id.lower():
            return route
    return None


def generate_booking_id():
    """Generate a unique booking ID like B1001, B1002..."""
    while True:
        state.booking_counter += 1
        new_id = f"T{state.booking_counter}"
        if new_id not in state.issued_booking_ids:
            state.issued_booking_ids.add(new_id)
            return new_id


def get_int_input(prompt):
    """Safely read an integer, return None on failure."""
    try:
        return int(input(prompt).strip())
    except ValueError:
        return None


def print_route_line(route, index=None):
    """Print a formatted route row."""
    status = "Fully Booked" if route["available_seats"] == 0 else "Available"
    prefix = f"{index}. " if index is not None else ""
    print(f"{prefix}{route['route_id']:5} | "
          f"{route['departure']} - {route['destination']:15} | "
          f"{route['departure_time']:9} | "
          f"Rs. {route['fare']:<5} | "
          f"{route['available_seats']}/{route['total_seats']} | {status}")
