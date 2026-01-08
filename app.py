from flask import Flask, render_template
from routes.expense_routes import expense_bp

app = Flask(__name__)
app.register_blueprint(expense_bp)

@app.route("/")
def home():
    return render_template("index.html")  # This loads the frontend page

if __name__ == "__main__":
    try:
        app.run(debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("\nServer stopped gracefully")
