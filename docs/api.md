# 接口示例

以下示例展示了提交交易数据的基本 POST 请求：

```bash
curl -X POST https://api.example.com/v1/transactions \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "TXN123456",
    "user_id": "USER001",
    "amount": 150.00,
    "merchant_id": "MERCH001",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

## 主要接口

- `GET /health` - 服务健康检查。
- `POST /transactions` - 处理单笔交易并返回风险评分。
- `POST /transactions/batch` - 批量处理交易，返回每笔交易的结果。
- `GET /users/{user_id}/profile` - 查询用户风险画像。

