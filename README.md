# OneKhusa Request to Pay Python Integration

A professional reference implementation of the **OneKhusa Payment Gateway** using **Python 3**, **FastAPI**, and **Socket.io**. This project demonstrates the **Hosted Checkout** flow with real-time webhook notifications and frontend verification overlay.

## 🚀 Key Features

- **FastAPI Backend**: High-performance, asynchronous Python server
- **Hosted Checkout**: Seamless redirection to OneKhusa's managed payment page
- **Real-Time Webhooks**: Automated transaction verification using WebSockets (`python-socketio`)
- **Verification Overlay**: Frontend verification strategy for asynchronous payment redirects
- **Payment Status Tracking**: In-memory transaction tracking with polling fallback
- **Structured Configuration**: Clean separation of authentication, merchant, payment, and route configs
- **Reference Sanitization**: Automatic alphanumeric reference cleaning for API compatibility

---

## 📂 Project Structure

```text
onekhusa-python-integration/
├── app/
│   ├── main.py                          # FastAPI server with Socket.io & webhook handling
│   ├── services/
│   │   └── onekhusa_service.py          # OneKhusa API integration service
│   └── README.md                        # App-specific documentation
├── public/
│   └── index.html                       # Frontend dashboard (Tailwind + Socket.io client)
├── .env                                 # Configuration & API credentials (not in repo)
├── .env.example                         # Example environment variables (optional)
├── .gitignore                           # Git configuration
├── requirements.txt                     # Python dependencies
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

Create a `.env` file in the root directory with your OneKhusa credentials:

```env
# OneKhusa API Credentials
ONEKHUSA_API_KEY=sandbox_vDdLumyfNCWiN...
ONEKHUSA_API_SECRET=_fefXaN9LGorR4uxlnT...
ONEKHUSA_ORG_ID=0BBNREQ33RSX
ONEKHUSA_MERCHANT_NUMBER=79619974
ONEKHUSA_CAPTURED_BY=your_email@example.com

# API Endpoints
ONEKHUSA_CHECKOUT_URL=https://api.onekhusa.com/sandbox/v1/checkout/rtp/initiate

# Public Redirect (Crucial for Webhooks)
# IMPORTANT: Update this with your active NGrok URL every time you restart NGrok
PUBLIC_CALLBACK_URL=https://your-ngrok-id.ngrok-free.dev

# Server Config
PORT=8000
DEBUG=True
```

---

## 💻 Usage

### Starting the Server

```bash
# Ensure virtual environment is activated
python -m app.main
```

The application will be available at `http://localhost:8000`.

### Application Flow

1. **User Interaction**: User clicks "PURCHASE TICKET" on the dashboard
2. **Backend Initiation**: FastAPI calls `/api/Tickets/buy/{event_id}` endpoint
3. **Payment Session**: `OneKhusaService` initiates a hosted checkout session
4. **Redirection**: User is redirected to OneKhusa Hosted Checkout page
5. **Payment Completion**: User completes payment in OneKhusa sandbox
6. **Webhook Callback**: OneKhusa sends webhook to `/webhooks/payments`
7. **Real-Time Update**: Socket.io emits event to frontend, updating payment status
8. **Verification**: Frontend displays success overlay with animated confirmation
9. **Dashboard Return**: User returns to main dashboard after verification

---

## 📡 Webhook Setup & Testing

### Configure NGrok for Local Webhook Testing

```bash
# Start NGrok on port 8000
ngrok http 8000

# Copy the generated HTTPS URL (e.g., https://abc-def-ghi.ngrok-free.dev)
# Update PUBLIC_CALLBACK_URL in your .env file
```

### Register Webhook with OneKhusa

1. Log in to **OneKhusa Merchant Portal**
2. Navigate to **Developers > Webhooks**
3. Register the callback URL:
   ```
   https://your-ngrok-id.ngrok-free.dev/webhooks/payments
   ```

### Test Webhook Locally

```bash
# Simulate a webhook from OneKhusa
curl -X POST http://localhost:8000/webhooks/payments \
  -H "Content-Type: application/json" \
  -d '{
    "metaData": {
      "ReferenceNumber": "OTPY12345678"
    },
    "responseCode": "S100",
    "transactionStatusCode": "S"
  }'
```

---

## 🔄 API Endpoints

### POST `/api/Tickets/buy/{event_id}`

Initiates a OneKhusa hosted checkout session.

**Response:**
```json
{
  "status": "success",
  "redirectUrl": "https://checkout.onekhusa.com/requestToPay/initiate?ptid=...",
  "reference": "OTPY12345678"
}
```

### GET `/api/Tickets/status/{reference}`

Polls the payment status (fallback mechanism).

**Response:**
```json
{
  "status": "Paid" | "Pending" | "NotFound"
}
```

### POST `/webhooks/payments`

Receives webhook notifications from OneKhusa.

**Expected Response:** `acknowledged` (plain text)

---

## 🏗️ Architecture Overview

### Service Layer: `OneKhusaService`

Handles all OneKhusa API interactions using structured configuration objects:

```python
# app/services/onekhusa_service.py

class OneKhusaService:
    def __init__(self):
        # Load credentials from environment
        self.api_key = os.getenv("ONEKHUSA_API_KEY")
        self.api_secret = os.getenv("ONEKHUSA_API_SECRET")
        # ...
    
    def initiate_hosted_checkout(self, amount: float, reference: str, description: str):
        # Build payload with sanitized reference
        # Send request to OneKhusa API
        # Return response with payment transaction ID
```

