import csv
import io
import os
from functools import wraps

from flask import Flask, Response, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from db import execute, query_all, query_one
from ml_analysis import analyze_and_save


app = Flask(__name__)

# Development fallback only. In production, set SECRET_KEY as an environment variable.
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)

MAX_REVIEW_LENGTH = 1000


def is_logged_in():
    return "user_id" in session


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not is_logged_in():
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped_view


def safe_csv_value(value):
    """Prevent spreadsheet programs from treating exported text as formulas."""
    value = "" if value is None else str(value)
    if value.startswith(("=", "+", "-", "@")):
        return "'" + value
    return value


@app.route("/")
def review_page():
    return render_template("review.html")


@app.route("/reviews", methods=["POST"])
def submit_review():
    text = request.form.get("text", "").strip()
    stars = request.form.get("stars", "").strip()

    if len(text) < 5:
        return render_template(
            "review.html",
            error="Please write a valid review with at least 5 characters.",
            text=text,
            stars=stars,
        )

    if len(text) > MAX_REVIEW_LENGTH:
        return render_template(
            "review.html",
            error=f"Review is too long. Maximum length is {MAX_REVIEW_LENGTH} characters.",
            text=text,
            stars=stars,
        )

    try:
        stars_int = int(stars)
    except ValueError:
        return render_template(
            "review.html",
            error="Please select a star rating.",
            text=text,
            stars=stars,
        )

    if stars_int < 1 or stars_int > 5:
        return render_template(
            "review.html",
            error="Stars must be between 1 and 5.",
            text=text,
            stars=stars,
        )

    review_id = execute(
        "INSERT INTO reviews (text, stars, status) VALUES (?, ?, 'queued')",
        (text, stars_int),
    )

    try:
        analyze_and_save(review_id, text)
        success_message = "Review received and analyzed successfully."
    except Exception:
        app.logger.exception("Failed to analyze review_id=%s", review_id)
        success_message = "Review received, but analysis failed and was marked for review."

    return render_template("review.html", success=success_message, text="", stars="")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = query_one("SELECT * FROM users WHERE email = ?", (email,))
    if not user or not check_password_hash(user["password_hash"], password):
        return render_template(
            "login.html",
            error="Invalid email or password.",
            email=email,
        )

    session.clear()
    session["user_id"] = user["id"]
    session["email"] = user["email"]
    session["user_type"] = user["user_type"]

    return redirect(url_for("dashboard"))


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/analyze-queued", methods=["POST"])
@login_required
def analyze_queued():
    queued_reviews = query_all("SELECT id, text FROM reviews WHERE status = 'queued'")

    for row in queued_reviews:
        try:
            analyze_and_save(row["id"], row["text"])
        except Exception:
            app.logger.exception("Failed to analyze queued review_id=%s", row["id"])

    return redirect(url_for("dashboard"))


@app.route("/dashboard")
@login_required
def dashboard():
    total_reviews = query_one("SELECT COUNT(*) AS count FROM reviews")["count"]
    queued_reviews = query_one("SELECT COUNT(*) AS count FROM reviews WHERE status='queued'")["count"]
    processed_reviews = query_one("SELECT COUNT(*) AS count FROM reviews WHERE status='processed'")["count"]
    failed_reviews = query_one("SELECT COUNT(*) AS count FROM reviews WHERE status='failed'")["count"]

    category_rows = query_all(
        """
        SELECT c.name AS category, COUNT(*) AS count
        FROM review_analysis ra
        JOIN categories c ON c.id = ra.category_id
        GROUP BY c.name
        ORDER BY count DESC
        """
    )

    opinion_rows = query_all(
        """
        SELECT opinion, COUNT(*) AS count
        FROM review_analysis
        GROUP BY opinion
        ORDER BY count DESC
        """
    )

    table_rows = query_all(
        """
        SELECT
            c.name AS category,
            ra.opinion,
            COUNT(*) AS count,
            ROUND(AVG(ra.confidence), 2) AS avg_confidence
        FROM review_analysis ra
        JOIN categories c ON c.id = ra.category_id
        GROUP BY c.name, ra.opinion
        ORDER BY c.name, ra.opinion
        """
    )

    recent_reviews = query_all(
        """
        SELECT id, text, stars, status, created_at
        FROM reviews
        ORDER BY id DESC
        LIMIT 8
        """
    )

    return render_template(
        "dashboard.html",
        total_reviews=total_reviews,
        queued_reviews=queued_reviews,
        processed_reviews=processed_reviews,
        failed_reviews=failed_reviews,
        category_rows=category_rows,
        opinion_rows=opinion_rows,
        table_rows=table_rows,
        recent_reviews=recent_reviews,
        user_type=session.get("user_type"),
        email=session.get("email"),
    )


@app.route("/export")
@login_required
def export_csv():
    rows = query_all(
        """
        SELECT
            r.id AS review_id,
            r.text,
            r.stars,
            c.name AS category,
            ra.opinion,
            ra.confidence,
            ra.analyzed_at
        FROM review_analysis ra
        JOIN reviews r ON r.id = ra.review_id
        JOIN categories c ON c.id = ra.category_id
        ORDER BY r.id DESC
        """
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["review_id", "text", "stars", "category", "opinion", "confidence", "analyzed_at"])

    for row in rows:
        writer.writerow(
            [
                row["review_id"],
                safe_csv_value(row["text"]),
                row["stars"],
                row["category"],
                row["opinion"],
                row["confidence"],
                row["analyzed_at"],
            ]
        )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=opinion_ai_analysis.csv"},
    )


if __name__ == "__main__":
    app.run(debug=True)
