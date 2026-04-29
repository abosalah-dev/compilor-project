"""Flask entry point exposing endpoints for all compiler phases."""

from flask import Flask, jsonify, render_template, request

from memory import execute
from scanner import scan
from semantic import analyze

app = Flask(__name__)


@app.route("/")
def index():
    """Render the single-page GUI."""
    return render_template("index.html")


@app.route("/scan", methods=["POST"])
def scan_route():
    """Run lexical analysis for submitted source code."""
    code = request.json.get("code", "")
    return jsonify(scan(code))


@app.route("/analyze", methods=["POST"])
def analyze_route():
    """Run semantic checks for submitted source code."""
    code = request.json.get("code", "")
    return jsonify(analyze(code))


@app.route("/execute", methods=["POST"])
def execute_route():
    """Execute assignment statements and return memory states."""
    code = request.json.get("code", "")
    return jsonify(execute(code))


if __name__ == "__main__":
    app.run(debug=True)
