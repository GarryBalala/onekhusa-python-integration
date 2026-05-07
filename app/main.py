import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import socketio
import uvicorn
from .services.onekhusa_service import onekhusa_service

# 1. Initialize FastAPI and Socket.io
app = FastAPI()
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
socket_app = socketio.ASGIApp(sio, app)

# 2. Middleware & Static Files
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serves the index.html from the public folder
app.mount("/public", StaticFiles(directory="public"), name="public")

# 3. In-memory Transaction Tracker
ticket_tracker = {}

@sio.event
async def connect(sid, environ):
    print(f"Socket connected: {sid}")

# --- API ROUTES ---

@app.post("/api/Tickets/buy/{event_id}")
async def buy_ticket(event_id: str):
    """
    Initiates the OneKhusa Hosted Checkout.
    Generates a reference and returns the redirect URL.
    """
    # Generate reference: OT-PY + last 8 digits of timestamp
    import time
    reference = f"OT-PY{str(int(time.time()))[-8:]}"
    
    try:
        data = onekhusa_service.initiate_hosted_checkout(
            amount=2500.00,
            reference=reference,
            description="OneTicket Python Showcase"
        )
        
        # Save status as Pending
        ticket_tracker[reference] = "Pending"
        
        # Return redirect URL
        # URL pattern: https://checkout.onekhusa.com/requestToPay/initiate?ptid=...
        ptid = data.get("paymentTransactionId")
        redirect_url = f"https://checkout.onekhusa.com/requestToPay/initiate?ptid={ptid}"
        
        return {
            "status": "success",
            "redirectUrl": redirect_url,
            "reference": reference
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

@app.get("/api/Tickets/status/{reference}")
async def get_status(reference: str):
    """Polling fallback for the UI"""
    status = ticket_tracker.get(reference, "NotFound")
    return {"status": status}

@app.post("/webhooks/payments")
async def handle_webhook(request: Request):
    """
    Webhook listener for OneKhusa notifications.
    Handles TitleCase keys from Sandbox metadata.
    """
    payload = await request.json()
    
    # 1. Extract reference (Check TitleCase and camelCase)
    metadata = payload.get("metaData", {})
    my_ref = metadata.get("ReferenceNumber") or metadata.get("referenceNumber") or payload.get("sourceReferenceNumber")
    
    print(f"Webhook Received for Ref: {my_ref}")
    
    # 2. Verify Success
    # S100 = Success, S = Checkout Success
    if payload.get("responseCode") == "S100" or payload.get("transactionStatusCode") == "S":
        ticket_tracker[my_ref] = "Paid"
        print(f"Status updated to PAID for {my_ref}")
        
        # 3. Real-time update to UI via Socket.io
        await sio.emit('webhook_received', {'reference': my_ref, 'status': 'Paid'})

    # 4. MANDATORY: Respond with 'acknowledged'
    return PlainTextResponse("acknowledged")

# Root route redirect to UI
@app.get("/")
async def read_index():
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/public/index.html")

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("app.main:socket_app", host="0.0.0.0", port=port, reload=True)