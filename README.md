# CST8917 Final Project
## Dual Implementation of an Expense Approval Workflow

**Name:** Saizal Saini  
**Student Number:** 041168394  
**Course:** CST8917 – Serverless Applications  

---

### YouTube Video Link:

## Overview

This project implements the same business workflow an expense approval pipeline using two different Azure serverless orchestration approaches:

- **Version A:** Azure Durable Functions (code-first orchestration)
- **Version B:** Azure Logic Apps with Azure Service Bus (visual/declarative orchestration)

The goal of the project is to directly compare these approaches based on hands-on experience and evaluate their trade-offs across development experience, testability, error handling, human interaction patterns, observability, and cost.

---

## Version A – Durable Functions Summary

Version A implements the expense approval workflow using Azure Durable Functions with the Python v2 programming model. The workflow is orchestrated using a durable orchestrator function, with separate activity functions handling validation, notification, and processing logic.

### Architecture and Design
- HTTP-triggered client function starts the orchestration.
- Durable orchestrator coordinates the workflow.
- Activity functions handle:
  - Expense validation
  - Email notification
- Human interaction is implemented using `wait_for_external_event`.
- A durable timer handles timeout scenarios for manager approval.

### Business Rules Implementation
- Expenses under $100 are automatically approved.
- Expenses $100 or more require manager approval.
- If no manager response is received within the timeout, the expense is auto-approved and flagged as escalated.
- Validation rejects missing fields or invalid categories.

### Challenges
The main challenge was configuring the Python v2 Durable Functions programming model, including setting up the correct decorators, managing durable timers, and ensuring proper local environment configuration. However, once configured, the workflow logic was clear and easy to follow due to its code-first nature.

---

## Version B – Logic Apps + Service Bus Summary

Version B implements the same workflow using Azure Logic Apps for orchestration and Azure Service Bus for message-based communication. Validation logic is handled by an Azure Function, while the overall workflow is modeled visually in the Logic App designer.

### Architecture and Design
- Expense requests are sent to an Azure Service Bus queue.
- A Logic App is triggered when a message arrives in the queue.
- An Azure Function performs expense validation.
- Logic App conditions and control flow implement business rules.
- Final outcomes are published to an Azure Service Bus topic with filtered subscriptions.

### Human Interaction Approach
Logic Apps do not natively support the Durable Functions human interaction pattern. To address this, manager approval was modeled using an email notification combined with an `Until` loop and `Delay` actions to simulate a timeout. If no response is received within the defined time window, the expense is automatically approved and marked as escalated.

### Challenges
The biggest challenges were tool-related rather than conceptual, including connector limitations with Linux-based Python Function Apps and managing Logic App state across delayed execution steps. Debugging also required navigating Logic App run history instead of traditional logs.

---

## Comparison Analysis

### Development Experience
Durable Functions felt more natural for implementing complex business logic, especially workflows involving timers and external events, because all logic was expressed directly in code. This provided greater confidence that the workflow behaved exactly as intended. Logic Apps, while faster to build initially for simple workflows, became more complex as conditional logic and timeout patterns were added.

### Testability
Durable Functions were significantly easier to test locally using Azure Functions Core Tools and HTTP test files. Logic Apps required cloud deployment for most testing, which slowed iteration and made automated testing more difficult.

### Error Handling
Durable Functions provided fine-grained control over retries and exception handling in code. Logic Apps offer built-in retries and visibility but less control over custom recovery behavior.

### Human Interaction Pattern
Durable Functions clearly outperformed Logic Apps for human interaction scenarios due to native support for waiting on external events. Logic Apps required a custom workaround using delays and loops, which felt less intuitive and more fragile.

### Observability
Logic Apps excelled in observability, with clear visual run history and execution paths. Durable Functions relied more on logs and Application Insights for tracing, which required more setup to analyze.

### Cost
At low volumes (~100 requests/day), both approaches have minimal cost differences. At higher volumes (~10,000/day), Logic Apps may become more expensive due to per-action billing, while Durable Functions benefit from lower per-execution costs but require more operational monitoring.

---

## Recommendation

For a production-grade expense approval system with complex workflows and human interaction requirements, Azure Durable Functions would be the preferred approach. The code-first model provides better control, clearer logic, easier testing, and stronger support for long-running workflows. However, Logic Apps are well suited for simpler integrations, rapid prototyping, or scenarios where visual monitoring by non-developers is important.

---

## References

- Azure Durable Functions Documentation  
  https://learn.microsoft.com/azure/azure-functions/durable/durable-functions-overview

- Azure Logic Apps Documentation  
  https://learn.microsoft.com/azure/logic-apps/logic-apps-overview

- Azure Pricing Calculator  
  https://azure.microsoft.com/pricing/calculator/

---

## AI Disclosure

AI tools were used to assist in understanding Azure Durable Functions patterns, Logic Apps design considerations, and troubleshooting environment configuration issues and formatting the Readme file. 