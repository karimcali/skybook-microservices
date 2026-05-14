from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

FLIGHT_SERVICE_URL = "http://flight-service:5002"
BOOKING_SERVICE_URL = "http://booking-service:5001"


PAGE = """
<!doctype html>
<html>
<head>
    <title>SkyBook</title>
    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background:
                radial-gradient(circle at top left, rgba(30, 136, 229, 0.20), transparent 32%),
                linear-gradient(180deg, #f5f8fc 0%, #eaf1f9 100%);
            color: #102033;
        }

        .hero {
            background:
                linear-gradient(135deg, rgba(6, 42, 76, 0.94), rgba(16, 111, 196, 0.94)),
                linear-gradient(135deg, #0f4c81, #1e88e5);
            color: white;
            padding: 52px 28px 62px;
            text-align: center;
        }

        .hero-badge {
            display: inline-block;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.25);
            border-radius: 999px;
            padding: 8px 14px;
            font-size: 13px;
            margin-bottom: 14px;
        }

        .hero h1 {
            margin: 0;
            font-size: 48px;
            letter-spacing: 1px;
        }

        .hero p {
            margin: 12px 0 0;
            font-size: 18px;
            color: #e8f3ff;
        }

        .container {
            width: 92%;
            max-width: 1120px;
            margin: -34px auto 42px;
        }

        .card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(210, 222, 238, 0.9);
            border-radius: 22px;
            padding: 26px;
            margin-bottom: 24px;
            box-shadow: 0 18px 45px rgba(31, 56, 88, 0.13);
        }

        .section-title {
            margin: 0 0 18px;
            font-size: 25px;
            color: #0d1d33;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
        }

        label {
            display: block;
            font-weight: 700;
            font-size: 13px;
            color: #1a2f4a;
            margin-bottom: 7px;
        }

        input, select {
            width: 100%;
            padding: 13px 14px;
            border: 1px solid #cad8ea;
            border-radius: 12px;
            background: #fbfdff;
            color: #102033;
            font-size: 15px;
            outline: none;
        }

        input:focus, select:focus {
            border-color: #1e88e5;
            box-shadow: 0 0 0 4px rgba(30, 136, 229, 0.14);
        }

        .button {
            display: inline-block;
            background: linear-gradient(135deg, #0f4c81, #156fc2);
            color: white;
            border: none;
            border-radius: 13px;
            padding: 13px 20px;
            font-size: 15px;
            font-weight: 800;
            cursor: pointer;
            box-shadow: 0 9px 18px rgba(15, 76, 129, 0.22);
        }

        .button:hover {
            transform: translateY(-1px);
            box-shadow: 0 12px 24px rgba(15, 76, 129, 0.28);
        }

        .flight-card {
            border: 1px solid #d8e4f3;
            border-radius: 20px;
            padding: 22px;
            margin-top: 16px;
            background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
        }

        .flight-top {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: flex-start;
            margin-bottom: 18px;
        }

        .flight-title {
            font-size: 26px;
            font-weight: 900;
            color: #0b2540;
            margin-bottom: 6px;
        }

        .route {
            color: #5e718c;
            font-size: 15px;
        }

        .price {
            background: #eaf4ff;
            color: #0f4c81;
            border: 1px solid #cde4fb;
            border-radius: 999px;
            padding: 10px 14px;
            font-weight: 900;
            white-space: nowrap;
        }

        .booking-result {
            background: linear-gradient(180deg, #e9fbf0 0%, #dcf6e8 100%);
            border: 1px solid #abe3bd;
            color: #105c2e;
        }

        .booking-result h2 {
            color: #105c2e;
        }

        .error {
            background: #fff0f0;
            border: 1px solid #f0b9b9;
            color: #842029;
        }

        .meta-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            margin-top: 16px;
        }

        .meta-box {
            background: rgba(255, 255, 255, 0.55);
            border: 1px solid rgba(120, 196, 145, 0.45);
            border-radius: 14px;
            padding: 12px;
        }

        .meta-label {
            font-size: 12px;
            opacity: 0.75;
            margin-bottom: 4px;
        }

        .meta-value {
            font-weight: 900;
        }

        .flow {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 10px;
            margin-top: 18px;
        }

        .flow-step {
            background: #f6f9fd;
            border: 1px solid #dbe6f4;
            border-radius: 14px;
            padding: 12px;
            text-align: center;
            font-size: 13px;
            font-weight: 700;
            color: #25425f;
        }

        .small {
            color: #5e718c;
            font-size: 14px;
        }

        .links {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 18px;
        }

        .link-pill {
            text-decoration: none;
            color: #0f4c81;
            background: #eaf4ff;
            border: 1px solid #cde4fb;
            padding: 10px 13px;
            border-radius: 999px;
            font-size: 14px;
            font-weight: 800;
        }

        @media (max-width: 900px) {
            .grid, .meta-grid, .flow {
                grid-template-columns: 1fr;
            }

            .flight-top {
                display: block;
            }

            .price {
                display: inline-block;
                margin-top: 12px;
            }

            .hero h1 {
                font-size: 36px;
            }

            .container {
                margin-top: -22px;
            }
        }
    </style>
</head>
<body>
    <div class="hero">
        <div class="hero-badge">SkyBook Airline Booking System</div>
        <h1>SkyBook</h1>
        <p>Search flights, choose a seat, pay, and trigger booking events.</p>
    </div>

    <div class="container">
        {% if error %}
        <div class="card error">
            <h2 class="section-title">Booking failed</h2>
            <p>{{ error }}</p>
        </div>
        {% endif %}

        {% if booking %}
        <div class="card booking-result">
            <h2 class="section-title">Booking confirmed</h2>
            <p class="small">The booking event was published to RabbitMQ. Ticket and notification services react to it.</p>

            <div class="meta-grid">
                <div class="meta-box">
                    <div class="meta-label">Booking ID</div>
                    <div class="meta-value">{{ booking.booking_id }}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Passenger</div>
                    <div class="meta-value">{{ booking.passenger_name }}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Flight</div>
                    <div class="meta-value">{{ booking.flight_id }}</div>
                </div>
                <div class="meta-box">
                    <div class="meta-label">Seat</div>
                    <div class="meta-value">{{ booking.seat }}</div>
                </div>
            </div>

            <div class="flow">
                <div class="flow-step">UI request</div>
                <div class="flow-step">Seat hold</div>
                <div class="flow-step">Payment</div>
                <div class="flow-step">RabbitMQ</div>
                <div class="flow-step">Ticket + notification</div>
            </div>

            <div class="links">
                <a class="link-pill" href="http://localhost:8090" target="_blank">Open monitoring</a>
                <a class="link-pill" href="http://localhost:15672" target="_blank">Open RabbitMQ</a>
            </div>
        </div>
        {% endif %}

        <div class="card">
            <h2 class="section-title">Search flights</h2>
            <form method="get" action="/">
                <div class="grid">
                    <div>
                        <label>Origin</label>
                        <input name="origin" value="{{ origin }}" required>
                    </div>
                    <div>
                        <label>Destination</label>
                        <input name="destination" value="{{ destination }}" required>
                    </div>
                    <div>
                        <label>Date</label>
                        <input name="date" value="{{ date }}" required>
                    </div>
                </div>
                <br>
                <button class="button" type="submit">Search flights</button>
            </form>
        </div>

        {% if flights %}
        <div class="card">
            <h2 class="section-title">Available flights</h2>

            {% for flight in flights %}
            <div class="flight-card">
                <div class="flight-top">
                    <div>
                        <div class="flight-title">{{ flight.flight_id }}</div>
                        <div class="route">{{ flight.origin }} to {{ flight.destination }} on {{ flight.date }}</div>
                    </div>
                    <div class="price">€{{ flight.price }}</div>
                </div>

                <form method="post" action="/book">
                    <input type="hidden" name="flight_id" value="{{ flight.flight_id }}">

                    <div class="grid">
                        <div>
                            <label>Seat</label>
                            <select name="seat" required>
                                {% for seat, status in flight.seats.items() %}
                                    {% if status == "available" %}
                                    <option value="{{ seat }}">{{ seat }}</option>
                                    {% endif %}
                                {% endfor %}
                            </select>
                        </div>
                        <div>
                            <label>Passenger name</label>
                            <input name="passenger_name" placeholder="Karim Cali" required>
                        </div>
                        <div>
                            <label>Card token</label>
                            <input name="card_token" value="test-card" required>
                        </div>
                    </div>
                    <br>
                    <button class="button" type="submit">Reserve and pay</button>
                </form>
            </div>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


@app.get("/health")
def health():
    return {"service": "web-ui", "status": "ok"}


@app.get("/")
def home():
    origin = request.args.get("origin", "Dublin")
    destination = request.args.get("destination", "London")
    date = request.args.get("date", "2026-05-10")

    flights = []

    if request.args:
        response = requests.get(
            f"{FLIGHT_SERVICE_URL}/flights",
            params={
                "origin": origin,
                "destination": destination,
                "date": date
            },
            timeout=5
        )

        if response.status_code == 200:
            flights = response.json()

            for flight in flights:
                if "seats" not in flight:
                    seats = {}

                    for seat in flight.get("available_seats", []):
                        seats[seat] = "available"

                    flight["seats"] = seats

    return render_template_string(
        PAGE,
        origin=origin,
        destination=destination,
        date=date,
        flights=flights,
        booking=None,
        error=None
    )


@app.post("/book")
def book():
    data = {
        "flight_id": request.form.get("flight_id"),
        "seat": request.form.get("seat"),
        "passenger_name": request.form.get("passenger_name"),
        "card_token": request.form.get("card_token")
    }

    response = requests.post(
        f"{BOOKING_SERVICE_URL}/bookings",
        json=data,
        timeout=5
    )

    if response.status_code not in [200, 201]:
        return render_template_string(
            PAGE,
            origin="Dublin",
            destination="London",
            date="2026-05-10",
            flights=[],
            booking=None,
            error=response.text
        )

    return render_template_string(
        PAGE,
        origin="Dublin",
        destination="London",
        date="2026-05-10",
        flights=[],
        booking=response.json(),
        error=None
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)