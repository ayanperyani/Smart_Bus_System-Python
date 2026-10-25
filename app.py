import streamlit as st
import pandas as pd
from database import routes
from state import bookings, issued_booking_ids
import state
from helpers import find_route, generate_booking_id

st.set_page_config(page_title="Smart Bus Reservation System", page_icon="🚌", layout="wide")

st.markdown("""
<style>
.main-header {padding: 1.2rem 1.4rem; border-radius: 14px; background: linear-gradient(110deg,#102a43,#176b87); color:white; margin-bottom:1rem;}
.main-header h1 {color:white; margin:0;}
.main-header p {color:#e6f6ff; margin:.35rem 0 0 0;}
div[data-testid="stMetric"] {background:#f4f8fb; padding:14px; border-radius:12px; border:1px solid #dce8ef;}
</style>
<div class="main-header"><h1>🚌 Smart Bus Reservation System</h1><p>Search routes, book tickets, manage reservations, and monitor seat availability.</p></div>
""", unsafe_allow_html=True)

if "flash_message" not in st.session_state:
    st.session_state.flash_message = None
if st.session_state.flash_message:
    kind, msg = st.session_state.flash_message
    getattr(st, kind)(msg)
    st.session_state.flash_message = None


def route_frame(route_list=None):
    rows = []
    for r in (routes if route_list is None else route_list):
        avail = r["available_seats"]
        status = "Fully Booked" if avail == 0 else ("Available" if avail == r["total_seats"] else "Partially Booked")
        rows.append({"Route ID": r["route_id"], "From": r["departure"].strip(), "To": r["destination"].strip(),
                     "Departure": r["departure_time"], "Fare (Rs.)": r["fare"],
                     "Available Seats": avail, "Total Seats": r["total_seats"], "Status": status})
    return pd.DataFrame(rows)


def bookings_frame():
    rows = []
    for b in bookings:
        r = find_route(b["route_id"])
        rows.append({"Booking ID": b["booking_id"], "Passenger": b["passenger_name"], "Age": b["passenger_age"],
                     "Route ID": b["route_id"], "Journey": f"{r['departure'].strip()} → {r['destination'].strip()}" if r else "N/A",
                     "Seats": b["seats"], "Total Fare (Rs.)": b["total_fare"], "Status": b["status"]})
    return pd.DataFrame(rows)

confirmed = [b for b in bookings if b["status"] == "Confirmed"]
revenue = sum(b["total_fare"] for b in confirmed)
reserved_seats = sum(b["seats"] for b in confirmed)
available_seats = sum(r["available_seats"] for r in routes)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Routes", len(routes))
m2.metric("Confirmed Bookings", len(confirmed))
m3.metric("Seats Available", available_seats)
m4.metric("Confirmed Revenue", f"Rs. {revenue:,}")

pages = ["Dashboard", "Find Routes", "Book Ticket", "Bookings & Cancellation", "Seat Availability", "Reports & Schedule"]
page = st.sidebar.radio("Navigation", pages)
st.sidebar.divider()
st.sidebar.caption("Smart Bus Reservation System · Streamlit edition")

if page == "Dashboard":
    st.subheader("Welcome")
    st.write("Use the menu to search for a bus, reserve seats, cancel a booking, or review system reports.")
    st.subheader("All Bus Routes")
    st.dataframe(route_frame(), use_container_width=True, hide_index=True)
    left, right = st.columns(2)
    with left:
        st.subheader("Booking Status")
        status_counts = pd.DataFrame({"Status": ["Confirmed", "Cancelled"],
                                      "Bookings": [len(confirmed), sum(b["status"] == "Cancelled" for b in bookings)]})
        st.bar_chart(status_counts.set_index("Status"))
    with right:
        st.subheader("Seats by Route")
        seat_data = pd.DataFrame([{"Route": r["route_id"], "Available": r["available_seats"],
                                   "Booked": r["total_seats"] - r["available_seats"]} for r in routes]).set_index("Route")
        st.bar_chart(seat_data)

elif page == "Find Routes":
    st.subheader("Find a Bus Route")
    term = st.text_input("Search by route ID, departure city, or destination", placeholder="e.g. R101, Gulshan, Defence")
    only_available = st.checkbox("Show only routes with available seats")
    matches = [r for r in routes if term.strip().lower() in (r["route_id"] + " " + r["departure"] + " " + r["destination"]).lower()] if term.strip() else routes[:]
    if only_available:
        matches = [r for r in matches if r["available_seats"] > 0]
    if matches:
        st.dataframe(route_frame(matches), use_container_width=True, hide_index=True)
    else:
        st.info("No matching routes found. Try another route ID or city name.")

