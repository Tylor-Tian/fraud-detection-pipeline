# API Documentation

## Overview

The Fraud Detection Pipeline provides both REST API and streaming interfaces for real-time fraud detection.

## REST API

### Base URL

```
https://api.example.com/v1
```

### Authentication

All API requests require authentication using JWT tokens.

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" https://api.example.com/v1/transactions
```

### Endpoints

#### POST /transactions

Process a single transaction for fraud detection.

**Request Body:**
```json
{
  "transaction_id": "TXN123456",
  "user_id": "USER001",
  "amount": 150.00,
  "merchant_id": "MERCHANT123",
  "timestamp": "2024-01-15T10:30:00Z",
  "location": {
    "latitude": 40.7128,
    "longitude": -74.0060,
    "country": "USA",
    "city": "New York"
  },
  "device_id": "DEVICE789"
}
```

**Response:**
```json
{
  "transaction_id": "TXN123456",
  "risk_score": 0.23,
  "risk_level": "LOW",
  "is_fraud": false,
  "flags": [],
  "ml_score": 0.18,
  "rule_score": 0.28,
  "explanation": {
    "amount_factor": 0.1,
    "velocity_factor": 0.0,
    "location_factor": 0.05,
    "time_factor": 0.08
  },
  "processing_time_ms": 45.2,
  "timestamp": "2024-01-15T10:30:01Z"
}
```

**Status Codes:**
- `200 OK` - Transaction processed successfully
- `400 Bad Request` - Invalid transaction data
- `401 Unauthorized` - Invalid or missing authentication
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

#### POST /transactions/batch

Process multiple transactions in a single request.

**Request Body:**
```json
{
  "transactions": [
    {
      "transaction_id": "TXN123456",
      "user_id": "USER001",
      "amount": 150.00,
      "merchant_id": "MERCHANT123",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "transaction_id": "TXN123457",
      "user_id": "USER002",
      "amount": 2500.00,
      "merchant_id": "MERCHANT456",
      "timestamp": "2024-01-15T10:31:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "results": [
    {
      "transaction_id": "TXN123456",
      "risk_score": 0.23,
      "risk_level": "LOW",
      "is_fraud": false
    },
    {
      "transaction_id": "TXN123457",
      "risk_score": 0.85,
      "risk_level": "HIGH",
      "is_fraud": true
    }
  ],
  "summary": {
    "total_processed": 2,
    "fraud_detected": 1,
    "average_risk_score": 0.54,
    "processing_time_ms": 112.5
  }
}
```

#### GET /users/{user_id}/profile

Get risk profile for a specific user.

**Response:**
```json
{
  "user_id": "USER001",
  "transaction_count": 156,
  "average_amount": 125.50,
  "total_amount": 19578.00,
  "risk_level": "LOW",
  "last_transaction": "2024-01-15T10:30:00Z",
  "fraud_count": 2,
  "fraud_rate": 0.0128,
  "locations": [
    {
      "country": "USA",
      "city": "New York",
      "frequency": 0.85
    },
    {
      "country": "USA",
      "city": "Boston",
      "frequency": 0.15
    }
  ]
}
```

#### GET /merchants/{merchant_id}/risk

Get risk assessment for a merchant.

**Response:**
```json
{
  "merchant_id": "MERCHANT123",
  "risk_score": 0.15,
  "risk_level": "LOW",
  "transaction_count": 5842,
  "fraud_count": 23,
  "fraud_rate": 0.0039,
  "average_transaction_amount": 87.50,
  "categories": ["electronics", "online"]
}
```

#### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "redis": "connected",
    "model": "loaded",
    "kafka": "connected"
  },
  "uptime_seconds": 3847293,
  "processed_today": 1523847,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /metrics

Prometheus-compatible metrics endpoint.

**Response:**
```
# HELP fraud_detection_transactions_total Total number of transactions processed
# TYPE fraud_detection_transactions_total counter
fraud_detection_transactions_total 1523847

# HELP fraud_detection_fraud_detected_total Total number of fraudulent transactions detected
# TYPE fraud_detection_fraud_detected_total counter
fraud_detection_fraud_detected_total 3892

# HELP fraud_detection_processing_time_seconds Transaction processing time in seconds
# TYPE fraud_detection_processing_time_seconds histogram
fraud_detection_processing_time_seconds_bucket{le="0.01"} 892347
fraud_detection_processing_time_seconds_bucket{le="0.05"} 1423892
fraud_detection_processing_time_seconds_bucket{le="0.1"} 1523000
fraud_detection_processing_time_seconds_bucket{le="+Inf"} 1523847
```

### Rate Limiting

API endpoints are rate limited to prevent abuse:

- **Per IP:** 1000 requests per minute
- **Per API Key:** 10,000 requests per minute
- **Batch endpoint:** 100 requests per minute

Rate limit information is included in response headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 998
X-RateLimit-Reset: 1642248900
```

### Error Responses

All error responses follow this format:

```json
{
  "error": {
    "code": "INVALID_TRANSACTION",
    "message": "Transaction amount must be positive",
    "details": {
      "field": "amount",
      "value": -100,
      "constraint": "positive"
    }
  },
  "request_id": "req_abc123",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

Common error codes:
- `INVALID_TRANSACTION` - Transaction data validation failed
- `USER_NOT_FOUND` - User ID not found in system
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `INTERNAL_ERROR` - Server error
- `MODEL_ERROR` - ML model prediction failed

## Streaming API (Kafka)

### Topics

#### Input Topic: `transactions`

Send transactions for processing.

**Message Format:**
```json
{
  "transaction_id": "TXN123456",
  "user_id": "USER001",
  "amount": 150.00,
  "merchant_id": "MERCHANT123",
  "timestamp": "2024-01-15T10:30:00Z",
  "metadata": {
    "source": "mobile_app",
    "version": "2.1.0"
  }
}
```

#### Output Topic: `fraud_alerts`

Receive fraud detection results.

**Message Format:**
```json
{
  "transaction_id": "TXN123456",
  "risk_score": 0.85,
  "risk_level": "HIGH",
  "is_fraud": true,
  "flags": ["HIGH_AMOUNT", "VELOCITY"],
  "timestamp": "2024-01-15T10:30:01Z",
  "action": "BLOCK"
}
```

### Producer Configuration

```python
from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda k: k.encode('utf-8') if k else None,
    compression_type='snappy',
    acks='all',
    retries=3
)

