
from flask import Flask, render_template, request, jsonify
import requests
import os
from datetime import datetime

app = Flask(__name__)

NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "")
SIGNAL_PIN = os.environ.get("SIGNAL_PIN", "")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/signal", methods=["POST"])
def send_signal():
    data = request.get_json(silent=True) or {}

    if not SIGNAL_PIN or data.get("pin") != SIGNAL_PIN:
        return jsonify({
            "success": False,
            "message": "Incorrect PIN."
        }), 403

    if not NTFY_TOPIC:
        return jsonify({
            "success": False,
            "message": "Notification service not configured."
        }), 503

    message = (
        "Teacher has pressed the red signal!\n"
        + datetime.now().strftime("%d-%m-%Y %H:%M:%S")
    )

    try:
        response = requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode("utf-8"),
            headers={
                "Title": "RED SIGNAL ALERT",
                "Priority": "urgent"
            },
            timeout=10
        )
        response.raise_for_status()

        return jsonify({
            "success": True,
            "message": "Alert sent successfully!"
        })

    except requests.RequestException:
        app.logger.exception("Notification failed")
        return jsonify({
            "success": False,
            "message": "Failed to send alert."
        }), 502


if __name__ == "__main__":
    app.run()
