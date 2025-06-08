# 部署步骤

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 通过 Docker Compose 启动服务：
   ```bash
   docker-compose up -d
   ```
3. 验证服务状态：
   ```bash
   docker-compose ps
   ```

配置文件位于 `config.yaml`，可以通过环境变量覆盖。对于生产环境，
建议在多实例模式下部署，并在 Redis 与 Kafka 之间启用持久化与监控。
