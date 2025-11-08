# YooKassa Payment Integration Documentation

## Overview
This document describes the YooKassa payment integration that has been added to the Telegram bot, allowing users to purchase paid reading packages.

## Features Implemented

### ✅ Payment Service (`src/services/payments.py`)
- **Payment Creation**: Creates payments in YooKassa using Python SDK
- **Package Management**: Supports multiple reading packages (5, 10, 20 readings)
- **Webhook Handling**: Secure webhook processing with signature verification
- **Database Integration**: Tracks all payments in PostgreSQL
- **Error Handling**: Comprehensive error handling and logging
- **Idempotency**: Prevents double payment processing

### ✅ Payment Handlers (`src/handlers/payments.py`)
- **`/buy` Command**: Shows package selection menu
- **Buy Buttons**: Inline buttons for package selection (buy_5, buy_10, buy_20)
- **Payment Creation**: Creates payment and sends payment URL to user
- **`/payments` Command**: Shows payment history
- **Russian Language**: All messages in Russian

### ✅ Webhook Integration (`src/main.py`)
- **Webhook Server**: Integrated YooKassa webhook handler
- **Dual Webhooks**: Supports both Telegram and YooKassa webhooks
- **Port Configuration**: Configurable webhook port (default 8080)

### ✅ Configuration Updates
- **YooKassa Settings**: Shop ID and API key configuration
- **Webhook Port**: Configurable port for webhook server
- **Environment Variables**: All settings in `.env`

## Payment Packages

| Package | Readings | Price | Description |
|---------|----------|-------|-------------|
| buy_5 | 5 readings | 299₽ | Пакет из 5 платных чтений |
| buy_10 | 10 readings | 499₽ | Пакет из 10 платных чтений |
| buy_20 | 20 readings | 899₽ | Пакет из 20 платных чтений |

## User Flow

### 1. Purchase Flow
```
User sends /buy 
→ Bot shows package menu 
→ User selects package 
→ Bot creates payment 
→ User receives payment URL 
→ User completes payment 
→ YooKassa sends webhook 
→ Bot processes webhook 
→ User balance updated
```

### 2. Payment History
```
User sends /payments 
→ Bot fetches user payments 
→ Bot formats payment list 
→ Bot shows payment history
```

## Technical Implementation

### Payment Service Architecture
```python
class PaymentService:
    - create_payment()          # Creates YooKassa payment
    - check_payment_status()    # Checks payment status
    - verify_webhook_signature() # Verifies webhook signature
    - handle_webhook()          # Processes webhook events
    - get_user_payments()       # Gets user payment history
```

### Database Schema
```sql
payments table:
- id (PK)
- user_id (FK)
- yookassa_payment_id (UNIQUE)
- amount (DECIMAL)
- currency (VARCHAR)
- status (VARCHAR)
- description (TEXT)
- metadata (JSONB)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### Webhook Processing
```python
async def yookassa_webhook_handler(request):
    1. Extract signature from headers
    2. Verify HMAC-SHA256 signature
    3. Parse webhook payload
    4. Process payment event
    5. Update database records
    6. Return HTTP response
```

## Configuration

### Environment Variables
```bash
# YooKassa Configuration
YOOKASSA_SHOP_ID=your_shop_id_here
YOOKASSA_API_KEY=your_api_key_here

# Webhook Configuration
WEBHOOK_PORT=8080
```

### Package Configuration
```python
PACKAGES = {
    "buy_5": {
        "readings": 5,
        "amount": Decimal("299.00"),
        "description": "Пакет из 5 платных чтений"
    },
    "buy_10": {
        "readings": 10,
        "amount": Decimal("499.00"),
        "description": "Пакет из 10 платных чтений"
    },
    "buy_20": {
        "readings": 20,
        "amount": Decimal("899.00"),
        "description": "Пакет из 20 платных чтений"
    }
}
```

## Security Features

### 1. Webhook Signature Verification
- HMAC-SHA256 signature verification
- Prevents unauthorized webhook processing
- Constant-time comparison for timing attack protection

### 2. Idempotency
- Payment status checking before processing
- Prevents double credit allocation
- Database transaction safety

### 3. Input Validation
- YooKassa SDK validation
- Database constraints
- Error handling for malformed requests

## Error Handling

### Payment Creation Errors
- Invalid package types
- YooKassa API errors
- Database connection issues
- User not found errors

### Webhook Processing Errors
- Invalid signatures
- Missing payments in database
- Malformed webhook payloads
- Network timeouts

### User-Friendly Messages
All error messages are in Russian and provide clear guidance:
- "❌ Ошибка при создании платежа. Попробуйте позже."
- "❌ Пользователь не найден. Используйте /start"
- "❌ Неизвестный пакет"

## Logging

### Comprehensive Logging
- Payment creation events
- Webhook processing
- Error conditions
- User actions
- Database operations

### Log Format
```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