elif page == "Book Ticket":
    st.subheader("Book Your Ticket")
    st.caption("Select a route and passenger details. Your booking will be confirmed immediately.")
    selectable = [r for r in routes if r["available_seats"] > 0]
    if not selectable:
        st.warning("All routes are fully booked at the moment.")
    else:
        options = {f"{r['route_id']} · {r['departure'].strip()} → {r['destination'].strip()} · {r['departure_time']} · Rs. {r['fare']} · {r['available_seats']} seats left": r for r in selectable}
        with st.form("booking_form", clear_on_submit=True):
            passenger_name = st.text_input("Passenger full name")
            age = st.number_input("Passenger age", min_value=1, max_value=120, value=18, step=1)
            selected_label = st.selectbox("Bus route", list(options.keys()))
            selected_route = options[selected_label]
            seats = st.number_input("Number of seats", min_value=1, max_value=max(1, selected_route["available_seats"]), value=1, step=1)
            st.info(f"Estimated total fare: Rs. {selected_route['fare'] * seats:,}")
            submitted = st.form_submit_button("Confirm Booking", type="primary", use_container_width=True)
        if submitted:
            route = options[selected_label]
            if not passenger_name.strip():
                st.error("Please enter the passenger's name.")
            elif seats > route["available_seats"]:
                st.error(f"Only {route['available_seats']} seat(s) are available on this route.")
            else:
                booking_id = generate_booking_id()
                total_fare = route["fare"] * int(seats)
                bookings.append({"booking_id": booking_id, "passenger_name": passenger_name.strip(),
                                 "passenger_age": int(age), "route_id": route["route_id"], "seats": int(seats),
                                 "total_fare": total_fare, "status": "Confirmed"})
                route["available_seats"] -= int(seats)
                st.success("Ticket booked successfully!")
                st.markdown(f"### Booking ID: `{booking_id}`")
                a, b, c = st.columns(3)
                a.metric("Route", route["route_id"])
                b.metric("Seats", int(seats))
                c.metric("Total Fare", f"Rs. {total_fare:,}")
                st.write(f"**Journey:** {route['departure'].strip()} → {route['destination'].strip()}  ")
                st.write(f"**Departure:** {route['departure_time']} · **Passenger:** {passenger_name.strip()}")

elif page == "Bookings & Cancellation":
    st.subheader("Bookings")
    if not bookings:
        st.info("No bookings have been made yet.")
    else:
        st.dataframe(bookings_frame(), use_container_width=True, hide_index=True)
        st.subheader("Cancel a Booking")
        cancellable = [b for b in bookings if b["status"] == "Confirmed"]
        if not cancellable:
            st.info("There are no confirmed bookings to cancel.")
        else:
            booking_labels = {f"{b['booking_id']} · {b['passenger_name']} · {b['route_id']} · {b['seats']} seat(s)": b for b in cancellable}
            with st.form("cancel_form"):
                selected_booking_label = st.selectbox("Choose a confirmed booking", list(booking_labels.keys()))
                confirm_cancel = st.checkbox("I confirm that I want to cancel this booking")
                cancel_submitted = st.form_submit_button("Cancel Booking", type="secondary")
            if cancel_submitted:
                if not confirm_cancel:
                    st.warning("Please tick the confirmation box before cancelling.")
                else:
                    booking = booking_labels[selected_booking_label]
                    route = find_route(booking["route_id"])
                    if route:
                        route["available_seats"] = min(route["total_seats"], route["available_seats"] + booking["seats"])
                    booking["status"] = "Cancelled"
                    st.success(f"Booking {booking['booking_id']} cancelled. Seats have been restored.")
                    st.rerun()

elif page == "Seat Availability":
    st.subheader("Live Seat Availability")
    only_available = st.checkbox("Hide fully booked routes")
    seat_routes = [r for r in routes if not only_available or r["available_seats"] > 0]
    st.dataframe(route_frame(seat_routes), use_container_width=True, hide_index=True)
    if seat_routes:
        st.subheader("Seat Availability by Route")
        st.bar_chart(pd.DataFrame([{"Route": r["route_id"], "Available Seats": r["available_seats"],
                                    "Booked Seats": r["total_seats"] - r["available_seats"]} for r in seat_routes]).set_index("Route"))

elif page == "Reports & Schedule":
    st.subheader("Booking Report")
    cancelled = [b for b in bookings if b["status"] == "Cancelled"]
    fully_booked = sum(r["available_seats"] == 0 for r in routes)
    a, b, c = st.columns(3)
    a.metric("All Bookings", len(bookings))
    b.metric("Cancelled Bookings", len(cancelled))
    c.metric("Fully Booked Routes", fully_booked)
    d, e, f = st.columns(3)
    d.metric("Reserved Seats", reserved_seats)
    e.metric("Confirmed Revenue", f"Rs. {revenue:,}")
    f.metric("Available Seats", available_seats)
    st.subheader("Route Schedule by Departure City")
    cities = sorted(set(r["departure"].strip() for r in routes), key=str.lower)
    for city in cities:
        city_routes = [r for r in routes if r["departure"].strip().lower() == city.lower()]
        with st.expander(city, expanded=True):
            st.dataframe(route_frame(city_routes)[["Route ID", "To", "Departure", "Fare (Rs.)", "Available Seats", "Status"]],
                         use_container_width=True, hide_index=True)
    if bookings:
        st.subheader("Download Booking Report")
        csv = bookings_frame().to_csv(index=False).encode("utf-8")
        st.download_button("Download bookings as CSV", data=csv, file_name="smart_bus_bookings.csv", mime="text/csv")
