# SRE Observability & Incident Readiness Platform

## Problem

Modern distributed systems often fail not because of a single bug, but due to lack of **visibility, resilience, and incident preparedness**.

This project solves:

*   Lack of **observability** (metrics, logs, traces in one place)
    
*   Poor **incident response readiness**
    
*   Inability to **test system resilience under failure**
    
*   Missing **SRE best practices** like SLIs, SLOs, alerting, and runbooks
    

In short:  
👉 Build a system that is not just working — but **monitorable, debuggable, and failure-resistant**

* * *

## Architecture

### System Flow

```mermaid
graph TD
    U[User / Client] --> MW[Observability Middleware]

    MW --> FI[Failure Injection Engine]
    FI --> AUTH[JWT Authentication]
    AUTH --> API[FastAPI Handlers]
    API --> DB_CONN[Async DB Engine]
    DB_CONN --> DB[(PostgreSQL)]

    %% Observability
    MW -. Metrics .-> PROM[Prometheus]
    MW -. Traces .-> TEMPO[Tempo]
    API -. Logs .-> LOKI[Loki]

    PROM --> GRAF[Grafana]
    TEMPO --> GRAF
    LOKI --> GRAF

    %% SRE Layer
    CHAOS[Chaos Experiments] --> FI
    PROM --> ALERTS[Alert Manager]
    ALERTS --> RUNBOOKS[Runbooks]
 ```

### Explanation

#### Request Lifecycle

*   User request enters → passes through middleware
    
*   Failure injection may simulate issues (latency/errors)
    
*   Auth layer validates JWT
    
*   API processes request and interacts with DB
    

#### Observability Layer

*   Prometheus → metrics (latency, errors, throughput)
    
*   Loki → logs
    
*   Tempo → traces
    
*   Grafana → unified dashboards (Golden Signals)
    

#### SRE Layer

*   Chaos engineering introduces failures
    
*   Alerts trigger runbooks
    
*   Enables structured incident handling
    

* * *

## Tech Stack

### Backend

*   Python (FastAPI)
    
*   Async SQLAlchemy
    
*   PostgreSQL
    

### Observability

*   Prometheus (Metrics)
    
*   Grafana (Dashboards)
    
*   Loki (Logging)
    
*   Tempo (Tracing)
    

### Infrastructure

*   Docker & Docker Compose
    
*   Kubernetes (HPA, PDB, graceful shutdown)
    
*   Helm (templated deployments)
    

### DevOps & Automation

*   GitHub Actions (CI/CD)
    
*   Pydantic (config management)
    

### SRE Practices

*   SLIs / SLOs
    
*   Alerting
    
*   Runbooks
    
*   Postmortems
    
*   Chaos Engineering
    

* * *

## How to Run

### Option 1: Full System (Recommended)

    docker-compose up --build
    

This starts:

*   FastAPI microservice
    
*   PostgreSQL database
    
*   Prometheus
    
*   Grafana
    
*   Tempo
    

* * *

### Option 2: Manual API Testing

#### 1\. Register User

    POST /api/auth/register
    

Body:

    {
      "username": "test",
      "email": "test@example.com",
      "password": "password"
    }
    

#### 2\. Get Token

    POST /api/auth/token
    

#### 3\. Create Resource

    POST /api/resource
    

#### 4\. Health Check

    GET /ready
    

* * *

## Monitoring Access

*   Metrics → [http://localhost:8000/metrics](http://localhost:8000/metrics)
    
*   Grafana → [http://localhost:3000](http://localhost:3000/)
    
*   Loki → [http://localhost:3100](http://localhost:3100/)
    

* * *

## Results

### Observability Outcomes

*   Achieved full-stack observability
    
*   Metrics + Logs + Traces correlation
    
*   Real-time dashboards using Golden Signals:
    
    *   Latency
        
    *   Traffic
        
    *   Errors
        
    *   Saturation
        

### Reliability Improvements

*   Failure injection validates:
    
    *   Latency spikes
        
    *   Error scenarios
        
    *   Resource exhaustion
        
*   System becomes resilient by design
    

### Incident Readiness

*   Alerts mapped directly to runbooks
    
*   Faster MTTR (Mean Time To Recovery)
    
*   Structured debugging using traces + logs
    

### Performance Characteristics

*   Async architecture improves throughput
    
*   Horizontal scaling via Kubernetes HPA
    
*   Persistent DB ensures reliability under load
