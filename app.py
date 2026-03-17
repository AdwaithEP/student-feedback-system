from flask import Flask, request, redirect, render_template, session, url_for
from firebase_admin import credentials, firestore, initialize_app
import os, json

app = Flask(__name__)
app.secret_key = "supersecretkey123"

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"  # change this to your own password

# Firebase setup
firebase_creds = json.loads(os.environ["FIREBASE_CREDENTIALS"])
cred = credentials.Certificate(firebase_creds)
initialize_app(cred)
db = firestore.client()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    print("=== /submit route HIT ===")
    print("Form data received:", dict(request.form))

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
        return render_template("index.html", success=True)

    except Exception as e:
        print("FIRESTORE WRITE FAILED:", type(e).__name__, str(e))
        import traceback
        traceback.print_exc()
        return f"Server error: {str(e)}", 500

# Admin login
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        if request.form["username"] == ADMIN_USERNAME and \
           request.form["password"] == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            error = "Invalid username or password"
    return render_template("admin_login.html", error=error)

@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))

# Admin panel
@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    feedbacks = []
    docs = db.collection("feedbacks").stream()
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        feedbacks.append(data)
    return render_template("admin.html", feedbacks=feedbacks)

# Delete feedback
@app.route("/delete/<fid>", methods=["POST"])
def delete(fid):
    if not session.get("admin"):
        return redirect(url_for("admin_login"))
    db.collection("feedbacks").document(fid).delete()
    return redirect("/admin")

if __name__ == "__main__":
    app.run(debug=True, port=5000)
