import os
import jwt
import hmac
import hashlib
import logging
from typing import Dict, Any

logger = logging.getLogger("hyper.hsm")

class MockCloudHSM:
    """
    Hardware Security Module (HSM) Abstraction Layer.
    In a true hyperscaler environment, this calls AWS KMS or Azure Key Vault APIs.
    The primary goal is that private keys NEVER exist as strings in application memory.
    """
    
    def __init__(self):
        # Simulated environment variables representing ARNs, not raw keys
        self.jwt_key_arn = os.getenv("KMS_JWT_KEY_ARN", "arn:aws:kms:us-east-1:12345:key/mock-jwt-key")
        self.stripe_wh_key_arn = os.getenv("KMS_STRIPE_WH_ARN", "arn:aws:kms:us-east-1:12345:key/mock-stripe-wh")
        
        # Internal mock storage to simulate the HSM boundary (Inaccessible from outside this class)
        self._mock_secure_enclave = {
            self.jwt_key_arn: b"super_secret_hardware_jwt_key_999",
            self.stripe_wh_key_arn: b"whsec_hardware_stripe_key_888"
        }

    def sign_jwt(self, payload: Dict[str, Any]) -> str:
        """Asks the HSM to sign the JWT payload."""
        logger.debug(f"Offloading cryptographic signing to HSM for KMS Key: {self.jwt_key_arn}")
        # Real world: client.sign(KeyId=self.jwt_key_arn, Message=payload, SigningAlgorithm="RSASSA_PKCS1_V1_5_SHA_256")
        return jwt.encode(payload, self._mock_secure_enclave[self.jwt_key_arn].decode(), algorithm="HS256")

    def verify_jwt(self, encoded_token: str) -> Dict[str, Any]:
        """Asks the HSM to verify the JWT signature."""
        try:
            return jwt.decode(encoded_token, self._mock_secure_enclave[self.jwt_key_arn].decode(), algorithms=["HS256"])
        except jwt.InvalidTokenError as e:
            return {"error": str(e)}

    def verify_stripe_webhook_signature(self, payload_body: bytes, sig_header: str) -> bool:
        """Asks the HSM to verify a cryptographic webhook hash."""
        logger.debug("Verifying webhook signature within Hardware Security Module.")
        try:
            # Typical Stripe logic expects timestamp and signatures
            parts = sig_header.split(",")
            t = parts[0].split("=")[1]
            v1 = parts[1].split("=")[1]
            
            signed_payload = f"{t}.".encode("utf-8") + payload_body
            
            # The actual cryptographic operation happens "inside the HSM"
            key = self._mock_secure_enclave[self.stripe_wh_key_arn]
            expected_sig = hmac.new(key, signed_payload, hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(expected_sig, v1)
        except Exception:
            return False

# Global HSM instance
cloud_hsm = MockCloudHSM()
