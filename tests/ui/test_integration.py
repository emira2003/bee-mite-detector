import pytest
import json
import time
from unittest.mock import patch, MagicMock

def test_detection_workflow_integration(client, reset_stats):
    """Test the complete detection workflow from start to data visualization"""
    from app import detection_stats, time_series_data
    
    # Mock the subprocess.Popen to avoid starting real detection
    mock_process = MagicMock()
    mock_process.stdout.readline.return_value = "Frame count: 1\n"
    mock_process.poll.return_value = None
    
    with patch('app.subprocess.Popen', return_value=mock_process):
        # 1. Start detection
        response = client.post('/start_detection')
        assert response.status_code == 200
        start_data = json.loads(response.data)
        assert start_data["status"] == "started"
        
        # 2. Simulate detection updates
        detection_stats.update({
            "current_bees": 15,
            "current_varroa": 3,
            "total_bees": 15,
            "total_varroa": 3,
            "infestation_ratio": 0.2,
            "infestation_risk_level": "High"
        })
        
        time_series_data["timestamps"].append("12:00:00")
        time_series_data["bee_counts"].append(15)
        time_series_data["varroa_counts"].append(3)
        time_series_data["infestation_ratio"].append(0.2)
        
        # 3. Verify stats are updated
        stats_response = client.get('/get_stats')
        assert stats_response.status_code == 200
        stats_data = json.loads(stats_response.data)
        assert stats_data["current_bees"] == 15
        assert stats_data["infestation_risk_level"] == "High"
        
        # 4. Verify time series data
        ts_response = client.get('/get_time_series')
        assert ts_response.status_code == 200
        ts_data = json.loads(ts_response.data)
        assert len(ts_data["timestamps"]) == 1
        assert ts_data["bee_counts"][0] == 15
        
        # 5. Stop detection
        stop_response = client.post('/stop_detection')
        assert stop_response.status_code == 200
        stop_data = json.loads(stop_response.data)
        assert stop_data["status"] == "stopped" 
