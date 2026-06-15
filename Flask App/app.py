from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)
# from flask import jsonify

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from config import Config

# Flask App Initialization
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = "InsurancePortalSecretKey"

db = SQLAlchemy(app)


# ==========================
# Dashboard
# ==========================
@app.route("/")
def dashboard():

    total = db.session.execute(
        text("SELECT COUNT(*) FROM Policies")
    ).scalar()

    active = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE ExpiryDate >= CAST(GETDATE() AS DATE)
        """)
    ).scalar()

    expired = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE ExpiryDate < CAST(GETDATE() AS DATE)
        """)
    ).scalar()

    added_today = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE CAST(CreatedDate AS DATE) = CAST(GETDATE() AS DATE)
        """)
    ).scalar()

    return render_template(
        "dashboard.html",
        total=total,
        active=active,
        expired=expired,
        added_today=added_today
    )


# ==========================
# View Policies
# ==========================
@app.route("/policies")
def view_policies():

    result = db.session.execute(
        text("""
            SELECT
                PolicyID,
                PolicyNumber,
                CustomerName,
                PolicyType,
                Premium,
                State,
                CASE
                    WHEN ExpiryDate >= CAST(GETDATE() AS DATE)
                    THEN 'Active'
                    ELSE 'Expired'
                END AS Status
            FROM Policies
            ORDER BY PolicyID
        """)
    )

    policies = result.mappings().all()

    return render_template(
        "policies.html",
        policies=policies
    )


# ==========================
# Add Policy
# ==========================
@app.route("/policies/add", methods=["GET", "POST"])
def add_policy():

    if request.method == "POST":

        policy_number = request.form["policy_number"]
        customer_name = request.form["customer_name"]
        policy_type = request.form["policy_type"]
        premium = float(request.form["premium"])
        effective_date = request.form["effective_date"]
        expiry_date = request.form["expiry_date"]
        state = request.form["state"]

        # Duplicate Policy Validation
        existing = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM Policies
                WHERE PolicyNumber = :policy_number
            """),
            {"policy_number": policy_number}
        ).scalar()

        if existing > 0:
            flash("Policy Number already exists.", "danger")
            return render_template("add_policy.html")

        # Premium Validation
        if premium <= 0:
            flash("Premium must be greater than zero.", "danger")
            return render_template("add_policy.html")

        # Customer Validation
        if customer_name.strip() == "":
            flash("Customer Name is required.", "danger")
            return render_template("add_policy.html")

        # Date Validation
        if expiry_date < effective_date:
            flash(
                "Expiry Date cannot be earlier than Effective Date.",
                "danger"
            )
            return render_template("add_policy.html")

        # Insert Policy
        db.session.execute(
            text("""
                INSERT INTO Policies
                (
                    PolicyNumber,
                    CustomerName,
                    PolicyType,
                    Premium,
                    EffectiveDate,
                    ExpiryDate,
                    State
                )
                VALUES
                (
                    :policy_number,
                    :customer_name,
                    :policy_type,
                    :premium,
                    :effective_date,
                    :expiry_date,
                    :state
                )
            """),
            {
                "policy_number": policy_number,
                "customer_name": customer_name,
                "policy_type": policy_type,
                "premium": premium,
                "effective_date": effective_date,
                "expiry_date": expiry_date,
                "state": state
            }
        )

        db.session.commit()

        flash("Policy added successfully.", "success")

        return redirect(url_for("view_policies"))

    return render_template("add_policy.html")

@app.route("/policies/edit/<int:policy_id>", methods=["GET", "POST"])
def edit_policy(policy_id):

    if request.method == "POST":

        policy_number = request.form["policy_number"]
        customer_name = request.form["customer_name"]
        policy_type = request.form["policy_type"]
        premium = float(request.form["premium"])
        effective_date = request.form["effective_date"]
        expiry_date = request.form["expiry_date"]
        state = request.form["state"]

        # Duplicate validation excluding current record
        existing = db.session.execute(
            text("""
                SELECT COUNT(*)
                FROM Policies
                WHERE PolicyNumber = :policy_number
                AND PolicyID <> :policy_id
            """),
            {
                "policy_number": policy_number,
                "policy_id": policy_id
            }
        ).scalar()

        if existing > 0:
            flash("Policy Number already exists.", "danger")

        elif premium <= 0:
            flash("Premium must be greater than zero.", "danger")

        elif customer_name.strip() == "":
            flash("Customer Name is required.", "danger")

        elif expiry_date < effective_date:
            flash(
                "Expiry Date cannot be earlier than Effective Date.",
                "danger"
            )

        else:
            db.session.execute(
                text("""
                    UPDATE Policies
                    SET
                        PolicyNumber = :policy_number,
                        CustomerName = :customer_name,
                        PolicyType = :policy_type,
                        Premium = :premium,
                        EffectiveDate = :effective_date,
                        ExpiryDate = :expiry_date,
                        State = :state,
                        ModifiedDate = GETDATE()
                    WHERE PolicyID = :policy_id
                """),
                {
                    "policy_number": policy_number,
                    "customer_name": customer_name,
                    "policy_type": policy_type,
                    "premium": premium,
                    "effective_date": effective_date,
                    "expiry_date": expiry_date,
                    "state": state,
                    "policy_id": policy_id
                }
            )

            db.session.commit()

            flash("Policy updated successfully.", "success")

            return redirect(url_for("view_policies"))

    result = db.session.execute(
        text("""
            SELECT *
            FROM Policies
            WHERE PolicyID = :policy_id
        """),
        {"policy_id": policy_id}
    )

    policy = result.mappings().first()

    return render_template(
        "edit_policy.html",
        policy=policy
    )

