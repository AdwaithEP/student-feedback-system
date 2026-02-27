from flask import Flask, request, redirect, render_template
from firebase_admin import credentials, firestore, initialize_app

app = Flask(__name__)

# ────────────────────────────────────────────────
#   Firebase setup (do this once at startup)
# ────────────────────────────────────────────────
cred = credentials.Certificate(r"C:\LENOVO\secure-creds\new-firebase-admin.json")
initialize_app(cred)
db = firestore.client()
# ────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")  # your feedback form page

@app.route("/submit", methods=["POST"])
def submit():
    print("=== /submit route HIT ===")  # Confirm route is called
    print("Form data received:", dict(request.form))  # Show ALL incoming fields

    try:
        data = {
            "name": request.form.get("name", "(missing)"),
            "title": request.form.get("title", "(missing)"),
            "rating": request.form.get("rating", "(missing)"),
            "message": request.form.get("feedback", "(missing)"),
        }
        print("Prepared data to save:", data)

        if all(value == "(missing)" for value in data.values()):
            print("WARNING: No real data from form!")
            return "Form fields missing - check your HTML input names", 400

        doc_ref = db.collection("feedbacks").add(data)
        print(f"SUCCESS - Document written with ID: {doc_ref[1].id}")
        return redirect("/")

    except Exception as e:
        print("FIRESTORE WRITE FAILED:", type(e).__name__, str(e))
        import traceback
        traceback.print_exc()  # Full stack trace in terminal
        return f"Server error: {str(e)}", 500
# ────────────────────────────────────────────────
#   Admin panel - list all feedback
# ────────────────────────────────────────────────
@app.route("/admin")
def admin():
    feedbacks = []

    # The correct way in recent firebase-admin versions
    docs = db.collection("feedbacks").stream()

    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id               # ← very important for delete
        feedbacks.append(data)

    return render_template("admin.html", feedbacks=feedbacks)


# ────────────────────────────────────────────────
#   Delete one document
# ────────────────────────────────────────────────
@app.route("/delete/<fid>", methods=["POST"])
def delete(fid):
    db.collection("feedbacks").document(fid).delete()
    return redirect("/admin")


if __name__ == "__main__":
    app.run(debug=True, port=5000)