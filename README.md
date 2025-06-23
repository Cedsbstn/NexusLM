# NexusLM: Large Language Model Customer Service Agent

This project implements an AI-powered customer service agent using NexusLM, a large language model designed for customer interactions. The agent excels at providing excellent customer service, assisting with inquiries, managing orders, scheduling services, and offering personalized recommendations.

## Overview

The NexusLM Customer Service Agent delivers seamless and personalized customer experiences. It leverages advanced natural language processing to understand customer needs, offer contextual responses, manage transactions, and schedule appointments. The agent maintains a professional, friendly, and efficient demeanor throughout all interactions.

## Agent Details

Key features of the NexusLM Agent include:

| Feature            | Description             |
| ------------------ | ----------------------- |
| _Interaction Type_ | Natural Language        |
| _Complexity_       | Advanced                |
| _Agent Type_       | Multi Agent            |
| _Components_       | Tools, Multimodal, Live |
| _Vertical_         | Customer Service        |

### Agent Architecture

![Agent Workflow](agent_workflow.png)

The agent employs a multi-modal architecture that processes text and multimedia inputs. It interfaces with various mock tools including:
- Customer Database
- Appointment Scheduling
- Product Catalog
- Inventory System

Note: This implementation uses mock tools. For production deployment, modify [tools/tools.py](./tools/tools.py) to integrate with actual backend services.

### Key Features

- **Personalized Service:**
  - Customer recognition
  - Context-aware responses
- **Order Management:**
  - Product recommendations
  - Inventory checks
- **Appointment Scheduling:**
  - Meeting arrangements
  - Confirmation handling
- **Support Features:**
  - 24/7 available
  - Status tracking
- **Feedback Mechanism:**
  - Customer feedback collection
  - Continuous improvement suggestions

### Installation
1. Clone repository
2. Install dependencies:
```bash
poetry install
```
3. Configure environment:
```bash
cp .env.example .env
```
## Usage
Run the agent:
```bash
adk web
```

## License
MIT License
