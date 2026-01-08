

def expense_schema(data):
    """Ensure all fields exist and provide default None if missing"""
    return {
        "expense_id": data.get("expense_id"),
        "date": data.get("date"),
        "category": data.get("category"),
        "amount": data.get("amount"),
        "description": data.get("description"),
        "payment_mode": data.get("payment_mode"),
        "merchant_name": data.get("merchant_name"),
        "location": data.get("location"),
        "notes": data.get("notes"),
        "created_by": data.get("created_by")
    }
