import requests

# Define the base URL of the API
BASE_URL = "http://127.0.0.1:8000"

# Test data for adding a cluster
test_cluster = {"domain": "UMU", "cluster": "UMU", "node_ip": "10.208.99.106"}

def test_add_cluster():
    response = requests.post(f"{BASE_URL}/cluster/", json=test_cluster)
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

def test_list_clusters_after_add():
    response = requests.get(f"{BASE_URL}/clusters/")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

def test_delete_cluster():
    response = requests.delete(f"{BASE_URL}/cluster/", params={"ip": "10.208.99.106"})
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"

def test_list_clusters_after_delete():
    response = requests.get(f"{BASE_URL}/clusters/")
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    clusters = response.json()
    assert not any(
        cluster["domain"] == test_cluster["domain"] and 
        cluster["cluster"] == test_cluster["cluster"] and 
        cluster["node_ip"] == test_cluster["node_ip"]
        for cluster in clusters
    ), "Deleted cluster still found in the list"

if __name__ == "__main__":
    # Run the tests
    test_add_cluster()
    test_list_clusters_after_add()
    test_delete_cluster()
    test_list_clusters_after_delete()

    print("All tests passed successfully!")
