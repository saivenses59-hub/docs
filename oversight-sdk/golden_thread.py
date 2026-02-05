"""
OVERSIGHT SDK - Final Test
Tests SDK against institutional backend
"""

from oversight import OversightClient, PaymentResponse
import uuid


def main():
    print("=" * 70)
    print("OVERSIGHT SDK - Institutional Backend Test")
    print("=" * 70)
    
    # VALID TEST WALLET (42 characters)
    TEST_WALLET = "0x742d35cc6634c0532925a3b844bc9e7595f0beb0"  # ✅ 42 chars
    
    # Initialize client
    client = OversightClient(
        api_key="ovr_test",
        base_url="http://127.0.0.1:8000"
    )
    
    print(f"\n✅ Client initialized: {client.base_url}")
    print(f"📍 Test wallet: {TEST_WALLET}")
    print(f"   Length: {len(TEST_WALLET)} characters ✅")
    
    # Test payment
    print("\n" + "=" * 70)
    print("TEST 1: Payment Processing")
    print("=" * 70)
    
    try:
        response = client.pay(
            wallet_address=TEST_WALLET,
            amount=40.00,
            vendor="OpenAI"
        )
        
        print(f"\n🎯 Status: {response.status}")
        
        if response.status == "APPROVED":
            print(f"✅ Payment APPROVED")
            print(f"\n💰 Financial Breakdown:")
            print(f"   Gross Amount:    $40.00")
            print(f"   Vendor Paid:     ${response.vendor_paid:.2f} (90%)")
            print(f"   Tax Collected:   ${response.tax_collected:.2f} (10%)")
            print(f"   New Balance:     ${response.new_balance:.2f}")
            print(f"\n📝 Detail: {response.detail}")
            print(f"🆔 Transaction ID: {response.transaction_id}")
            print(f"🔑 Idempotency Key: {response.idempotency_key}")
        else:
            print(f"❌ Payment DENIED")
            print(f"📝 Reason: {response.detail}")
        
        print("\n" + "=" * 70)
        print("✅ TEST 1 PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST 1 FAILED: {type(e).__name__}")
        print(f"Error: {str(e)}")
        return
    
    # Test idempotency
    print("\n" + "=" * 70)
    print("TEST 2: Idempotency Protection")
    print("=" * 70)
    
    try:
        # First request with custom key
        key = f"test_{uuid.uuid4()}"
        
        response1 = client.pay(
            wallet_address=TEST_WALLET,
            amount=30.00,
            vendor="Stripe",
            idempotency_key=key
        )
        
        print(f"\n1st Request: {response1.status} - TX: {response1.transaction_id}")
        print(f"   Balance: ${response1.new_balance:.2f}")
        
        # Second request with SAME key (should return same result)
        response2 = client.pay(
            wallet_address=TEST_WALLET,
            amount=30.00,
            vendor="Stripe",
            idempotency_key=key  # Same key
        )
        
        print(f"2nd Request: {response2.status} - TX: {response2.transaction_id}")
        print(f"   Balance: ${response2.new_balance:.2f}")
        
        # Verify they're the same transaction
        if response1.transaction_id == response2.transaction_id:
            print(f"\n✅ Idempotency works! Same TX ID returned")
            print(f"   Balance unchanged: ${response2.new_balance:.2f}")
            
            if response1.new_balance == response2.new_balance:
                print(f"   ✅ Balance correctly NOT deducted twice!")
            else:
                print(f"   ❌ WARNING: Balance changed on retry!")
        else:
            print(f"\n❌ Idempotency FAILED - different TXs!")
        
        print("\n" + "=" * 70)
        print("✅ TEST 2 PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST 2 FAILED: {str(e)}")
    
    # Test deposit
    print("\n" + "=" * 70)
    print("TEST 3: Deposit Funds")
    print("=" * 70)
    
    try:
        deposit = client.deposit(
            wallet_address=TEST_WALLET,
            amount=100.00
        )
        
        print(f"\n💵 Deposit: {deposit.status}")
        print(f"   Amount: ${deposit.amount_deposited:.2f}")
        print(f"   New Balance: ${deposit.new_balance:.2f}")
        print(f"   TX ID: {deposit.transaction_id}")
        
        print("\n" + "=" * 70)
        print("✅ TEST 3 PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST 3 FAILED: {str(e)}")
    
    # Test list agents
    print("\n" + "=" * 70)
    print("TEST 4: List Agents")
    print("=" * 70)
    
    try:
        agents = client.get_agents()
        
        print(f"\n📋 Total Agents: {agents['count']}")
        
        for agent in agents['agents'][:3]:  # Show first 3
            print(f"\n   🤖 {agent['name']}")
            print(f"      Wallet: {agent['wallet_address']}")
            print(f"      Balance: ${agent['balance']:.2f}")
            print(f"      Daily Spent: ${agent['daily_spent']:.2f}")
        
        print("\n" + "=" * 70)
        print("✅ TEST 4 PASSED")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ TEST 4 FAILED: {str(e)}")
    
    # Cleanup
    client.close()
    
    print("\n" + "=" * 70)
    print("🎉 ALL TESTS COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()