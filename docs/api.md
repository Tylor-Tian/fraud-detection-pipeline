# 接口示例

以下示例展示了提交交易数据的基本 POST 请求：

```bash
curl -X POST https://api.example.com/v1/transactions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "user_id": "USER001",
    "amount": 150.00
  }'
```

文档待补充