### Example Logs
```
2024-01-01 12:00:00 - src.services.payments - INFO - Создан платеж 123 для пользователя 456 на сумму 299.00
2024-01-01 12:01:00 - src.services.payments - INFO - Платеж 123 успешно обработан
2024-01-01 12:02:00 - src.services.payments - ERROR - Ошибка при обработке webhook: Invalid signature
```

## Testing

### Manual Testing
See `YOOKASSA_TESTING_GUIDE.md` for comprehensive testing procedures.

### Test Scenarios
1. **Payment Creation**: Test all package types
2. **Webhook Processing**: Test successful and failed payments
3. **Error Handling**: Test various error conditions
4. **Security**: Test signature verification
5. **Idempotency**: Test duplicate webhook processing

### Test Cards (Sandbox)
- Success: `5555 5555 5555 4444`
- 3DS Required: `5555 5555 5555 5557`
- Insufficient Funds: `5555 5555 5555 0002`

## Deployment

### Production Setup
1. **YooKassa Production Credentials**
   - Replace test credentials with production ones
   - Configure webhook URL in YooKassa dashboard

2. **Webhook URL**
   - Set up HTTPS endpoint
   - Configure firewall rules
   - Set up monitoring

3. **Database**
   - Ensure proper indexing
   - Set up backups
   - Monitor performance

### Monitoring
- Payment success rates
- Webhook processing times
- Error rates
- Database performance
- User engagement metrics

## Future Enhancements

### TODO Items
1. **Balance Integration**: Update user model to include balance fields
2. **Automatic Notifications**: Send payment confirmation messages
3. **Refund Support**: Handle payment refunds and cancellations
4. **Analytics Dashboard**: Payment statistics and analytics
5. **Subscription Model**: Recurring payment support

### Potential Improvements
1. **Package Customization**: Allow custom reading packages
2. **Promotional Codes**: Discount code system
3. **Payment Methods**: Additional payment methods support
4. **Multi-currency**: Support for different currencies
5. **Advanced Analytics**: Detailed payment analytics

## API Reference

### Payment Service Methods

#### `create_payment(user_id: int, package_type: str) -> Optional[Dict[str, Any]]`
Creates a new payment in YooKassa and database.

**Parameters:**
- `user_id`: Database user ID
- `package_type`: Package identifier (buy_5, buy_10, buy_20)

**Returns:**
- Dict with payment_id, confirmation_url, amount, description
- None if error occurred

#### `handle_webhook(request_data: Dict[str, Any]) -> bool`
Processes YooKassa webhook events.

**Parameters:**
- `request_data`: Webhook payload

**Returns:**
- True if processed successfully
- False if error occurred

#### `get_user_payments(user_id: int) -> List[Payment]`
Retrieves payment history for user.

**Parameters:**
- `user_id`: Database user ID

**Returns:**
- List of Payment objects

## Support

### Troubleshooting
1. **Payment Creation Fails**: Check YooKassa credentials and network
2. **Webhook Issues**: Verify webhook URL and signature
3. **Database Errors**: Check database connection and logs
4. **User Issues**: Verify user exists in database

### Debug Information
- Check application logs
- Verify YooKassa dashboard
- Test webhook endpoint
- Review database records

## Conclusion

The YooKassa payment integration provides a robust, secure, and user-friendly payment system for the Telegram bot. It includes comprehensive error handling, security features, and logging to ensure reliable operation in production.

For detailed testing procedures, refer to `YOOKASSA_TESTING_GUIDE.md`.