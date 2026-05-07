import os
import requests
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OneKhusaService:
    def __init__(self):
        self.api_key = os.getenv("ONEKHUSA_API_KEY")
        self.api_secret = os.getenv("ONEKHUSA_API_SECRET")
        self.org_id = os.getenv("ONEKHUSA_ORG_ID")
        self.merchant_no = int(os.getenv("ONEKHUSA_MERCHANT_NUMBER", 0))
        self.checkout_url = os.getenv("ONEKHUSA_CHECKOUT_URL")
        self.callback_base = os.getenv("PUBLIC_CALLBACK_URL")

    def initiate_hosted_checkout(self, amount: float, reference: str, description: str):
        payload = {
            "authentication": {
                "apiKey": self.api_key,
                "apiSecret": self.api_secret  
            },
            "merchant": {
                "organisationId": self.org_id,
                "merchantAccountNumber": self.merchant_no
            },
            "payment": {
                "sourceReferenceNumber": reference,
                "description": description,
                "amount": amount
            },
            "route": {
                "successRedirectionUrl": f"{self.callback_base}/?ref={reference}",
                "failureRedirectionUrl": f"{self.callback_base}/?ref={reference}",
                "callbackApiUrl": f"{self.callback_base}/webhooks/payments"
            }
        }
        
        # Ensure the reference is strictly alphanumeric and max 12 chars for sandbox stability
        safe_ref = "".join(filter(str.isalnum, reference))[:12]
        payload["payment"]["sourceReferenceNumber"] = safe_ref
        payload["route"]["successRedirectionUrl"] = f"{self.callback_base}/?ref={safe_ref}"
        payload["route"]["failureRedirectionUrl"] = f"{self.callback_base}/?ref={safe_ref}"

        idempotency_key = f"PY-CHK-{safe_ref}-{str(uuid.uuid4())[:8]}"

        headers = {
            "Content-Type": "application/json",
            "X-Idempotency-Key": idempotency_key
        }

        try:
            response = requests.post(self.checkout_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if e.response is not None:
                print(f"OneKhusa API Error: {e.response.json()}")
            raise e
# Instantiate the service for use in main.py
onekhusa_service = OneKhusaService()
