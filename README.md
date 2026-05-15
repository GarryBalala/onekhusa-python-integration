# OneKhusa Request to Pay Python Integration Reference

A professional reference implementation of the **OneKhusa Payment Gateway** using **Python 3**, **FastAPI**, and **Socket.io**. This project demonstrates the **Hosted Checkout** flow with real-time webhooks and employs the **Abstract Factory Pattern** for extensible payment provider integration.

## 🚀 Key Features

- **FastAPI Backend**: High-performance, asynchronous Python server.
- **Hosted Checkout**: Seamless redirection logic to OneKhusa's managed payment page.
- **Real-Time Webhooks**: Automated transaction verification using WebSockets (`python-socketio`).
- **Verification Overlay**: A robust frontend strategy to handle asynchronous payment redirects.
- **Abstract Factory Pattern**: Extensible architecture for multiple payment providers.
- **Strict Validation**: Automatic cleaning of references to ensure alphanumeric compatibility.
- **Comprehensive Testing**: Unit tests and integration tests for robust quality assurance.

---

## 📂 Project Structure

```text
onekhusa-python-integration/
├── app/
│   ├── main.py                          # FastAPI Server, Socket.io & Webhook Logic
│   ├── factories/
│   │   ├── __init__.py
│   │   ├── payment_provider_factory.py   # Abstract Factory Pattern Implementation
│   │   └── concrete_providers.py         # Concrete Payment Provider Implementations
│   ├── models/
│   │   ├── __init__.py
│   │   └── payment.py                   # Pydantic Models for Payment Operations
│   ├── services/
│   │   ├── __init__.py
│   │   ├── onekhusa_service.py          # Core OneKhusa API Logic
│   │   └── payment_service.py           # Payment Service Interface
│   └── utils/
│       ├── __init__.py
│       └── validators.py                # Validation Utilities
├── tests/
│   ├── __init__.py
│   ├── test_payment_factory.py          # Factory Pattern Tests
│   ├── test_onekhusa_service.py         # Service Tests
│   └── conftest.py                      # Pytest Fixtures
├── public/
│   └── index.html                       # OneTicket Fintech Dashboard (Frontend)
├── .env.example                         # Example Environment Configuration
├── .gitignore                           # Security: Excludes venv and .env from Git
├── requirements.txt                     # Python Project Dependencies
└── README.md                            # This file
```

---

## 🛠️ Installation

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **NGrok** (for local webhook testing)
- **OneKhusa Merchant Account**
- **Git**

### Step 1: Clone the Repository

```bash
git clone https://github.com/GarryBalala/onekhusa-python-integration.git
cd onekhusa-python-integration
```

### Step 2: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` and fill in your OneKhusa credentials:

```env
# OneKhusa API Credentials
ONEKHUSA_API_KEY=sandbox_vDdLumyfNCWiN...
ONEKHUSA_API_SECRET=_fefXaN9LGorR4uxlnT...
ONEKHUSA_ORG_ID=0BBNREQ33RSX
ONEKHUSA_MERCHANT_NUMBER=79619974
ONEKHUSA_CAPTURED_BY=your_email@example.com

# Webhook Security
ONEKHUSA_WEBHOOK_SECRET=NTEKlKbI7J9tfYwAlyj...

# API Endpoints
ONEKHUSA_BASE_URL=https://api.onekhusa.com/sandbox/v1
ONEKHUSA_CHECKOUT_URL=https://api.onekhusa.com/sandbox/v1/checkout/rtp/initiate

# Public Redirect (Crucial for Webhooks)
# IMPORTANT: Update this with your active NGrok URL every time you restart NGrok
PUBLIC_CALLBACK_URL=https://your-ngrok-id.ngrok-free.dev

# Server Config
PORT=8000
DEBUG=True
```

---

## 📐 Architecture: Abstract Factory Pattern

This project implements the **Abstract Factory Pattern** to provide a flexible and extensible payment provider integration system.

### Pattern Overview

