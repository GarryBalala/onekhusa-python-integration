# OneKhusa Python Integration Reference

A professional reference implementation of the **OneKhusa Payment Gateway** using **Python 3**, **FastAPI**, and **Socket.io**. This project demonstrates the **Hosted Checkout** flow with real-time webhook automation, specifically optimized for mobile and web application backends.

## 🚀 Key Features
- **FastAPI Backend**: High-performance, asynchronous Python server.
- **Hosted Checkout**: Seamless redirection logic to OneKhusa’s managed payment page.
- **Real-Time Webhooks**: Automated transaction verification using WebSockets (`python-socketio`).
- **Verification Overlay**: A robust frontend strategy to handle asynchronous payment redirects.
- **Strict Validation**: Automatic cleaning of references to ensure alphanumeric compatibility.

---

## 📂 Project Structure
```text
onekhusa-python-integration/
├── app/
│   ├── main.py             # FastAPI Server, Socket.io & Webhook Logic
│   └── services/
│       └── onekhusa_service.py # Core API Logic (Hosted Checkout Service)
├── public/
│   └── index.html          # OneTicket Fintech Dashboard (Frontend)
├── .env                    # The Brain: Configuration & Secrets
├── .gitignore              # Security: Excludes venv and .env from Git
└── requirements.txt        # Python Project Dependencies
🛠️ Setup & Installation
1. Prerequisites
Python 3.8+
NGrok (for local webhook testing)
OneKhusa Merchant Account
2. Installation
code
Bash
# Clone the repository
git clone https://github.com/GarryBalala/onekhusa-python-integration.git
cd onekhusa-python-integration

# Set up virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
3. Configuration (.env)
Create a .env file in the root directory. This file acts as the brain of your integration. Copy and fill in the following keys:
code
Env
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
PUBLIC_CALLBACK_URL=https://zena-unjudgeable-renita.ngrok-free.dev

# Server Config
PORT=8000
📡 Webhook Automation Setup
To receive real-time notifications on your local machine from the cloud:
Start NGrok: Run ngrok http 8000.
Update .env: Copy the generated https URL from NGrok and paste it into the PUBLIC_CALLBACK_URL field in your .env.
Register URL: In the OneKhusa Portal, navigate to Developers > Webhooks and register the following callback:
https://your-id.ngrok-free.dev/webhooks/payments
💻 Usage
Starting the Server
code
Bash
python -m app.main
The application will be available at http://localhost:8000.
Functional Flow
Initiation: The user clicks "Purchase" on the dashboard. The FastAPI backend calls OneKhusa to create a session.
Redirection: The browser is redirected to the OneKhusa Hosted Checkout page.
Simulation: You complete the payment in the OneKhusa Sandbox Portal using the TAN provided on the checkout page.
Verification: OneKhusa redirects the user back to the dashboard. The Verification Overlay appears, polling the backend and waiting for the Socket.io event triggered by the incoming webhook.