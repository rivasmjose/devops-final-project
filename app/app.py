from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os

app = Flask(__name__)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://notes:notes@db:5432/notesdb")
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

REQUEST_COUNT = Counter('notes_requests_total', 'Request Count', ['method','endpoint','status_code'])

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    content = db.Column(db.Text)

@app.route('/')
def index():
    notes = Note.query.all()
    return render_template('index.html', notes=notes)

@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    data = [{'id': n.id, 'title': n.title, 'content': n.content} for n in notes]
    REQUEST_COUNT.labels('GET', '/api/notes', 200).inc()
    return jsonify(data)

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.json
    if not data or not data.get('title'):
        REQUEST_COUNT.labels('POST', '/api/notes', 400).inc()
        return jsonify({'error': 'Missing title'}), 400
    note = Note(title=data['title'], content=data.get('content', ''))
    db.session.add(note)
    db.session.commit()
    REQUEST_COUNT.labels('POST', '/api/notes', 201).inc()
    return jsonify({'id': note.id, 'title': note.title}), 201

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
