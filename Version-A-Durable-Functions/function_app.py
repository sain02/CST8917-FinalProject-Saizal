import azure.functions as func
import azure.durable_functions as df
from datetime import timedelta

app = df.DFApp()

# =====================================================
# CLIENT FUNCTION (Employee submits expense)
# =====================================================
@app.route(route="expense", methods=["POST"])
@app.durable_client_input(client_name="client")
async def start_expense(req: func.HttpRequest, client):
    expense = req.get_json()
    instance_id = await client.start_new(
        orchestration_function_name="expense_orchestrator",
        client_input=expense
    )
    return client.create_check_status_response(req, instance_id)


# =====================================================
# MANAGER DECISION ENDPOINT
# =====================================================
@app.route(route="manager/{instance_id}", methods=["POST"])
@app.durable_client_input(client_name="client")
async def manager_decision(req: func.HttpRequest, client):
    decision = req.params.get("decision")
    instance_id = req.route_params["instance_id"]

    await client.raise_event(
        instance_id=instance_id,
        event_name="manager_response",
        event_data=decision
    )

    return func.HttpResponse("Manager decision received")


# =====================================================
# ORCHESTRATOR FUNCTION ✅ (v2 decorator)
# =====================================================
@app.orchestration_trigger(context_name="context")
def expense_orchestrator(context: df.DurableOrchestrationContext):
    expense = context.get_input()

    validation = yield context.call_activity(
        "validate_expense", expense
    )

    if not validation["ok"]:
        yield context.call_activity("notify_employee", validation)
        return validation

    # Auto-approve under $100
    if expense["amount"] < 100:
        expense["status"] = "approved"
        yield context.call_activity("notify_employee", expense)
        return expense

    # Wait for manager OR timeout
    approval_event = context.wait_for_external_event("manager_response")
    timeout = context.create_timer(
        context.current_utc_datetime + timedelta(minutes=1)
    )

    completed = yield context.task_any([approval_event, timeout])

    if completed == timeout:
        expense["status"] = "escalated"
    else:
        expense["status"] = approval_event.result

    yield context.call_activity("notify_employee", expense)
    return expense


# =====================================================
# ACTIVITY FUNCTIONS ✅ (v2 decorator)
# =====================================================
@app.activity_trigger(input_name="expense")
def validate_expense(expense: dict):
    required_fields = [
        "employee", "email", "amount",
        "category", "managerEmail"
    ]
    valid_categories = [
        "travel", "meals", "supplies",
        "equipment", "software", "other"
    ]

    for field in required_fields:
        if field not in expense:
            return {"ok": False, "error": f"Missing field: {field}"}

    if expense["category"] not in valid_categories:
        return {"ok": False, "error": "Invalid category"}

    return {"ok": True}


import json

@app.activity_trigger
def notify_employee(data: str):
    payload = json.loads(data)
    print("EMAIL SENT:", payload)