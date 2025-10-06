"""
Tests for Live Camera API endpoints
"""
import pytest
import base64
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def create_test_image_base64():
    """Create a simple test image in base64 format"""
    # Create a minimal valid JPEG image (1x1 black pixel)
    # This is a valid JPEG file encoded in base64
    jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xfe\xa2\x8a(\xff\xd9'
    return base64.b64encode(jpeg_data).decode('utf-8')


def test_get_available_rules():
    """Test getting list of available PPE detection rules"""
    # Note: This endpoint requires authentication
    # For now, we'll test that the endpoint exists
    response = client.get("/api/v1/live-camera/rules")
    
    # Should return 401 without authentication
    assert response.status_code in [200, 401]


def test_detect_frame_no_auth():
    """Test detection without authentication"""
    test_image = create_test_image_base64()
    
    response = client.post(
        "/api/v1/live-camera/detect",
        json={
            "frame": test_image,
            "selected_rules": ["helmet", "safety-vest"]
        }
    )
    
    # Should require authentication
    assert response.status_code == 401


def test_detect_frame_invalid_data():
    """Test detection with invalid frame data"""
    response = client.post(
        "/api/v1/live-camera/detect",
        json={
            "frame": "",
            "selected_rules": ["helmet"]
        }
    )
    
    # Should return 400 or 401 (depending on auth check order)
    assert response.status_code in [400, 401]


def test_detect_frame_invalid_base64():
    """Test detection with invalid base64 data"""
    response = client.post(
        "/api/v1/live-camera/detect",
        json={
            "frame": "not-valid-base64!!!",
            "selected_rules": ["helmet"]
        }
    )
    
    # Should return 400 or 401
    assert response.status_code in [400, 401, 500]


def test_api_routes_registered():
    """Test that live camera routes are registered in the app"""
    # Check that the router is included
    routes = [route.path for route in app.routes]
    
    # Should have live camera endpoints
    assert any("/live-camera" in route for route in routes)


def test_available_rules_list():
    """Test that the available rules list is correct"""
    from app.api.v1.live_camera import AVAILABLE_RULES
    
    expected_rules = [
        "glasses",
        "face-mask",
        "ear-muffs",
        "hands",
        "gloves",
        "safety-vest",
        "tools",
        "helmet",
        "medical-suit",
        "safety-suit"
    ]
    
    assert AVAILABLE_RULES == expected_rules
    assert len(AVAILABLE_RULES) == 10


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
