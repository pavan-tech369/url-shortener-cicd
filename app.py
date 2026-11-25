import os
import string
import random
from flask import Flask, request, redirect, render_template_string, jsonify
import redis

app = Flask(__name__)

# Connect to Redis (defaults to host 'redis' when running in Docker Compose)
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

db = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

# Simple webpage HTML with a box to paste a long URL
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>DevOps URL Shortener</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 60px auto; padding: 20px; }
        input[type="url"] { width: 75%; padding: 10px; font-size: 16px; }
        button { padding: 10px 18px; font-size: 16px; cursor: pointer; }
        .result { margin-top: 20px; padding: 12px; background: #f0f4f8; border-radius: 5px; }
    </style>
</head>
<body>
    <h2>URL Shortener (Flask + Redis + Docker)</h2>
    <form method="POST" action="/shorten">
        <input type="url" name="url" placeholder="https://example.com" required>
        <button type="submit">Shorten</button>
    </form>
    {% if short_url %}
    <div class="result">
        Short URL: <a href="{{ short_url }}" target="_blank">{{ short_url }}</a>
    </div>
    {% endif %}
</body>
</html>
"""

# Helper function to create a random 6-character code like 'aB9xQ2'
def generate_code(length=6):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))

# 1. Home page route
@app.route("/", methods=["GET"])
def home():
    return render_template_string(HTML_TEMPLATE)

# 2. Save the long URL in Redis and return the short link
@app.route("/shorten", methods=["POST"])
def shorten():
    original_url = request.form.get("url") or (request.json or {}).get("url")
    if not original_url:
        return jsonify({"error": "URL is required"}), 400

    code = generate_code()
    db.set(code, original_url)
    short_url = request.host_url + code

    if request.is_json:
        return jsonify({"short_code": code, "short_url": short_url}), 201
    return render_template_string(HTML_TEMPLATE, short_url=short_url)

# 3. Look up the short code in Redis and redirect the visitor
@app.route("/<code>", methods=["GET"])
def redirect_to_url(code):
    original_url = db.get(code)
    if original_url:
        return redirect(original_url)
    return jsonify({"error": "Short URL not found"}), 404

# 4. Health check route (used by Docker to verify the app is alive)
@app.route("/health", methods=["GET"])
def health():
    try:
        db.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except redis.exceptions.ConnectionError:
        return jsonify({"status": "unhealthy", "redis": "disconnected"}), 503

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)