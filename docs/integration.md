# Integration Guide

This guide outlines how to integrate the Fraud Detection Pipeline with your existing systems.

## REST API

Use the `/transactions` endpoint to submit single transactions and `/transactions/batch` for batches. Each request must include a valid authentication token.

## Streaming

For high volume throughput, publish transaction events to the Kafka `transactions` topic. The service consumes events, evaluates risk and publishes results to `fraud_alerts`.

