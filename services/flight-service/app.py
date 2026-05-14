from flask import Flask, request, jsonify

app = Flask(__name__)

flights = {
    "FL100": {
        "flight_id": "FL100",
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
    },
    "FL200": {
        "flight_id": "FL200",
        "origin": "Dublin",
        "destination": "Paris",
        "date": "2026-05-10",
        "price": 150,
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

    for flight in flights.values():
        if origin and flight["origin"] != origin:
            continue
        if destination and flight["destination"] != destination:
            continue
        if date and flight["date"] != date:
            continue

        results.append({
            "flight_id": flight["flight_id"],
            "origin": flight["origin"],
            "destination": flight["destination"],
            "date": flight["date"],
            "price": flight["price"],
            "seats": flight["seats"]
        })

    return jsonify(results)


@app.post("/flights/<flight_id>/hold-seat")
def hold_seat(flight_id):
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    seat = data.get("seat")

    if not seat:
        return jsonify({"error": "seat is required"}), 400

    flight = flights.get(flight_id)

    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    if seat not in flight["seats"]:
        return jsonify({"error": "Seat not found"}), 404

    if flight["seats"][seat] != "available":
        return jsonify({"error": "Seat is already taken"}), 409

    flight["seats"][seat] = "held"

    return jsonify({
        "message": "Seat held successfully",
        "flight_id": flight_id,
        "seat": seat,
        "status": "held",
        "price": flight["price"]
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)