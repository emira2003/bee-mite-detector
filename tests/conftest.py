import pytest
from app import app, detection_stats, time_series_data

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def reset_stats():
    """Reset detection stats to initial values"""
    # Store original values
    original_stats = detection_stats.copy()
    original_series = {
        "timestamps": list(time_series_data["timestamps"]),
        "bee_counts": list(time_series_data["bee_counts"]),
        "varroa_counts": list(time_series_data["varroa_counts"]),
        "infestation_ratio": list(time_series_data["infestation_ratio"])
    }
    
    # Reset for test
    detection_stats.update({
        "total_frames": 0,
        "total_bees": 0,
        "total_varroa": 0,
        "unique_bees": 0,
        "unique_varroa": 0,
        "current_bees": 0,
        "current_varroa": 0,
        "fps": 0,
        "infestation_ratio": 0,
        "infestation_risk_level": "Unknown"
    })
    
    time_series_data["timestamps"].clear()
    time_series_data["bee_counts"].clear()
    time_series_data["varroa_counts"].clear()
    time_series_data["infestation_ratio"].clear()
    
    yield
    
    # Restore original values after test
    detection_stats.update(original_stats)
    time_series_data["timestamps"].extend(original_series["timestamps"])
    time_series_data["bee_counts"].extend(original_series["bee_counts"])
    time_series_data["varroa_counts"].extend(original_series["varroa_counts"])
    time_series_data["infestation_ratio"].extend(original_series["infestation_ratio"]) 
