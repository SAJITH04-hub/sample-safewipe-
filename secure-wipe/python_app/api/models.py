from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class WipeRequest(BaseModel):
    devices: List[str]
    passes: Optional[int] = 3
    method: Optional[str] = "DoD 3-Pass"

class CertData(BaseModel):
    device_id: str
    method: str
    timestamp: datetime
    status: str = "Completed"

class CertVerifyRequest(BaseModel):
    json_data: str
    signature_hex: str

class WipeResponse(BaseModel):
    status: str
    wiped_devices: List[str]
    cert_files: Optional[List[str]] = None