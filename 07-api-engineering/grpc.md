# gRPC, Protocol Buffers & High-Performance Microservices Guide

## Module Overview
This module covers **gRPC**, **Protocol Buffers (Protobuf)**, streaming models, and why internal microservices use gRPC over REST.

---

## gRPC vs REST API Comparison

| Feature | REST API | gRPC |
| :--- | :--- | :--- |
| **Payload Protocol** | Text JSON / XML | **Binary Protocol Buffers (Protobuf)** |
| **Transport** | HTTP/1.1 or HTTP/2 | **Strictly HTTP/2 (Multiplexed, Streaming)** |
| **Payload Size** | Larger (human readable strings) | **Up to 70% smaller** (compact binary packing) |
| **Speed & Throughput** | Standard | **Up to 7–10x faster** than JSON REST |
| **Streaming** | Request/Response (SSE is unidirectional) | **Unary, Client Streaming, Server Streaming, Bidirectional Streaming** |
| **Schema Contract** | OpenAPI / Swagger (optional) | **Strict `.proto` Interface Definition Language (IDL)** |
| **Browser Support** | Universal 100% native browser support | Requires `grpc-web` proxy |
| **Best Used For** | External public-facing APIs, web/mobile frontends | **Internal microservice-to-microservice communication** |

---

## Protobuf Definition Example

```protobuf
syntax = "proto3";

package payment;

service PaymentService {
  // Unary RPC
  rpc ProcessPayment (PaymentRequest) returns (PaymentResponse);
  // Server-Streaming RPC
  rpc StreamTransactions (AccountRequest) returns (stream Transaction);
}

message PaymentRequest {
  string account_id = 1;
  double amount_inr = 2;
  string currency = 3;
}

message PaymentResponse {
  bool success = 1;
  string transaction_id = 2;
}
```
