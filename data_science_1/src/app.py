"""
SOTA Data Science Dashboard App (placeholder for portfolio showcase)
"""
from flask import Flask, jsonify
app = Flask(__name__)
@app.route("/health")
def health():
    return jsonify({"status": "ok"})
@app.route("/")
def index():
    return "SOTA Data Science Dashboard - Portfolio Showcase"
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