@app.route("/policies/delete/<int:policy_id>")
def delete_policy(policy_id):

    # Check if record exists
    existing = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE PolicyID = :policy_id
        """),
        {
            "policy_id": policy_id
        }
    ).scalar()

    if existing == 0:
        flash("Policy not found.", "danger")

    else:
        db.session.execute(
            text("""
                DELETE FROM Policies
                WHERE PolicyID = :policy_id
            """),
            {
                "policy_id": policy_id
            }
        )

        db.session.commit()

        flash("Policy deleted successfully.", "success")

    return redirect(url_for("view_policies"))
@app.route("/api/health")
def api_health():

    return {
        "status": "UP",
        "application": "Insurance Policy Portal",
        "database": "InsurancePortalDB"
    }, 200

@app.route("/api/policies")
def api_policies():

    result = db.session.execute(
        text("""
            SELECT
                PolicyID,
                PolicyNumber,
                CustomerName,
                PolicyType,
                Premium,
                EffectiveDate,
                ExpiryDate,
                State,
                CreatedDate,
                ModifiedDate
            FROM Policies
            ORDER BY PolicyID
        """)
    )

    policies = result.mappings().all()

    return [dict(policy) for policy in policies], 200
@app.route("/api/policies/<int:policy_id>")
def api_policy(policy_id):

    result = db.session.execute(
        text("""
            SELECT
                PolicyID,
                PolicyNumber,
                CustomerName,
                PolicyType,
                Premium,
                EffectiveDate,
                ExpiryDate,
                State,
                CreatedDate,
                ModifiedDate
            FROM Policies
            WHERE PolicyID = :policy_id
        """),
        {"policy_id": policy_id}
    )

    policy = result.mappings().first()

    if policy is None:
        return {
            "error": "Policy not found"
        }, 404

    return dict(policy), 200
@app.route("/api/policies", methods=["POST"])
def create_policy_api():

    data = request.get_json()

    required_fields = [
        "PolicyNumber",
        "CustomerName",
        "PolicyType",
        "Premium",
        "EffectiveDate",
        "ExpiryDate",
        "State"
    ]

    # Required field validation
    for field in required_fields:
        if field not in data:
            return jsonify({
                "error": f"{field} is required."
            }), 400

    # Duplicate validation
    existing = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE PolicyNumber = :policy_number
        """),
        {
            "policy_number": data["PolicyNumber"]
        }
    ).scalar()

    if existing > 0:
        return jsonify({
            "error": "Policy Number already exists."
        }), 409

    # Premium validation
    if float(data["Premium"]) <= 0:
        return jsonify({
            "error": "Premium must be greater than zero."
        }), 400

    # Date validation
    if data["ExpiryDate"] < data["EffectiveDate"]:
        return jsonify({
            "error": "Expiry Date cannot be earlier than Effective Date."
        }), 400

    db.session.execute(
        text("""
            INSERT INTO Policies
            (
                PolicyNumber,
                CustomerName,
                PolicyType,
                Premium,
                EffectiveDate,
                ExpiryDate,
                State
            )
            VALUES
            (
                :PolicyNumber,
                :CustomerName,
                :PolicyType,
                :Premium,
                :EffectiveDate,
                :ExpiryDate,
                :State
            )
        """),
        data
    )

    db.session.commit()

    return jsonify({
        "message": "Policy created successfully.",
        "policy_number": data["PolicyNumber"]
    }), 201
@app.route("/api/policies/<int:policy_id>", methods=["PUT"])
def update_policy_api(policy_id):

    data = request.get_json()

    existing_policy = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE PolicyID = :policy_id
        """),
        {"policy_id": policy_id}
    ).scalar()

    if existing_policy == 0:
        return jsonify({
            "error": "Policy not found."
        }), 404

    duplicate = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE PolicyNumber = :policy_number
              AND PolicyID <> :policy_id
        """),
        {
            "policy_number": data["PolicyNumber"],
            "policy_id": policy_id
        }
    ).scalar()

    if duplicate > 0:
        return jsonify({
            "error": "Policy Number already exists."
        }), 409

    if float(data["Premium"]) <= 0:
        return jsonify({
            "error": "Premium must be greater than zero."
        }), 400

    if data["ExpiryDate"] < data["EffectiveDate"]:
        return jsonify({
            "error": "Expiry Date cannot be earlier than Effective Date."
        }), 400

    db.session.execute(
        text("""
            UPDATE Policies
            SET
                PolicyNumber = :PolicyNumber,
                CustomerName = :CustomerName,
                PolicyType = :PolicyType,
                Premium = :Premium,
                EffectiveDate = :EffectiveDate,
                ExpiryDate = :ExpiryDate,
                State = :State,
                ModifiedDate = GETDATE()
            WHERE PolicyID = :policy_id
        """),
        {
            **data,
            "policy_id": policy_id
        }
    )

    db.session.commit()

    return jsonify({
        "message": "Policy updated successfully.",
        "policy_id": policy_id
    }), 200
@app.route("/api/policies/<int:policy_id>", methods=["DELETE"])
def delete_policy_api(policy_id):

    existing = db.session.execute(
        text("""
            SELECT COUNT(*)
            FROM Policies
            WHERE PolicyID = :policy_id
        """),
        {"policy_id": policy_id}
    ).scalar()

    if existing == 0:
        return jsonify({
            "error": "Policy not found."
        }), 404

    db.session.execute(
        text("""
            DELETE FROM Policies
            WHERE PolicyID = :policy_id
        """),
        {"policy_id": policy_id}
    )

    db.session.commit()

    return jsonify({
        "message": "Policy deleted successfully.",
        "policy_id": policy_id
    }), 200
# ==========================
# Application Entry Point
# ==========================
if __name__ == "__main__":
    app.run(debug=True)