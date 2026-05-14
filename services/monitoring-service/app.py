from flask import Flask, render_template_string
import requests

app = Flask(__name__)

services = {
    "web-ui": "http://web-ui:5000/health",
    "booking-service": "http://booking-service:5001/health",
    "flight-service": "http://flight-service:5002/health",
    "payment-service": "http://payment-service:5003/health",
    "ticket-service": "http://ticket-service:5004/health",
    "notification-service": "http://notification-service:5005/health"
}

PAGE = """
<!doctype html>
<html>
<head>
    <title>SkyBook Monitoring</title>
    <style>
        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #eef3fb;
            color: #172033;
        }

        .hero {
            background: linear-gradient(135deg, #172033, #0f4c81);
            color: white;
            padding: 36px;
            text-align: center;
        }

        .hero h1 {
            margin: 0;
            font-size: 36px;
        }

        .container {
            width: 92%;
            max-width: 900px;
            margin: 30px auto;
        }

        .card {
            background: white;
            border-radius: 18px;
            padding: 24px;
            box-shadow: 0 10px 28px rgba(20, 40, 80, 0.12);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th, td {
            text-align: left;
            padding: 14px;
            border-bottom: 1px solid #dbe5f2;
        }

        th {
            background: #f4f8fd;
        }

        .ok {
            color: #0b7a3b;
            font-weight: bold;
        }

        .down {
            color: #b00020;
            font-weight: bold;
        }

        .small {
            color: #65748b;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="hero">
        <h1>SkyBook Monitoring</h1>
        <p>Health status for the running microservices.</p>
    </div>

    <div class="container">
        <div class="card">
            <table>
                <tr>
                    <th>Service</th>
                    <th>Status</th>
                    <th>Details</th>
                </tr>
                {% for item in results %}
                <tr>
                    <td>{{ item.name }}</td>
                    <td class="{{ item.css }}">{{ item.status }}</td>
                    <td class="small">{{ item.details }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>
</body>
</html>
"""


@app.get("/health")
def health():
    return {
        "service": "monitoring-service",
        "status": "ok"
    }


@app.get("/")
def dashboard():
    results = []

    for name, url in services.items():
        try:
            response = requests.get(url, timeout=3)

            if response.status_code == 200:
                data = response.json()
                status = data.get("status", "ok")

                results.append({
                    "name": name,
                    "status": status,
                    "details": "HTTP 200",
                    "css": "ok"
                })
            else:
                results.append({
                    "name": name,
                    "status": "down",
                    "details": f"HTTP {response.status_code}",
                    "css": "down"
                })

        except Exception as error:
            results.append({
                "name": name,
                "status": "down",
                "details": str(error),
                "css": "down"
            })

    return render_template_string(PAGE, results=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5010)