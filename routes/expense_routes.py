from flask import Blueprint, request, jsonify, send_file
from database.mongo import expense_collection
from models.expense_model import expense_schema
import pandas as pd
from fpdf import FPDF

expense_bp = Blueprint("expense_bp", __name__)


@expense_bp.route("/expenses", methods=["POST"])
def create_expense():
    data = request.get_json()
    if not data or "expense_id" not in data:
        return jsonify({"error": "expense_id is required"}), 400
    expense = expense_schema(data)
    expense_collection.insert_one(expense)
    return jsonify({"message": "Expense added successfully", "expense_id": expense.get("expense_id")}), 201


@expense_bp.route("/expenses", methods=["GET"])
def get_all_expenses():
    expenses = list(expense_collection.find({}, {"_id": 0}))
    return jsonify(expenses), 200


@expense_bp.route("/expenses/<expense_id>", methods=["GET"])
def get_expense_by_id(expense_id):
    expense_id = expense_id.upper()
    expense = expense_collection.find_one(
        {"expense_id": expense_id},
        {"_id": 0}
    )
    if expense:
        return jsonify(expense), 200
    return jsonify({"error": "Expense not found"}), 404



@expense_bp.route("/expenses/<expense_id>", methods=["PUT"])
def update_expense(expense_id):
    data = request.get_json()
    update_data = {"$set": expense_schema(data)}
    result = expense_collection.update_one({"expense_id": expense_id}, update_data)
    if result.matched_count:
        return jsonify({"message": "Expense updated successfully"}), 200
    else:
        return jsonify({"error": "Expense not found"}), 404


@expense_bp.route("/expenses/<expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    result = expense_collection.delete_one({"expense_id": expense_id})
    if result.deleted_count:
        return jsonify({"message": "Expense deleted successfully"}), 200
    else:
        return jsonify({"error": "Expense not found"}), 404


@expense_bp.route("/debug_expenses", methods=["GET"])
def debug_expenses():
    expenses = list(expense_collection.find({}))
    return jsonify(expenses), 200


@expense_bp.route("/expenses/summary", methods=["GET"])
def summary_report():
    expenses = list(expense_collection.find({}, {"_id": 0}))
    if not expenses:
        return jsonify({"message": "No expenses found"}), 404

    df = pd.DataFrame(expenses)
    summary = df.groupby("category")["amount"].sum().reset_index()

    file_format = request.args.get("format", "").lower()

    if file_format == "excel":
        excel_file = "expense_summary.xlsx"
        summary.to_excel(excel_file, index=False)
        return send_file(excel_file, as_attachment=True)

    elif file_format == "pdf":
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, "Expense Summary by Category", ln=True, align="C")
        pdf.ln(10)
        pdf.set_font("Arial", "", 12)
        for index, row in summary.iterrows():
            pdf.cell(0, 10, f"{row['category']}: {row['amount']}", ln=True)
        pdf_file = "expense_summary.pdf"
        pdf.output(pdf_file)
        return send_file(pdf_file, as_attachment=True)

    return jsonify({"message": "Summary report generated", "summary": summary.to_dict(orient="records")}), 200
