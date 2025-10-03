import pytest
from flask.testing import FlaskClient
from api.app import app
from unittest.mock import patch, MagicMock
import secure_wipe_engine as engine

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('api.routes.gen.generate_full_cert')
@patch('api.routes.engine.wipe_device')
@patch('api.routes.engine.handle_hpa_dco')
def test_wipe_endpoint(mock_hpa, mock_wipe, mock_cert, client):
    response = client.post('/api/v1/wipe', json={
        'devices': ['/dev/sda'],
        'passes': 1,
        'method': 'DoD 1-Pass'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['wiped_devices']) == 1
    mock_wipe.assert_called_once()
    mock_hpa.assert_called_once()
    mock_cert.assert_called_once()

def test_verify_cert_valid(client):
    # Mock public key and verify
    with patch('api.routes.serialization.load_pem_public_key') as mock_load, \
         patch('api.routes.ec.ECDSA') as mock_ecdsa:
        mock_key = MagicMock()
        mock_load.return_value = mock_key
        mock_verify = MagicMock()
        mock_key.verify = mock_verify
        mock_verify.side_effect = None  # Valid
        response = client.post('/api/v1/verify_cert', json={
            'json_data': '{"test": "data"}',
            'signature_hex': 'deadbeef'
        })
        assert response.status_code == 200
        data = response.get_json()
        assert data['valid'] == True

def test_logs_endpoint(client):
    response = client.get('/api/v1/logs')
    assert response.status_code == 200
    data = response.get_json()
    assert 'logs' in data
    assert len(data['logs']) > 0

def test_404(client):
    response = client.get('/nonexistent')
    assert response.status_code == 404