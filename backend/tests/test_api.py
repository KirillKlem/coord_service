from io import BytesIO

from fastapi.testclient import TestClient


def _auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/auth/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_full_flow(client: TestClient):
    headers = _auth_headers(client)

    project_resp = client.post(
        "/api/projects/",
        json={"name": "Test Project", "description": "Demo"},
        headers=headers,
    )
    assert project_resp.status_code == 201
    project_id = project_resp.json()["id"]

    files = [
        ("files", ("house.jpg", BytesIO(b"fake-image-bytes"), "image/jpeg")),
    ]
    predict_resp = client.post(
        "/api/analysis/predict",
        headers=headers,
        files=files,
        data={"project_id": str(project_id)},
    )
    assert predict_resp.status_code == 202
    body = predict_resp.json()
    assert body["status"] in ("completed", "running")
    query_id = body["query_id"]

    if body["status"] == "running":
        poll_resp = client.get(f"/api/analysis/predict/{query_id}", headers=headers)
        assert poll_resp.status_code == 200
        body = poll_resp.json()

    images = body.get("images") or []
    assert images, "Expected images in prediction response"
    detections = images[0]["detections"]
    assert detections, "Expected detections for the uploaded image"
    lat = detections[0]["latitude"]
    lon = detections[0]["longitude"]

    search_resp = client.get(
        "/api/analysis/search",
        headers=headers,
        params={
            "lat": lat,
            "lon": lon,
            "radius_km": 1.0,
            "project_id": project_id,
        },
    )
    assert search_resp.status_code == 200
    search_body = search_resp.json()
    assert search_body["results"], "Search results should not be empty"

    export_xlsx = client.get("/api/export/xlsx", headers=headers, params={"query_id": query_id})
    assert export_xlsx.status_code == 200
    assert export_xlsx.headers["content-type"].startswith("application/vnd.openxmlformats")

    export_zip = client.get("/api/export/images", headers=headers, params={"query_id": query_id})
    assert export_zip.status_code == 200
    assert export_zip.headers["content-type"] == "application/zip"
