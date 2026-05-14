from flask import Flask, request, jsonify
import uuid

app = Flask(__name__)

authorisations = {}
payments = {}


@app.get("/health")
def health():
    return jsonify({
        "service": "payment-service",
        "status": "ok"
    })


@app.post("/payments/authorise")
def authorise_payment():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    card_token = data.get("card_token")
    amount = data.get("amount")

    if not card_token:
        return jsonify({"error": "card_token is required"}), 400

    if card_token == "fail-card":
        return jsonify({
            "status": "declined",
            "reason": "Card was declined"
        }), 402

    authorisation_id = "AUTH-" + str(uuid.uuid4())[:8]

    authorisations[authorisation_id] = {
        "authorisation_id": authorisation_id,
        "card_token": card_token,
        "amount": amount,
        "status": "authorised"
    }

    return jsonify({
        "message": "Payment authorised",
        "authorisation_id": authorisation_id,
        "status": "authorised"
    })


@app.post("/payments/capture")
def capture_payment():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    authorisation_id = data.get("authorisation_id")

    if not authorisation_id:
        return jsonify({"error": "authorisation_id is required"}), 400

    authorisation = authorisations.get(authorisation_id)

    if not authorisation:
        return jsonify({"error": "Authorisation not found"}), 404

    if authorisation["status"] != "authorised":
        return jsonify({"error": "Payment is not authorised"}), 400

    payment_id = "PAY-" + str(uuid.uuid4())[:8]

    payments[payment_id] = {
        "payment_id": payment_id,
        "authorisation_id": authorisation_id,
        "amount": authorisation["amount"],
        "status": "captured"
    }

    authorisation["status"] = "captured"

    return jsonify({
        "message": "Payment captured",
        "payment_id": payment_id,
        "authorisation_id": authorisation_id,
        "status": "captured"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)