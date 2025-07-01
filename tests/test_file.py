import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def get_ops_token():
    # This assumes an ops user exists with these credentials
    resp = client.post('/ops/login', json={"email": "ops@admin.com", "password": "opspass"})
    if resp.status_code == 200:
        return resp.json()['access_token']
    return None

def get_client_token():
    # This assumes a client user exists and is verified
    resp = client.post('/client/login', json={"email": "test@client.com", "password": "testpass"})
    if resp.status_code == 200:
        return resp.json()['access_token']
    return None

def test_upload_file(monkeypatch):
    token = get_ops_token()
    if not token:
        pytest.skip("No ops user available")
    files = {'file': ('test.docx', b'content', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.post('/ops/upload', files=files, headers=headers)
    assert resp.status_code == 200
    assert 'filename' in resp.json()

def test_list_files():
    token = get_client_token()
    if not token:
        pytest.skip("No client user available")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get('/client/files', headers=headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_download_link():
    token = get_client_token()
    if not token:
        pytest.skip("No client user available")
    headers = {"Authorization": f"Bearer {token}"}
    # Assume at least one file exists
    files_resp = client.get('/client/files', headers=headers)
    if not files_resp.json():
        pytest.skip("No files to download")
    file_id = files_resp.json()[0]['id']
    resp = client.get(f'/client/download/{file_id}', headers=headers)
    assert resp.status_code == 200
    assert 'download_link' in resp.json() 