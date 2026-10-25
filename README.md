# Smart Bus Reservation System — Streamlit Edition

A web-based interface for the Smart Bus Ticket Booking & Reservation System. The Streamlit app supports route search, ticket booking, booking cancellation, seat availability, reports, schedule views, and CSV export.

## Requirements
- Python 3.9 or newer
- pip

## Run locally
1. Extract this folder and open a terminal in it.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   streamlit run app.py
   ```
4. Open the local URL shown in the terminal (usually `http://localhost:8501`).

## Features
- Dashboard with booking and seat metrics
- Search routes by route ID, departure, or destination
- Book one or more seats and calculate the fare
- View bookings and cancel confirmed bookings
- Restore seats after cancellation
- Seat availability table and chart
- Booking reports and route schedule
- Download booking data as CSV

## Important storage note
The original project stores routes and bookings in Python memory. Therefore, bookings and changed seat counts reset when the app process restarts. This version is suitable for demonstration and local practice, not multi-user production use. A persistent database would be needed to keep bookings between restarts.

## Project files
- `app.py` — Streamlit user interface and booking workflow
- `database.py` — sample bus route data
- `state.py` — in-memory booking state
- `functions.py`, `helpers.py`, `index.py` — original console application modules
- `requirements.txt` — app dependencies
