def validate_return_request(data):
    if not data:
        return "No data provided"

    if not data.get("order_id"):
        return "Order ID is required"

    if not data.get("reason"):
        return "Return reason is required"

    if len(data.get("reason")) < 10:
        return "Reason must be at least 10 characters"

    return None
