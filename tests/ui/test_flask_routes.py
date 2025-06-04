import pytest
import json

def test_index_route(client):
    """Test the main dashboard page loads correctly"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Bee Colony Health Monitor' in response.data

def test_get_stats_route(client, reset_stats):
    """Test the /get_stats endpoint returns correct data"""
    # Set some test data
    from app import detection_stats
    detection_stats.update({
        "current_bees": 10,
        "current_varroa": 2,
        "total_bees": 50,
        "total_varroa": 8,
        "infestation_ratio": 0.16,
        "infestation_risk_level": "High",
        "fps": 25.3
    })
    
    # Test the endpoint
    response = client.get('/get_stats')
    assert response.status_code == 200
    
    # Verify response data
    data = json.loads(response.data)
    assert data["current_bees"] == 10
    assert data["current_varroa"] == 2
    assert data["infestation_ratio"] == 0.16
    assert data["infestation_risk_level"] == "High"

def test_get_time_series_route(client, reset_stats):
    """Test the /get_time_series endpoint returns correct data"""
    # Set some test data
    from app import time_series_data
    time_series_data["timestamps"].extend(["12:01", "12:02"])
    time_series_data["bee_counts"].extend([5, 8])
    time_series_data["varroa_counts"].extend([1, 2])
    time_series_data["infestation_ratio"].extend([0.2, 0.25])
    
    # Test the endpoint
    response = client.get('/get_time_series')
    assert response.status_code == 200
    
    # Verify response data
    data = json.loads(response.data)
    assert len(data["timestamps"]) == 2
    assert data["timestamps"] == ["12:01", "12:02"]
    assert data["bee_counts"] == [5, 8]
    assert data["varroa_counts"] == [1, 2]
    assert data["infestation_ratio"] == [0.2, 0.25]

def test_start_stop_detection(client):
    """Test the start and stop detection endpoints"""
    from unittest.mock import patch
    
    # Mock the detection thread to avoid actually starting it
    with patch('app.threading.Thread'):
        # Test start endpoint
        response = client.post('/start_detection')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "started"
        
        # Test stop endpoint
        response = client.post('/stop_detection')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data["status"] == "stopped" 
