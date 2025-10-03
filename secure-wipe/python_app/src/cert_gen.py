import json
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import qrcode
from io import BytesIO
from .utils import load_config

class CertificateGenerator:
    def __init__(self):
        config = load_config()
        private_path = config['keys']['private_path']
        public_path = config['keys']['public_path']
        with open(private_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None
            )
        with open(public_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(f.read())

    def generate_data(self, device_id, wipe_method, timestamp=None):
        if timestamp is None:
            timestamp = datetime.now()
        data = {
            'app': 'Secure Wipe',
            'device_id': device_id,
            'method': wipe_method,
            'timestamp': timestamp.isoformat(),
            'status': 'Completed'
        }
        return data

    def sign_data(self, data):
        json_str = json.dumps(data, sort_keys=True)
        signature = self.private_key.sign(
            json_str.encode(), ec.ECDSA(hashes.SHA256())
        )
        return json_str, signature

    def generate_pdf(self, data, filename='cert.pdf'):
        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(100, 750, f"Secure Wipe Certificate")
        c.drawString(100, 700, f"Device: {data['device_id']}")
        c.drawString(100, 650, f"Method: {data['method']}")
        c.drawString(100, 600, f"Date: {data['timestamp']}")
        c.drawString(100, 550, f"Status: {data['status']}")
        c.save()

    def generate_qr(self, data_json, filename='cert.qr.png'):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(data_json)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(filename)

    def verify_signature(self, json_str, signature):
        try:
            self.public_key.verify(
                signature, json_str.encode(), ec.ECDSA(hashes.SHA256())
            )
            return True
        except InvalidSignature:
            return False

    def generate_full_cert(self, device_id, wipe_method, output_dir='.'):
        data = self.generate_data(device_id, wipe_method)
        json_str, sig = self.sign_data(data)
        pdf_file = f"{output_dir}/{device_id}_cert.pdf"
        qr_file = f"{output_dir}/{device_id}_qr.png"
        json_file = f"{output_dir}/{device_id}_cert.json"
        self.generate_pdf(data, pdf_file)
        self.generate_qr(json_str, qr_file)
        with open(json_file, 'w') as f:
            json.dump({'data': json_str, 'signature': sig.hex()}, f)
        return {'pdf': pdf_file, 'qr': qr_file, 'json': json_file, 'valid': True}

# Example usage (for testing; run python cert_gen.py)
if __name__ == "__main__":
    gen = CertificateGenerator()
    data = gen.generate_data("test_device", "DoD 3-Pass")
    json_str, sig = gen.sign_data(data)
    gen.generate_pdf(data)
    gen.generate_qr(json_str)
    print("Signature valid:", gen.verify_signature(json_str, sig))