**Configuration Objects:**
- `AuthenticationConfig`: API credentials
- `MerchantConfig`: Organization and merchant account details
- `PaymentDetails`: Amount, description, reference
- `RouteConfig`: Success/failure URLs and callback endpoint
- `CheckoutPayload`: Builder pattern for constructing complete payload

### FastAPI Backend: `app.main`

Handles HTTP requests, WebSocket connections, and webhook processing:

```python
@app.post("/api/Tickets/buy/{event_id}")
async def buy_ticket(event_id: str):
    # Generate reference
    # Initiate checkout via OneKhusaService
    # Track payment in ticket_tracker
    # Return checkout redirect URL

@app.post("/webhooks/payments")
async def handle_webhook(request: Request):
    # Receive webhook from OneKhusa
    # Extract reference and status
    # Update ticket_tracker
    # Emit Socket.io event to connected clients
    # Return "acknowledged"
```

### Frontend: `public/index.html`

Interactive dashboard built with **Tailwind CSS** and **Socket.io client**:

- **Purchase View**: Displays ticket price and purchase button
- **Verification Overlay**: Shows animated loader while waiting for payment confirmation
- **Success View**: Celebrates successful payment with option to buy another ticket
- **Real-Time Updates**: Listens for Socket.io webhook events
- **Polling Fallback**: Polls `/api/Tickets/status/{ref}` every 3 seconds as fallback

---

## 📊 Payment Flow Diagram

```
┌──────────────┐
│   User       │
└──────────────┘
      │
      │ 1. Click "PURCHASE TICKET"
      ▼
┌──────────────────────────┐
│  Frontend Dashboard      │
│  (index.html)            │
└──────────────────────────┘
      │
      │ 2. POST /api/Tickets/buy/showcase
      ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  (app.main)              │
└──────────────────────────┘
      │
      │ 3. initiate_hosted_checkout()
      ▼
┌──────────────────────────┐
│  OneKhusa Service        │
│  (onekhusa_service.py)   │
└──────────────────────────┘
      │
      │ 4. HTTP POST to OneKhusa API
      ▼
┌──────────────────────────┐
│  OneKhusa Payment API    │
│  (Hosted Checkout)       │
└──────────────────────────┘
      │
      │ 5. Return checkout URL
      ▼
┌──────────────────────────┐
│  Frontend Dashboard      │
│  (Redirect to checkout)  │
└──────────────────────────┘
      │
      │ 6. Redirect to OneKhusa Checkout
      ▼
┌──────────────────────────┐
│  OneKhusa Checkout Page  │
│  (Payment Processing)    │
└──────────────────────────┘
      │
      │ 7. Complete Payment (via TAN)
      ▼
┌──────────────────────────┐
│  OneKhusa Servers        │
│  (Process & Verify)      │
└──────────────────────────┘
      │
      │ 8. Async Webhook
      ▼
┌──────────────────────────┐
│  FastAPI Backend         │
│  POST /webhooks/payments │
└──────────────────────────┘
      │
      │ 9. Process webhook
      │    Update ticket_tracker
      │    Emit Socket.io event
      ▼
┌──────────────────────────┐
│  Frontend Dashboard      │
│  (Socket.io listener)    │
└──────────────────────────┘
      │
      │ 10. Show Success Screen
      ▼
┌──────────────────────────┐
│  Success View            │
│  "Payment Confirmed!"    │
└──────────────────────────┘
```

---

## 🔧 Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `ONEKHUSA_API_KEY` | Your OneKhusa API key | `sandbox_vDdLumyfNCWiN...` |
| `ONEKHUSA_API_SECRET` | Your OneKhusa API secret | `_fefXaN9LGorR4uxlnT...` |
| `ONEKHUSA_ORG_ID` | Organization ID from OneKhusa | `0BBNREQ33RSX` |
| `ONEKHUSA_MERCHANT_NUMBER` | Merchant account number | `79619974` |
| `ONEKHUSA_CHECKOUT_URL` | OneKhusa checkout endpoint | `https://api.onekhusa.com/sandbox/v1/checkout/rtp/initiate` |
| `PUBLIC_CALLBACK_URL` | Your public callback URL (NGrok) | `https://abc-def-ghi.ngrok-free.dev` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `True` or `False` |

---

## 📦 Dependencies

All dependencies are listed in `requirements.txt`:

- **fastapi** (0.136.1): Web framework
- **uvicorn** (0.46.0): ASGI server
- **python-socketio** (5.16.1): WebSocket support
- **python-engineio** (4.13.1): Engine.IO protocol
- **requests** (2.33.1): HTTP client
- **python-dotenv** (1.2.2): Environment variable management
- **pydantic** (2.13.4): Data validation

---

## 📞 Support & Resources

- **GitHub Issues**: [Create an issue](https://github.com/GarryBalala/onekhusa-python-integration/issues)
- **OneKhusa API Docs**: [https://docs.onekhusa.com](https://docs.onekhusa.com)
- **FastAPI Documentation**: [https://fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- **Socket.io Python**: [https://python-socketio.readthedocs.io](https://python-socketio.readthedocs.io)

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- **OneKhusa** for providing excellent payment gateway APIs
- **FastAPI** for the amazing async framework
- **Socket.io** for real-time communication capabilities
- **Tailwind CSS** for beautiful UI components

---

**Built by**: [GarryBalala](https://github.com/GarryBalala)  
**Last Updated**: May 2026
