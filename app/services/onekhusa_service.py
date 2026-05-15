import os
import requests
import uuid
from dotenv import load_dotenv
from dataclasses import dataclass

# Load environment variables
load_dotenv()


@dataclass
class AuthenticationConfig:
    """Authentication credentials for OneKhusa API"""
    api_key: str
    api_secret: str

    def to_dict(self):
        return {
            "apiKey": self.api_key,
            "apiSecret": self.api_secret
        }


@dataclass
class MerchantConfig:
    """Merchant account details"""
    organisation_id: str
    merchant_account_number: int

    def to_dict(self):
        return {
            "organisationId": self.organisation_id,
            "merchantAccountNumber": self.merchant_account_number
        }


@dataclass
class PaymentDetails:
    """Payment transaction details"""
    source_reference_number: str
    description: str
    amount: float

    def to_dict(self):
        return {
            "sourceReferenceNumber": self.source_reference_number,
            "description": self.description,
            "amount": self.amount
        }


@dataclass
class RouteConfig:
    """Redirect and callback URLs"""
    success_redirection_url: str
    failure_redirection_url: str
    callback_api_url: str

    def to_dict(self):
        return {
            "successRedirectionUrl": self.success_redirection_url,
            "failureRedirectionUrl": self.failure_redirection_url,
            "callbackApiUrl": self.callback_api_url
        }


class CheckoutPayload:
    """Builder for OneKhusa checkout API payload"""
    def __init__(self, auth: AuthenticationConfig, merchant: MerchantConfig,
                 payment: PaymentDetails, route: RouteConfig):
        self.authentication = auth
        self.merchant = merchant
        self.payment = payment
        self.route = route

    def build(self):
        """Construct the complete payload dictionary"""
        return {
            "authentication": self.authentication.to_dict(),
            "merchant": self.merchant.to_dict(),
            "payment": self.payment.to_dict(),
            "route": self.route.to_dict()
        }


class OneKhusaService:
    def __init__(self):
        self.api_key = os.getenv("ONEKHUSA_API_KEY")
        self.api_secret = os.getenv("ONEKHUSA_API_SECRET")
        self.org_id = os.getenv("ONEKHUSA_ORG_ID")
        self.merchant_no = int(os.getenv("ONEKHUSA_MERCHANT_NUMBER", 0))
        self.checkout_url = os.getenv("ONEKHUSA_CHECKOUT_URL")
        self.callback_base = os.getenv("PUBLIC_CALLBACK_URL")

    @staticmethod
    def _sanitize_reference(reference: str, max_length: int = 12) -> str:
        """Ensure reference is strictly alphanumeric and within max length"""
        return "".join(filter(str.isalnum, reference))[:max_length]

    def _build_checkout_payload(self, amount: float, reference: str, description: str) -> dict:
        """Build structured checkout payload using object-oriented components"""
        safe_ref = self._sanitize_reference(reference)

        # Create configuration objects
        auth = AuthenticationConfig(
            api_key=self.api_key,
            api_secret=self.api_secret
        )

        merchant = MerchantConfig(
            organisation_id=self.org_id,
            merchant_account_number=self.merchant_no
        )

        payment = PaymentDetails(
            source_reference_number=safe_ref,
            description=description,
            amount=amount
        )

        route = RouteConfig(
            success_redirection_url=f"{self.callback_base}/?ref={safe_ref}",
            failure_redirection_url=f"{self.callback_base}/?ref={safe_ref}",
            callback_api_url=f"{self.callback_base}/webhooks/payments"
        )

        # Build and return payload
        payload_builder = CheckoutPayload(auth, merchant, payment, route)
        return payload_builder.build()

    def initiate_hosted_checkout(self, amount: float, reference: str, description: str):
        """Initiate a hosted checkout session"""
        payload = self._build_checkout_payload(amount, reference, description)
        
        safe_ref = self._sanitize_reference(reference)
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
