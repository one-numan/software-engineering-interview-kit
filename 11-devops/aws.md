# AWS Cloud Infrastructure & Services Interview Guide

## Module Overview
This module covers **Amazon Web Services (AWS)** architecture for backend engineers: **EC2**, **S3**, **RDS**, **IAM**, and **Application Load Balancers (ALB)**.

---

## Visual Architecture: Resilient Multi-AZ AWS Web Application

```mermaid
flowchart TD
    Internet([Public Internet]) --> Route53[Amazon Route 53 DNS]
    Route53 --> CloudFront[Amazon CloudFront CDN]
    CloudFront --> ALB[Application Load Balancer - Multi-AZ]
    
    subgraph VPC["Virtual Private Cloud (VPC)"]
        subgraph Public_Subnets["Public Subnets"]
            ALB
            NAT[NAT Gateway]
        end

        subgraph Private_App_Subnets["Private App Subnets"]
            ALB --> EC2_A[Auto-Scaling EC2 / ECS Task AZ-1]
            ALB --> EC2_B[Auto-Scaling EC2 / ECS Task AZ-2]
        end

        subgraph Private_DB_Subnets["Private Database Subnets"]
            EC2_A --> RDS_Primary[(Amazon RDS Multi-AZ Primary)]
            EC2_B --> RDS_Primary
            RDS_Primary -.->|Sync Replication| RDS_Standby[(RDS Multi-AZ Standby)]
            EC2_A --> ElastiCache[(Amazon ElastiCache Redis)]
        end
    end
```

---

## Questions & Comprehensive Solutions

### AWS-BAS-001: Core AWS Services Explained

1. **Amazon EC2 (Elastic Compute Cloud):** Resizable virtual machines in the cloud (IaaS).
2. **Amazon S3 (Simple Storage Service):** Highly scalable object storage with 11 9's durability.
3. **Amazon RDS (Relational Database Service):** Managed PostgreSQL/MySQL with automated failover and backups.
4. **AWS IAM (Identity & Access Management):** Controls authentication and permissions using IAM Roles (e.g. EC2 instance profiles accessing S3 without hardcoded credentials).
