from app import app, db, Note
import pytest

@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_create_note(client):
    res = client.post('/api/notes', json={'title':'Hello','content':'World'})
    assert res.status_code == 201
