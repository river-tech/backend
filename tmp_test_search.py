from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print('GET /api/workflows/search without q')
resp = client.get('/api/workflows/search')
print(resp.status_code)
print(resp.text)

print('\nGET /api/workflows/search?q=hello')
resp = client.get('/api/workflows/search?q=hello')
print(resp.status_code)
print(resp.text)
