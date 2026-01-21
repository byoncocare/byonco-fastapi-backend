import os
import sys
import httpx

TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
PIN = os.getenv("WHATSAPP_PIN")
CERT = os.getenv("WHATSAPP_CERTIFICATE")

def fail(msg):
    print(f"❌ {msg}")
    sys.exit(1)

if not TOKEN:
    fail("WHATSAPP_ACCESS_TOKEN missing")
if not PHONE_NUMBER_ID:
    fail("WHATSAPP_PHONE_NUMBER_ID missing")
if not PIN or not PIN.isdigit() or len(PIN) != 6:
    fail("WHATSAPP_PIN must be exactly 6 digits")
if not CERT or len(CERT) < 50:
    fail("WHATSAPP_CERTIFICATE looks invalid")

url = f"https://graph.facebook.com/v21.0/{PHONE_NUMBER_ID}/register"

payload = {
    "messaging_product": "whatsapp",
    "pin": PIN,
    "certificate": CERT
}

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("📡 Registering WhatsApp phone number...")
print(f"➡️  Phone Number ID: {PHONE_NUMBER_ID}")

try:
    with httpx.Client(timeout=30) as client:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        print("✅ SUCCESS:", response.json())
except httpx.HTTPStatusError as e:
    print("❌ Meta API Error:", e.response.text)
    sys.exit(1)
except Exception as e:
    print("❌ Unexpected error:", str(e))
    sys.exit(1)
