from fastapi.testclient import TestClient

from app.main import app

#create the client
client = TestClient(app)

#Define the test
def test_health_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status":"ok"}

def test_unknown_route_returns_not_found() -> None:
    response = client.get("/unknown")

    assert response.status_code==404
    assert response.json() == {"detail":"Not Found"}