import requests


def test_all_services_are_healthy():
    services = {
        "web-ui": "http://localhost:8080/health",
        "booking-service": "http://localhost:5001/health",
        "flight-service": "http://localhost:5002/health",
        "payment-service": "http://localhost:5003/health",
        "ticket-service": "http://localhost:5004/health",
        "notification-service": "http://localhost:5005/health",
        "monitoring-service": "http://localhost:8090/health",
    }

    for service_name, url in services.items():
        response = requests.get(url, timeout=5)

        assert response.status_code == 200, service_name

        data = response.json()
        assert data["service"] == service_name
        assert data["status"] in ["ok", "healthy"]