"""
OVERSIGHT SDK - Final Test Script
"""

from oversight import OversightClient, PaymentResponse
import sys


def print_section(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def test_payment():
    print_section("OVERSIGHT SDK - Final Test")
    
    API_KEY = "ovr_test"
    BASE_URL = "http://127.0.0.1:8000"
    WALLET_ADDRESS = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
    AMOUNT = 100.00
    VENDOR = "OpenAI"
    
    print(f"\n📋 Configuration:")
    print(f"   API Key:     {API_KEY}")
    print(f"   Backend URL: {BASE_URL}")
    print(f"   Wallet:      {WALLET_ADDRESS}")
    print(f"   Amount:      ")
    print(f"   Vendor:      {VENDOR}")
    
    print_section("Initializing Client")
    
    try:
        client = OversightClient(api_key=API_KEY, base_url=BASE_URL)
        print(f"\n✅ Client initialized successfully")
        print(f"   {client}")
    except Exception as e:
        print(f"\n❌ Failed to initialize client: {e}")
        sys.exit(1)
    
    print_section("Sending Payment Request")
    print(f"\n📤 Calling client.pay()...")
    print(f"   wallet_address = {WALLET_ADDRESS}")
    print(f"   amount = {AMOUNT}")
    print(f"   vendor = {VENDOR}")
    
    try:
        response = client.pay(
            wallet_address=WALLET_ADDRESS,
            amount=AMOUNT,
            vendor=VENDOR
        )
        
        print_section("Payment Response")
        print(f"\n🎯 Status: {response.status}")
        
        if response.status == "APPROVED":
            print(f"   ✅ Payment APPROVED")
        else:
            print(f"   ❌ Payment DENIED")
        
        print(f"\n💰 Financial Breakdown:")
        print(f"   Gross Amount:    ")
        print(f"   Vendor Paid:      (90%)")
        print(f"   Tax Collected:    (10%)")
        print(f"   New Balance:     ")
        
        print(f"\n📝 Detail:")
        print(f"   {response.detail}")
        
        print_section("Verification")
        
        expected_tax = AMOUNT * 0.10
        expected_vendor = AMOUNT * 0.90
        
        tax_ok = abs(response.tax_collected - expected_tax) < 0.01
        vendor_ok = abs(response.vendor_paid - expected_vendor) < 0.01
        
        print(f"\n🔍 Tax Calculation:    {'✅ PASS' if tax_ok else '❌ FAIL'}")
        print(f"   Expected: ")
        print(f"   Received: ")
        
        print(f"\n🔍 Vendor Payment:     {'✅ PASS' if vendor_ok else '❌ FAIL'}")
        print(f"   Expected: ")
        print(f"   Received: ")
        
        if response.status == "APPROVED" and tax_ok and vendor_ok:
            print_section("✅ ALL TESTS PASSED")
            print("\n🎉 SDK is working correctly!")
        else:
            print_section("⚠️ TESTS COMPLETED WITH WARNINGS")
        
    except Exception as e:
        print_section("❌ TEST FAILED")
        print(f"\n💥 Error Type: {type(e).__name__}")
        print(f"📄 Error Message: {str(e)}")
        
        # Fixed: Check if response attribute exists
        if hasattr(e, 'response') and e.response is not None:
            print(f"\n🌐 HTTP Response:")
            print(f"   Status Code: {e.response.status_code}")
            print(f"   Body: {e.response.text[:200]}")
        
        # Connection error specific message
        if "ConnectionError" in str(type(e)):
            print("\n⚠️  BACKEND NOT RUNNING!")
            print("    Start your backend server first:")
            print("    1. Open a new terminal")
            print("    2. cd to your backend directory")
            print("    3. Run: python main.py")
        
        sys.exit(1)
    
    finally:
        client.close()
        print("\n🔌 Client connection closed")
    
    print("\n" + "=" * 70 + "\n")


if __name__ == "__main__":
    test_payment()
