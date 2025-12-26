from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

# Flask app
app = Flask(__name__)
CORS(app)

# global reference to Appdata instance
_state = None


def init_api(state):
    """
    Initializes the API with the global Appdata instance.
    Must be called before start_server().
    """
    global _state
    _state = state


@app.route("/api/effects/current", methods=["GET"])
def get_effect():
    """
    Returns the currently active visual effect.
    """
    return jsonify({"effect": _state.current_effect})


@app.route("/api/effects/current", methods=["POST"])
def set_effect():
    """
    Sets the current visual effect.
    Expected JSON: { "effect": "fire" | "ice" | "blood" | null }
    """
    data = request.json
    _state.current_effect = data.get("effect")
    return jsonify({"ok": True, "effect": _state.current_effect})


def start_server():
    """
    Starts the Flask API server in a background thread so it does not
    block the main CV / tracking loop.
    """
    thread = threading.Thread(
        target=lambda: app.run(
            host="0.0.0.0",   # IMPORTANT: needed for Docker / external access
            port=5001,
            debug=False,
            use_reloader=False
        ),
        daemon=True
    )
    thread.start()