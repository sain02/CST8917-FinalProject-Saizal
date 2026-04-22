# CST8917 Final Project
## Dual Implementation of an Expense Approval Workflow

**Name:** Saizal Saini  
**Student Number:** 041168394  
**Course:** CST8917 – Serverless Applications  

---

### YouTube Video Link:

https://youtu.be/6FF-avWNRD0 
### Presentation Slides:

For the presentation slides, I have submitted it separately with the Repository Link.

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

## Comparison — Durable Functions vs Logic Apps

This section compares the two implementations of the expense approval workflow based on hands-on development experience. The same business rules were implemented twice once using Azure Durable Functions and once using Azure Logic Apps with Azure Service Bus allowing for a direct, experience-based comparison across six key dimensions.

---

### High-Level Comparison Summary

| Dimension | Durable Functions (Version A) | Logic Apps + Service Bus (Version B) |
|---------|-------------------------------|--------------------------------------|
| Development Experience | Code-first, more setup required | Faster initial setup, visual designer |
| Testability | Strong local testing support | Mostly cloud-based testing |
| Error Handling | Explicit and customizable in code | Built-in retries, less granular |
| Human Interaction | Native support via external events | Requires custom workaround |
| Observability | Logs and Application Insights | Excellent visual run history |
| Cost | Predictable for complex workflows | Can increase with action count |

---

### Development Experience

Developing the workflow using Azure Durable Functions required more initial setup, including configuring the Python v2 programming model, durable orchestrators, and local storage emulation. However, once the environment was correctly configured, implementing the workflow felt natural and well-structured. All business rules, branching conditions, and timeout logic were expressed directly in code, making the workflow easier to reason about and maintain.

Logic Apps provided a faster initial development experience for simple scenarios. The visual designer made it easy to connect services, add conditions, and build a basic workflow quickly. However, as the workflow grew more complex especially when implementing timeouts and approval logic the visual layout became harder to follow compared to structured code.

**Summary:** Logic Apps were quicker to start, but Durable Functions provided a clearer and more maintainable experience for complex workflows.

---

### Testability

Durable Functions were significantly easier to test locally. Using Azure Functions Core Tools and HTTP test files, the entire workflow could be executed and validated without deploying to Azure. Scenarios such as manager approval, rejection, and timeout could be simulated quickly, which supported rapid iteration and debugging.

In contrast, Logic Apps required deployment to Azure before meaningful testing could occur. Debugging relied on the Logic App run history, which is useful but slower to iterate with than local testing. Automated testing of Logic Apps was also more difficult to implement compared to code-based solutions.

**Summary:** Durable Functions provided a superior local testing and debugging experience.

---

### Error Handling

Error handling in Durable Functions was implemented directly in code, allowing precise control over how validation errors, failures, and timeout scenarios were handled. Exceptions, retries, and fallback logic could be customized to match the workflow’s requirements.

Logic Apps offer built-in retry behavior at the connector level, which simplifies handling transient failures. However, this approach provides less control for implementing complex recovery logic or custom error propagation.

**Summary:** Durable Functions offer more flexibility and control, while Logic Apps prioritize simplicity.

---

### Human Interaction Pattern

This dimension highlighted the most significant difference between the two approaches.

Durable Functions natively support human interaction through the `wait_for_external_event` pattern. Implementing “wait for manager approval or timeout” aligned naturally with the workflow and required minimal additional logic.

Logic Apps do not provide native support for waiting on human input. To handle manager approval, a workaround was designed using email notifications combined with an `Until` loop and `Delay` actions. While effective, this approach was less intuitive and more complex than the Durable Functions implementation.

**Summary:** Durable Functions are clearly better suited for workflows involving human interaction and timeouts.

---

### Observability

Logic Apps excel in observability. The visual run history clearly displays each step, condition branch, execution time, and failure point. This makes monitoring and troubleshooting much easier, especially for demonstrations or operational tracking.

Durable Functions rely on logs and Application Insights for observability. While powerful, this requires additional configuration and familiarity with log querying. Understanding workflow execution often involves correlating multiple log entries instead of viewing a single visual timeline.

**Summary:** Logic Apps provide better built-in observability, while Durable Functions require more tooling knowledge.

---

### Cost Considerations

At low volumes (approximately 100 expense submissions per day), both approaches have negligible cost differences and are suitable for small workloads. At higher volumes (for example, 10,000 requests per day), cost differences become more relevant.

Logic Apps charge per action, meaning workflows with many steps can become costly as volume increases. Durable Functions, running on a consumption plan, tend to scale more predictably for complex workflows, though they require monitoring to avoid excessive executions.

**Summary:** Durable Functions offer more predictable costs for complex workflows, while Logic Apps may become more expensive as workflow complexity increases.

---

### Overall Comparison Takeaway

| Scenario | Recommended Approach |
|--------|----------------------|
| Complex workflow logic | Durable Functions |
| Human approval with timeout | Durable Functions |
| Rapid prototyping | Logic Apps |
| Visual monitoring and demos | Logic Apps |
| Strong local testing | Durable Functions |

---

Overall, both approaches are viable depending on the use case. Durable Functions are better suited for complex, long-running workflows with human interaction requirements, while Logic Apps are ideal for integration-heavy scenarios that benefit from visual orchestration and built-in monitoring.

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

---
---

## THANKS