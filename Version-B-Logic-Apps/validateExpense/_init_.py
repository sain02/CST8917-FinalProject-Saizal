import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        expense = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON payload",
            status_code=400
        )

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
            return func.HttpResponse(
                f"Missing field: {field}",
                status_code=400
            )

    if expense["category"] not in valid_categories:
        return func.HttpResponse(
            "Invalid category",
            status_code=400
        )

    return func.HttpResponse(
        json.dumps({"valid": True}),
        status_code=200,
        mimetype="application/json"
    )