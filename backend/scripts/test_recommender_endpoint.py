from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# We need to bypass auth or provide a valid auth token.
# Let's bypass authorize_student dependency
from backend.app.main import authorize_student
app.dependency_overrides[authorize_student] = lambda: 1

response = client.get("/api/v1/students/1/recommendations")
print(response.status_code)
print(response.json())
