from flask import Blueprint, request, jsonify
from pydantic import ValidationError
import secure_wipe_engine as engine
from ..src.cert_gen import CertificateGenerator
from ..src.utils import log_message, parse_device_path
from .models import WipeRequest, CertVerifyRequest
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.exceptions import InvalidSignature

bp = Blueprint('routes', __name__)
gen = CertificateGenerator()

@bp.route('/wipe', methods=['POST'])
def wipe_devices():
    try:
        data = WipeRequest(**request.json)
        wiped = []
        certs = []
        for device in data.devices:
            parsed = parse_device_path(device)
            engine.wipe_device(parsed, data.passes)
            engine.handle_hpa_dco(parsed)
            wiped.append(parsed)
            cert_files = gen.generate_full_cert(device, data.method)
            certs.extend(list(cert_files.values()))
        log_message('INFO', f'Bulk wipe completed: {wiped}')
        return jsonify({
            'status': 'success',
            'wiped_devices': wiped,
            'cert_files': certs
        })
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        log_message('ERROR', f'Wipe failed: {e}')
        return jsonify({'error': str(e)}), 500

@bp.route('/logs', methods=['GET'])
def get_logs():
    # Placeholder: In production, read from file/DB
    logs = [
        {'timestamp': '2023-10-01T12:00:00', 'level': 'INFO', 'message': 'App started'},
        {'timestamp': '2023-10-01T12:05:00', 'level': 'INFO', 'message': 'Wipe completed on /dev/sda'}
    ]
    return jsonify({'logs': logs})

@bp.route('/verify_cert', methods=['POST'])
def verify_cert():
    try:
        data = CertVerifyRequest(**request.json)
        # Load public key (assume from config or upload)
        from ..src.utils import load_config
        config = load_config()
        with open(config['keys']['public_path'], 'rb') as f:
            public_key = serialization.load_pem_public_key(f.read())
        signature = bytes.fromhex(data.signature_hex)
        is_valid = public_key.verify(
            signature, data.json_data.encode(), ec.ECDSA(hashes.SHA256())
        )
        return jsonify({'valid': is_valid, 'message': 'Verified' if is_valid else 'Tampered'})
    except InvalidSignature:
        return jsonify({'valid': False, 'message': 'Invalid signature'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404