```python
# app/factories/payment_provider_factory.py

from abc import ABC, abstractmethod
from enum import Enum

class PaymentProviderType(Enum):
    ONEKHUSA = "onekhusa"
    STRIPE = "stripe"  # Future implementation
    PAYPAL = "paypal"  # Future implementation

class PaymentProvider(ABC):
    """Abstract base class for all payment providers"""
    
    @abstractmethod
    async def initiate_payment(self, amount: float, reference: str) -> dict:
        """Initiate a payment session"""
        pass
    
    @abstractmethod
    async def verify_payment(self, transaction_id: str) -> dict:
        """Verify payment status"""
        pass
    
    @abstractmethod
    async def process_webhook(self, payload: dict) -> bool:
        """Process webhook from payment provider"""
        pass

class PaymentProviderFactory:
    """Factory for creating payment provider instances"""
    
    _providers = {}
    
    @classmethod
    def register_provider(cls, provider_type: PaymentProviderType, provider_class):
        """Register a new payment provider"""
        cls._providers[provider_type] = provider_class
    
    @classmethod
    def create_provider(cls, provider_type: PaymentProviderType) -> PaymentProvider:
        """Create and return a payment provider instance"""
        provider_class = cls._providers.get(provider_type)
        if not provider_class:
            raise ValueError(f"Unknown payment provider: {provider_type}")
        return provider_class()

# app/factories/concrete_providers.py

class OneKhusaProvider(PaymentProvider):
    """Concrete implementation for OneKhusa payment provider"""
    
    async def initiate_payment(self, amount: float, reference: str) -> dict:
        # OneKhusa specific implementation
        pass
    
    async def verify_payment(self, transaction_id: str) -> dict:
        # OneKhusa specific implementation
        pass
    
    async def process_webhook(self, payload: dict) -> bool:
        # OneKhusa specific implementation
        pass

# Register providers
PaymentProviderFactory.register_provider(
    PaymentProviderType.ONEKHUSA,
    OneKhusaProvider
)
```

---

## 💻 Usage

### Starting the Server

```bash
# Ensure virtual environment is activated
python -m app.main
```

The application will be available at `http://localhost:8000`.

### Using the Payment Factory

```python
from app.factories.payment_provider_factory import PaymentProviderFactory, PaymentProviderType

# Create a OneKhusa payment provider
provider = PaymentProviderFactory.create_provider(PaymentProviderType.ONEKHUSA)

# Initiate a payment
response = await provider.initiate_payment(
    amount=100.00,
    reference="ORD-12345"
)

# Verify payment
verification = await provider.verify_payment(
    transaction_id="TXN-67890"
)
```

### FastAPI Integration Example

```python
# app/main.py

from fastapi import FastAPI
from app.factories.payment_provider_factory import PaymentProviderFactory, PaymentProviderType

app = FastAPI()

@app.post("/api/payments/initiate")
async def initiate_payment(amount: float, reference: str):
    provider = PaymentProviderFactory.create_provider(PaymentProviderType.ONEKHUSA)
    response = await provider.initiate_payment(amount, reference)
    return response

@app.post("/api/webhooks/payments")
async def process_webhook(payload: dict):
    provider = PaymentProviderFactory.create_provider(PaymentProviderType.ONEKHUSA)
    success = await provider.process_webhook(payload)
    return {"success": success}
```

---

## 🧪 Testing

### Prerequisites for Testing

Install test dependencies:

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_payment_factory.py

# Run tests with verbose output
pytest -v

# Run specific test
pytest tests/test_payment_factory.py::test_factory_creates_provider
```

### Test Examples

#### Unit Test: Payment Factory

```python
# tests/test_payment_factory.py

import pytest
from app.factories.payment_provider_factory import (
    PaymentProviderFactory,
    PaymentProviderType,
    OneKhusaProvider
)

@pytest.fixture
def factory():
    return PaymentProviderFactory()

def test_factory_creates_onekhusa_provider():
    """Test that factory creates OneKhusa provider"""
    provider = PaymentProviderFactory.create_provider(PaymentProviderType.ONEKHUSA)
    assert isinstance(provider, OneKhusaProvider)

def test_factory_raises_error_for_unknown_provider():
    """Test that factory raises error for unknown provider"""
    with pytest.raises(ValueError, match="Unknown payment provider"):
        PaymentProviderFactory.create_provider("unknown_provider")

def test_provider_has_required_methods():
    """Test that provider implements all required methods"""
    provider = PaymentProviderFactory.create_provider(PaymentProviderType.ONEKHUSA)
    assert hasattr(provider, 'initiate_payment')
    assert hasattr(provider, 'verify_payment')
    assert hasattr(provider, 'process_webhook')