# Send transaction
producer.send(
    'transactions',
    key=transaction['user_id'],
    value=transaction
)
```

### Consumer Configuration

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'fraud_alerts',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='fraud-alert-processor',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    alert = message.value
    if alert['is_fraud']:
        # Handle fraud case
        print(f"Fraud detected: {alert['transaction_id']}")
```

## SDK Examples

### Python SDK

```python
from fraud_detection import FraudDetectionClient

# Initialize client
client = FraudDetectionClient(
    api_key="YOUR_API_KEY",
    base_url="https://api.example.com/v1"
)

# Process single transaction
result = client.process_transaction({
    "transaction_id": "TXN123456",
    "user_id": "USER001",
    "amount": 150.00,
    "merchant_id": "MERCHANT123",
    "timestamp": "2024-01-15T10:30:00Z"
})

if result.is_fraud:
    print(f"Fraud detected! Risk score: {result.risk_score}")
    print(f"Flags: {', '.join(result.flags)}")

# Process batch
results = client.process_batch([transaction1, transaction2, transaction3])

# Get user profile
profile = client.get_user_profile("USER001")
print(f"User risk level: {profile.risk_level}")
```

### JavaScript/Node.js SDK

```javascript
const { FraudDetectionClient } = require('fraud-detection-sdk');

// Initialize client
const client = new FraudDetectionClient({
    apiKey: 'YOUR_API_KEY',
    baseUrl: 'https://api.example.com/v1'
});

// Process transaction
const result = await client.processTransaction({
    transactionId: 'TXN123456',
    userId: 'USER001',
    amount: 150.00,
    merchantId: 'MERCHANT123',
    timestamp: new Date().toISOString()
});

if (result.isFraud) {
    console.log(`Fraud detected! Risk score: ${result.riskScore}`);
    console.log(`Flags: ${result.flags.join(', ')}`);
}

// Stream processing
client.streamTransactions()
    .on('fraud', (alert) => {
        console.log(`Fraud alert: ${alert.transactionId}`);
    })
    .on('error', (error) => {
        console.error('Stream error:', error);
    });
```

### cURL Examples

```bash
# Process single transaction
curl -X POST https://api.example.com/v1/transactions \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "user_id": "USER001",
    "amount": 150.00,
    "merchant_id": "MERCHANT123",
    "timestamp": "2024-01-15T10:30:00Z"
  }'

# Get user profile
curl -X GET https://api.example.com/v1/users/USER001/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"

# Health check
curl -X GET https://api.example.com/v1/health
```

## Webhooks

Configure webhooks to receive real-time fraud alerts.

### Webhook Configuration

```json
POST /webhooks
{
  "url": "https://your-server.com/fraud-webhook",
  "events": ["fraud_detected", "high_risk"],
  "secret": "your_webhook_secret"
}
```

### Webhook Payload

```json
{
  "event": "fraud_detected",
  "transaction": {
    "transaction_id": "TXN123456",
    "user_id": "USER001",
    "amount": 5000.00,
    "risk_score": 0.92,
    "risk_level": "CRITICAL"
  },
  "timestamp": "2024-01-15T10:30:01Z",
  "signature": "sha256=..."
}
```

### Verifying Webhook Signatures

```python
import hmac
import hashlib

def verify_webhook(payload, signature, secret):
    expected = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(
        f"sha256={expected}",
        signature
    )
```

## Best Practices

1. **Always validate** transaction data before sending
2. **Implement retry logic** for network failures
3. **Cache user profiles** to reduce API calls
4. **Use batch endpoints** for bulk processing
5. **Monitor rate limits** and implement backoff
6. **Verify webhook signatures** for security
7. **Log all fraud alerts** for audit trails
8. **Set up monitoring** for API health

## Performance Guidelines

- **Latency**: 95th percentile < 100ms
- **Throughput**: 10,000 TPS per instance
- **Batch size**: Optimal 100-500 transactions
- **Connection pooling**: Recommended for high volume
- **Timeout**: Set client timeout to 5 seconds

## Support

- **Documentation**: https://docs.example.com
- **Status Page**: https://status.example.com
- **Support Email**: support@example.com
- **GitHub Issues**: https://github.com/Tylor-Tian/fraud-detection-pipeline/issues
