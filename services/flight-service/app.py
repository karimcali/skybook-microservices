from flask import Flask, request, jsonify

app = Flask(__name__)

flights = {
    "FL100": {
        "origin": "Dublin",
        "destination": "London",
        "date": "2026-05-10",
        "price": 120,
        "seats": {
            "1A": "available",
            "1B": "available",
            "2A": "available",
            "2B": "available"
        }
    }
}


@app.get("/health")
def health():
    return jsonify({
        "service": "flight-service",
        "status": "ok"
    })


@app.get("/flights")
def get_flights():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    date = request.args.get("date")

    results = []

    for flight_id, flight in flights.items():
        if flight["origin"] == origin and flight["destination"] == destination and flight["date"] == date:
            results.append({
                "flight_id": flight_id,
                "origin": flight["origin"],
                "destination": flight["destination"],
                "date": flight["date"],
                "price": flight["price"],
                "seats": flight["seats"]
            })

    return jsonify(results)


@app.post("/flights/<flight_id>/hold-seat")
def hold_seat(flight_id):
    data = request.get_json() or {}
    seat = data.get("seat")

    if not seat:
        return jsonify({"error": "seat is required"}), 400

    flight = flights.get(flight_id)

    if not flight:
        return jsonify({"error": "flight not found"}), 404

    if seat not in flight["seats"]:
        return jsonify({"error": "seat not found"}), 404

    if flight["seats"][seat] != "available":
        return jsonify({"error": "seat is already taken"}), 409

    flight["seats"][seat] = "held"

    return jsonify({
        "flight_id": flight_id,
        "seat": seat,
        "status": "held",
        "price": flight["price"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)