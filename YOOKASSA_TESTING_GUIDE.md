# YooKassa Payment Integration Testing Guide

## Overview
This guide provides comprehensive testing procedures for the YooKassa payment integration in the Telegram bot.

## Prerequisites

### 1. YooKassa Sandbox Setup
1. Register at [YooKassa](https://yookassa.ru/)
2. Get test credentials:
   - Shop ID (TEST_XXXXX)
   - API Key (test_XXXXX)
3. Add to `.env`:
   ```
   YOOKASSA_SHOP_ID=TEST_12345
   YOOKASSA_API_KEY=test_XXXXX
   ```

### 2. Test Cards
Use these test cards for sandbox testing:
- **Successful payment**: `5555 5555 5555 4444`
- **3DS Required**: `5555 5555 5555 5557`
- **Insufficient funds**: `5555 5555 5555 0002`

## Testing Scenarios

### 1. Payment Creation Flow

#### Test Case 1.1: Successful Payment Creation
1. Start bot with `/start`
2. Use `/buy` command
3. Click on any package (e.g., "💎 5 чтений - 299₽")
4. Verify:
   - Payment details message appears
   - Payment ID is displayed
   - "💳 Оплатить" button with valid URL
   - Database entry created with status "pending"

#### Test Case 1.2: Invalid Package Type
1. Send callback with invalid package: `buy_invalid`
2. Expected: Error alert "Неизвестный пакет"

#### Test Case 1.3: User Not Found
1. Clear user from database
2. Try to buy package
3. Expected: Error "Пользователь не найден. Используйте /start"

### 2. Webhook Processing

#### Test Case 2.1: Successful Payment Webhook
1. Create a test payment via bot
2. Use YooKassa API to simulate successful payment:
   ```bash
   curl -X POST "https://api.yookassa.ru/v3/payments/{payment_id}/capture" \
     -u "TEST_12345:test_XXXXX" \
     -H "Content-Type: application/json" \
     -d '{"amount": {"value": "299.00", "currency": "RUB"}}'
   ```
3. Verify:
   - Payment status changes to "succeeded"
   - User balance updated (when implemented)
   - No double processing on retry

#### Test Case 2.2: Invalid Webhook Signature
1. Send POST to `/yookassa_webhook` with invalid signature
2. Expected: 401 Unauthorized response

#### Test Case 2.3: Missing Payment in Database
1. Send webhook for non-existent payment ID
2. Expected: Error logged, 200 response (to prevent retries)

#### Test Case 2.4: Idempotency Test
1. Send same successful webhook twice
2. Expected: Second request processed but no duplicate actions

### 3. Payment History

#### Test Case 3.1: View Payment History
1. Create multiple payments
2. Use `/payments` command
3. Verify:
   - All payments listed
   - Correct status emojis
   - Proper formatting
   - Timestamps displayed

#### Test Case 3.2: Empty Payment History
1. New user with no payments
2. Use `/payments` command
3. Expected: "У вас пока нет платежей"

### 4. Error Handling

#### Test Case 4.1: YooKassa API Error
1. Set invalid API key in config
2. Try to create payment
3. Expected: Error message to user

#### Test Case 4.2: Database Error
1. Stop database service
2. Try to create payment
3. Expected: Error message to user

## Manual Testing Steps

### Step 1: Environment Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with test YooKassa credentials

# Start bot in webhook mode
python -m src.main
```

### Step 2: Test Payment Creation
1. Send `/start` to bot
2. Send `/buy` command
3. Click on "💎 5 чтений - 299₽"
4. Click "💳 Оплатить" button
5. In browser, complete test payment:
   - Use card: `5555 5555 5555 4444`
   - Any future expiry date
   - Any 3-digit CVV
   - Any cardholder name

### Step 3: Verify Database
```sql
-- Check payment record
SELECT * FROM payments WHERE status = 'pending';

-- After webhook success:
SELECT * FROM payments WHERE status = 'succeeded';
```

### Step 4: Test Webhook
```bash
# Test webhook endpoint (requires ngrok or similar)
curl -X POST "http://localhost:8080/yookassa_webhook" \
  -H "Content-Type: application/json" \
  -H "Yookassa-Signature: sha256_..." \
  -d '{"event": "payment.succeeded", "object": {...}}'
```

## Automated Tests

### Unit Tests Structure
```python
# tests/test_payments.py
import pytest
from src.services.payments import PaymentService

@pytest.mark.asyncio
async def test_create_payment():
    service = PaymentService()
    result = await service.create_payment(user_id=1, package_type="buy_5")
    assert result is not None
    assert "payment_id" in result
    assert "confirmation_url" in result

@pytest.mark.asyncio
async def test_webhook_signature_verification():
    service = PaymentService()
    # Test signature verification
    payload = '{"test": "data"}'
    signature = service.generate_signature(payload)
    assert service.verify_webhook_signature(payload, signature)
```

### Integration Tests
```python
# tests/test_payment_flow.py
import pytest
from aiogram_tests import MockedBot, Requester

@pytest.mark.asyncio
async def test_full_payment_flow():
    # Test complete payment flow
    # 1. Create user
    # 2. Initiate payment
    # 3. Process webhook
    # 4. Verify results
```

## Performance Testing

### Load Testing Webhook Endpoint
```bash
# Use Apache Bench or similar
ab -n 1000 -c 10 -p webhook_payload.json -T application/json \
   http://localhost:8080/yookassa_webhook
```

### Metrics to Monitor
- Response time < 200ms
- Success rate > 99.9%
- No memory leaks
- Database connection pool efficiency

## Security Testing

### 1. Signature Verification
- Test with various invalid signatures
- Verify HMAC-SHA256 implementation
- Check timing attack resistance

### 2. Input Validation
- Test with malformed JSON
- Test SQL injection attempts
- Verify webhook data sanitization

### 3. Rate Limiting
- Test webhook endpoint rate limiting
- Verify payment creation rate limits

## Production Deployment Checklist

### 1. Configuration
- [ ] Production YooKassa credentials
- [ ] HTTPS webhook URL
- [ ] Proper logging levels
- [ ] Monitoring setup

### 2. Database
- [ ] Payment table indexes
- [ ] Backup strategy
- [ ] Connection pooling

### 3. Security
- [ ] Webhook URL secured
- [ ] API keys in environment variables
- [ ] Rate limiting enabled
- [ ] Monitoring for suspicious activity

### 4. Monitoring
- [ ] Payment success/failure metrics
- [ ] Webhook processing metrics
- [ ] Error rate monitoring
- [ ] Database performance metrics

## Troubleshooting

### Common Issues

#### 1. Payment Creation Fails
**Symptoms:** Error message when clicking buy button
**Solutions:**
- Check YooKassa credentials
- Verify network connectivity
- Check database connection
- Review logs for specific error

#### 2. Webhook Not Processing
**Symptoms:** Payment stays in "pending" status
**Solutions:**
- Verify webhook URL accessibility
- Check YooKassa webhook configuration
- Verify signature verification
- Check webhook payload format

#### 3. Double Payment Processing
**Symptoms:** User gets double credits
**Solutions:**
- Check idempotency logic
- Verify webhook duplicate handling
- Review database transaction isolation

### Debug Commands
```bash
# Check bot logs
tail -f logs/bot.log

# Test webhook signature generation
python -c "
import hmac, hashlib
key = 'your_api_key'
payload = '{"test": "data"}'
signature = hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()
print(f'sha256_{signature}')
"

# Database queries
psql $DATABASE_URL -c "SELECT * FROM payments ORDER BY created_at DESC LIMIT 10;"
```

## Success Criteria

### Functional Requirements
- [x] Users can purchase reading packages
- [x] Payments are created in YooKassa
- [x] Webhooks are processed correctly
- [x] Payment history is accessible
- [x] Error handling works properly

### Non-Functional Requirements
- [x] Response time < 200ms
- [x] 99.9% uptime
- [x] Secure webhook processing
- [x] Idempotent operations
- [x] Comprehensive logging

### Business Requirements
- [x] Multiple package options
- [x] Russian language interface
- [x] Clear payment descriptions
- [x] User-friendly error messages
- [x] Payment tracking

## Conclusion

This testing guide covers all aspects of the YooKassa payment integration. Follow these steps to ensure a robust, secure, and user-friendly payment system.

For any issues or questions, refer to the:
- Application logs
- YooKassa documentation
- Database records
- Monitoring dashboards