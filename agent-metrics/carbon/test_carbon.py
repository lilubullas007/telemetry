import requests

BASE_URL = "http://localhost:8001"  # Change this if your app runs on a different host/port

def test_add_cluster():
    response = requests.post(f"{BASE_URL}/cluster/", json={"lat": "48.864716", "lon": "2.349014"})
    assert response.status_code == 200

def test_add_cluster_invalid_input():
    response = requests.post(f"{BASE_URL}/cluster/", json={"lat": "48.864716"})  # Missing lon
    assert response.status_code == 400

def test_list_clusters():
    # Add a cluster to test listing
    response = requests.get(f"{BASE_URL}/clusters/")
    assert response.status_code == 200

def test_delete_cluster():
    # Add a cluster to delete
    response = requests.delete(f"{BASE_URL}/cluster/", json={"lat": "48.864716", "lon": "2.349014"})
    assert response.status_code == 200


def test_delete_nonexistent_cluster():
    response = requests.delete(f"{BASE_URL}/cluster/", json={"lat": "0.0", "lon": "0.0"})
    assert response.status_code == 400
if __name__ == "__main__":
    test_add_cluster()
    test_add_cluster_invalid_input()
    test_list_clusters()
    test_delete_cluster()
    test_delete_nonexistent_cluster()
    print("All tests passed!")
