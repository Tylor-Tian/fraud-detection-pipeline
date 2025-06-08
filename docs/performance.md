# Performance Tuning

The pipeline is optimized for real-time fraud detection. To achieve the best throughput:

1. **Scale Redis and Kafka** horizontally to handle increasing workloads.
2. **Tune model thresholds** in `config.yaml` to balance precision and recall.
3. **Monitor latency** via Prometheus and adjust worker concurrency accordingly.

