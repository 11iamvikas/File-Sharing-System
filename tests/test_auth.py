import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ops_login_fail():
    response = client.post('/ops/login', json={"email": "notfound@x.com", "password": "badpass"})
    assert response.status_code == 401

def test_client_signup_and_verify(monkeypatch):
    emails = {}
    def fake_send_email(to_email, subject, body):
        emails['url'] = body.split('http')[1].split()[0]
    monkeypatch.setattr('app.services.email.send_email', fake_send_email)
    response = client.post('/client/signup', json={"email": "test@client.com", "password": "testpass"})
    assert response.status_code == 200
    assert 'verify_url' in response.json()
    verify_url = response.json()['verify_url']
    token = verify_url.split('/')[-1]
    verify_resp = client.get(f'/client/verify/{token}')
    assert verify_resp.status_code in (200, 307)

def test_client_login_unverified():
    response = client.post('/client/login', json={"email": "test2@client.com", "password": "testpass"})
    assert response.status_code == 403 or response.status_code == 401 