```

#### Integration Test: Payment Service

```python
# tests/test_onekhusa_service.py

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_initiate_payment_endpoint():
    """Test payment initiation endpoint"""
    response = client.post(
        "/api/payments/initiate",
        json={
            "amount": 100.00,
            "reference": "TEST-ORD-001"
        }
    )
    assert response.status_code == 200
    assert "checkout_url" in response.json()

@pytest.mark.asyncio
async def test_webhook_endpoint():
    """Test webhook processing endpoint"""
    webhook_payload = {
        "transaction_id": "TXN-001",
        "status": "SUCCESS",
        "amount": 100.00
    }
    response = client.post(
        "/api/webhooks/payments",
        json=webhook_payload
    )
    assert response.status_code == 200
    assert response.json()["success"] is True
```

### Pytest Configuration

```python
# tests/conftest.py

import pytest
from unittest.mock import AsyncMock, patch
import os

@pytest.fixture(autouse=True)
def setup_env():
    """Setup test environment variables"""
    os.environ['ONEKHUSA_API_KEY'] = 'test_key'
    os.environ['ONEKHUSA_API_SECRET'] = 'test_secret'
    os.environ['ONEKHUSA_ORG_ID'] = 'test_org'

@pytest.fixture
def mock_onekhusa_response():
    """Mock OneKhusa API response"""
    return {
        "checkout_url": "https://api.onekhusa.com/checkout/abc123",
        "session_id": "sess_123",
        "reference": "ORD-001"
    }

@pytest.fixture
def async_mock():
    """Create async mock objects"""
    return AsyncMock()
```

### Running Tests with Coverage

```bash
# Generate coverage report
pytest --cov=app --cov-report=html tests/

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

---

## 📡 Webhook Setup & Testing

### Configure NGrok for Local Webhook Testing

```bash
# Start NGrok
ngrok http 8000

# Copy the generated HTTPS URL and update .env
# Example: https://abc-def-ghi.ngrok-free.dev
PUBLIC_CALLBACK_URL=https://your-ngrok-id.ngrok-free.dev
```

### Register Webhook with OneKhusa

1. Log in to OneKhusa Merchant Portal
2. Navigate to **Developers > Webhooks**
3. Register the callback URL:
   ```
   https://your-ngrok-id.ngrok-free.dev/api/webhooks/payments
   ```

### Test Webhook Locally

```bash
# Use curl to simulate webhook
curl -X POST http://localhost:8000/api/webhooks/payments \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN-12345",
    "status": "SUCCESS",
    "amount": 100.00,
    "reference": "ORD-001"
  }'
```

---

## 🔄 Payment Flow Diagram

```
┌──────────────┐
│   User       │
└──────────────┘
      │
      │ 1. Click "Purchase"
      ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  (Factory Pattern)       │
└──────────────────────────┘
      │
      │ 2. initiate_payment()
      ▼
┌──────────────────────────┐
│  OneKhusa Payment API    │
│  (Hosted Checkout)       │
└──────────────────────────┘
      │
      │ 3. Redirect to Checkout
      ▼
┌──────────────────────────┐
│  OneKhusa Checkout Page  │
│  (Payment Processing)    │
└──────────────────────────┘
      │
      │ 4. Complete Payment
      ▼
┌──────────────────────────┐
│  OneKhusa Webhook        │
│  (async notification)    │
└──────────────────────────┘
      │
      │ 5. POST /webhooks/payments
      ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  (process_webhook)       │
└──────────────────────────┘
      │
      │ 6. Socket.io Event
      ▼
┌──────────────────────────┐
│  Frontend Dashboard      │
│  (Update UI)             │
└──────────────────────────┘
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Run tests to ensure they pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 📞 Support

For issues and questions:
- **GitHub Issues**: [Create an issue](https://github.com/GarryBalala/onekhusa-python-integration/issues)
- **OneKhusa Documentation**: [https://docs.onekhusa.com](https://docs.onekhusa.com)

---

## 🙏 Acknowledgments

- OneKhusa for providing excellent payment gateway APIs
- FastAPI for the amazing async framework
- Socket.io for real-time communication capabilities
