from flask import Blueprint, request, jsonify, send_file
from database.mongo import expense_collection
from models.expense_model import expense_schema
import pandas as pd
from fpdf import FPDF
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4  

expense_bp = Blueprint("expense_bp", __name__)

# -------------------------------
# CREATE EXPENSE (POST)
# -------------------------------
@expense_bp.route("/expenses", methods=["POST"])
def create_expense():
    data = request.get_json()
    if not data or "expense_id" not in data:
        return jsonify({"error": "expense_id is required"}), 400

    # Normalize ID
    data["expense_id"] = data["expense_id"].upper()

    # Check if ID already exists
    existing = expense_collection.find_one({"expense_id": data["expense_id"]})
    if existing:
        return jsonify({"error": f"Expense ID '{data['expense_id']}' already exists"}), 409

    expense = expense_schema(data)
    expense_collection.insert_one(expense)
    return jsonify({
        "message": "Expense added successfully",
        "expense_id": expense["expense_id"]
    }), 201
# -------------------------------
# READ ALL EXPENSES (GET)
# -------------------------------
@expense_bp.route("/expenses", methods=["GET"])
def get_all_expenses():
    expenses = list(expense_collection.find({}, {"_id": 0}))
    return jsonify(expenses), 200

# -------------------------------
# READ EXPENSE BY ID (GET)
# -------------------------------
@expense_bp.route("/expenses/<expense_id>", methods=["GET"])
def get_expense_by_id(expense_id):
    expense_id = expense_id.upper()  # normalize
    expense = expense_collection.find_one({"expense_id": expense_id}, {"_id": 0})
    if expense:
        return jsonify(expense), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

# -------------------------------
# UPDATE EXPENSE (PUT)
# -------------------------------
@expense_bp.route("/expenses/<expense_id>", methods=["PUT"])
def update_expense(expense_id):
    expense_id = expense_id.upper()
    data = request.get_json()

    # Prevent changing to a duplicate expense_id if included in payload
    if "expense_id" in data:
        data["expense_id"] = data["expense_id"].upper()
        existing = expense_collection.find_one({"expense_id": data["expense_id"]})
        if existing and existing["expense_id"] != expense_id:
            return jsonify({"error": f"Expense ID '{data['expense_id']}' already exists"}), 409

    update_data = {"$set": expense_schema(data)}
    result = expense_collection.update_one({"expense_id": expense_id}, update_data)
    if result.matched_count:
        return jsonify({"message": "Expense updated successfully"}), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

# -------------------------------
# DELETE EXPENSE (DELETE)
# -------------------------------
@expense_bp.route("/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense_id = expense_id.upper()
    result = expense_collection.delete_one({"expense_id": expense_id})
    if result.deleted_count:
        return jsonify({"message": "Expense deleted successfully"}), 200
    else:
        return jsonify({"error": "Expense not found"}), 404

# -------------------------------
# DEBUG: view all data in terminal
# -------------------------------
@expense_bp.route("/debug_expenses", methods=["GET"])
def debug_expenses():
    expenses = list(expense_collection.find({}, {"_id": 0}))
    return jsonify(expenses), 200

# -------------------------------
# SUMMARY REPORT BY CATEGORY
# -------------------------------
@expense_bp.route('/expenses/summary/pdf', methods=['GET'])
def expense_summary_by_date_pdf():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')

    query = {}
    if from_date and to_date:
        query["date"] = {"$gte": from_date, "$lte": to_date}

    expenses = list(expense_collection.find(query, {"_id": 0}))

    if not expenses:
        return {"error": "No expenses found"}, 404

    # ---- CATEGORY TOTAL ----
    category_totals = {}
    for exp in expenses:
        category = exp.get("category", "Others")
        amount = exp.get("amount", 0)
        category_totals[category] = category_totals.get(category, 0) + amount

    # ---- PDF ----
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(150, height - 40, "Expense Summary By Category")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, height - 65, f"From: {from_date}   To: {to_date}")

    y = height - 100

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y, "Category")
    pdf.drawString(300, y, "Total Amount")

    y -= 20
    pdf.setFont("Helvetica", 11)

    grand_total = 0

    for category, total in category_totals.items():
        pdf.drawString(60, y, category)
        pdf.drawString(300, y, f" Rs. {total}")
        grand_total += total
        y -= 18

        if y < 60:
            pdf.showPage()
            y = height - 60

    y -= 20
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(60, y, f"Grand Total: Rs. {grand_total}")

    pdf.save()
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="expense_summary_by_category.pdf",
        mimetype="application/pdf"
    )
