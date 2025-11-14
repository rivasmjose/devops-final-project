"""Flask Notes App with Prometheus metrics and PostgreSQL storage."""

import os

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

# Flask app setup
app = Flask(__name__, static_folder="static", template_folder="templates")
db_url = os.getenv(
    "DATABASE_URL", "postgresql://notesuser:notespass@db:5432/notesdb"
)

# Fix possible postgres:// format
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(app)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "app_request_count", "Total count of requests", ["method", "endpoint", "http_status"]
)


class Note(db.Model):  # pylint: disable=too-few-public-methods
    """Database model for storing a note with a title and content."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)

    def to_dict(self):
        """Return a dictionary representation of the note."""
        return {"id": self.id, "title": self.title, "content": self.content}


@app.after_request
def after_request(response):
    """Increment Prometheus request counter after each request."""
    try:
        REQUEST_COUNT.labels(
            method=request.method, endpoint=request.path, http_status=response.status_code
        ).inc()
    except Exception:  # pylint: disable=broad-except
        pass
    return response


@app.route("/")
def home():
    """Render the home page."""
    return render_template("index.html")


@app.route("/notes", methods=["GET"])
def get_notes():
    """Return all notes as JSON."""
    notes = Note.query.all()
    return jsonify([note.to_dict() for note in notes])


@app.route("/notes", methods=["POST"])
def add_note():
    """Add a new note from JSON request data."""
    data = request.get_json()
    note = Note(title=data["title"], content=data["content"])
    db.session.add(note)
    db.session.commit()
    return jsonify(note.to_dict()), 201


@app.route("/notes/<int:note_id>", methods=["DELETE"])
def delete_note(note_id):
    """Delete a note by ID."""
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({"message": "Note deleted"})


@app.route("/metrics")
def metrics():
    """Return Prometheus metrics."""
    metrics_data = generate_latest()
    return metrics_data, 200, {"Content-Type": CONTENT_TYPE_LATEST}


if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()

    app.run(host="0.0.0.0", port=5000)
