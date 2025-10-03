import pytest
from src.cert_gen import CertificateGenerator
from src.gen_keys import private_key  # Import for test keys (or generate temp)
import tempfile
import os
import json

@pytest.fixture
def temp_gen():
    # Generate temp keys for isolated test
    from cryptography.hazmat.primitives import serialization
    private_key_temp = ec.generate_private_key(ec.SECP384R1(), default_backend())
    private_pem = private_key_temp.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    public_key_temp = private_key_temp.public_key()
    public_pem = public_key_temp.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with tempfile.NamedTemporaryFile(suffix='.pem', delete=False) as priv_f, \
         tempfile.NamedTemporaryFile(suffix='.pem', delete=False) as pub_f:
        priv_f.write(private_pem)
        pub_f.write(public_pem)
        priv_path, pub_path = priv_f.name, pub_f.name
    gen = CertificateGenerator()  # Will use temp paths (override in init for test)
    gen.private_key = private_key_temp
    gen.public_key = public_key_temp
    yield gen
    os.unlink(priv_path)
    os.unlink(pub_path)

def test_generate_data(temp_gen):
    data = temp_gen.generate_data("test_device", "DoD 3-Pass")
    assert data['device_id'] == "test_device"
    assert data['method'] == "DoD 3-Pass"
    assert 'timestamp' in data
    assert data['status'] == 'Completed'

def test_sign_and_verify(temp_gen):
    data = temp_gen.generate_data("test_device", "DoD 3-Pass")
    json_str, sig = temp_gen.sign_data(data)
    assert temp_gen.verify_signature(json_str, sig) == True
    # Tamper test
    tampered = json_str + "tampered"
    assert temp_gen.verify_signature(tampered, sig) == False

def test_generate_full_cert(temp_gen):
    with tempfile.TemporaryDirectory() as tmpdir:
        cert_files = temp_gen.generate_full_cert("test_device", "DoD 3-Pass", tmpdir)
        assert 'pdf' in cert_files
        assert 'qr' in cert_files
        assert 'json' in cert_files
        assert os.path.exists(cert_files['pdf'])
        assert os.path.exists(cert_files['qr'])
        assert os.path.exists(cert_files['json'])
        # Verify JSON
        with open(cert_files['json'], 'r') as f:
            cert_json = json.load(f)
        assert 'data' in cert_json
        assert 'signature' in cert_json