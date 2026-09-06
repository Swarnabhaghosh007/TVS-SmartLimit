
from pathlib import Path
import sqlite3
import uuid
import json
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent

DEFAULT_DB_PATH = (
    BASE_DIR
    / "data"
    / "smartlimit_workflow.db"
)


# ============================================================
# INTERNAL HELPERS
# ============================================================

def _now():

    return datetime.now().isoformat(
        timespec="seconds"
    )


def _connect(db_path=None):

    path = Path(
        db_path
        or
        DEFAULT_DB_PATH
    )

    path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(
        str(path),
        timeout=30
    )

    conn.row_factory = sqlite3.Row

    conn.execute(
        "PRAGMA foreign_keys = ON"
    )

    conn.execute(
        "PRAGMA journal_mode = WAL"
    )

    return conn


def _row_to_dict(row):

    if row is None:
        return None

    return dict(row)


# ============================================================
# INITIALISE DATABASE
# ============================================================

def init_db(db_path=None):

    conn = _connect(
        db_path
    )

    cursor = conn.cursor()


    # --------------------------------------------------------
    # APPLICATIONS
    # Customer-created data only
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (

        application_id TEXT PRIMARY KEY,

        created_at TEXT NOT NULL,

        updated_at TEXT NOT NULL,

        customer_name TEXT NOT NULL,

        mobile TEXT,

        email TEXT,

        date_of_birth TEXT,

        employment TEXT,

        monthly_income REAL,

        requested_amount REAL,

        requested_tenure INTEGER,

        loan_purpose TEXT,

        consent_given INTEGER DEFAULT 0,

        pan_document_name TEXT,

        aadhaar_document_name TEXT,

        kyc_uploaded INTEGER DEFAULT 0,

        status TEXT NOT NULL,

        current_owner TEXT NOT NULL

    )
    """)


    # --------------------------------------------------------
    # CREDIT ASSESSMENTS
    # Loan Officer verified/internal data
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS credit_assessments (

        application_id TEXT PRIMARY KEY,

        assessed_at TEXT,

        assessed_by TEXT,

        cibil_score REAL,

        avg_emi REAL,

        active_loans REAL,

        outstanding_balance REAL,

        max_previous_credit REAL,

        credit_history_months REAL,

        months_since_last_loan REAL,

        payment_count REAL,

        successful_payment_count REAL,

        repayment_success_rate REAL,

        external_risk_score REAL,

        risk_gradation REAL,

        current_dpd REAL,

        write_off_flag INTEGER DEFAULT 0,

        settlement_flag INTEGER DEFAULT 0,

        kyc_verified INTEGER DEFAULT 0,

        loan_officer_notes TEXT,

        FOREIGN KEY(application_id)
            REFERENCES applications(application_id)

    )
    """)


    # --------------------------------------------------------
    # MODEL RESULTS
    # SmartLimit V4 decision-support output
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS model_results (

        application_id TEXT PRIMARY KEY,

        scored_at TEXT,

        engine_version TEXT,

        policy_status TEXT,

        policy_reasons TEXT,

        offer_anchor REAL,

        relative_risk_score REAL,

        risk_segment TEXT,

        guardrail_multiplier REAL,

        smartlimit REAL,

        confidence TEXT,

        nearest_distance REAL,

        extreme_feature_count INTEGER DEFAULT 0,

        stability_grade TEXT,

        stability_review INTEGER DEFAULT 0,

        ood_review INTEGER DEFAULT 0,

        recommended_amount REAL,

        model_outcome TEXT,

        workflow_route TEXT,

        FOREIGN KEY(application_id)
            REFERENCES applications(application_id)

    )
    """)


    # --------------------------------------------------------
    # BRANCH MANAGER DECISION
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS branch_manager_decisions (

        application_id TEXT PRIMARY KEY,

        decided_at TEXT,

        decided_by TEXT,

        decision TEXT,

        approved_amount REAL,

        branch_manager_notes TEXT,

        FOREIGN KEY(application_id)
            REFERENCES applications(application_id)

    )
    """)


    # --------------------------------------------------------
    # AUDIT TRAIL
    # --------------------------------------------------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_log (

        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT,

        event_time TEXT NOT NULL,

        actor_role TEXT NOT NULL,

        actor_name TEXT,

        action TEXT NOT NULL,

        details TEXT

    )
    """)


    conn.commit()
    conn.close()

    return True


# ============================================================
# APPLICATION ID
# ============================================================

def generate_application_id():

    date_code = (
        datetime.now()
        .strftime(
            "%Y%m%d"
        )
    )

    token = (
        uuid.uuid4()
        .hex[:6]
        .upper()
    )

    return (
        f"TVS-{date_code}-{token}"
    )


# ============================================================
# AUDIT LOG
# ============================================================

def add_audit_event(
    application_id,
    actor_role,
    action,
    details=None,
    actor_name=None,
    db_path=None
):

    conn = _connect(
        db_path
    )

    conn.execute(
        """
        INSERT INTO audit_log
        (
            application_id,
            event_time,
            actor_role,
            actor_name,
            action,
            details
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            application_id,
            _now(),
            actor_role,
            actor_name,
            action,
            (
                json.dumps(
                    details
                )
                if isinstance(
                    details,
                    (
                        dict,
                        list
                    )
                )
                else details
            )
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# CREATE CUSTOMER APPLICATION
# ============================================================

def create_application(
    customer_name,
    mobile,
    email,
    date_of_birth,
    employment,
    monthly_income,
    requested_amount,
    requested_tenure,
    loan_purpose,
    consent_given,
    pan_document_name=None,
    aadhaar_document_name=None,
    db_path=None
):

    application_id = (
        generate_application_id()
    )

    now = _now()

    kyc_uploaded = int(
        bool(
            pan_document_name
            or
            aadhaar_document_name
        )
    )


    conn = _connect(
        db_path
    )


    conn.execute(
        """
        INSERT INTO applications
        (
            application_id,
            created_at,
            updated_at,
            customer_name,
            mobile,
            email,
            date_of_birth,
            employment,
            monthly_income,
            requested_amount,
            requested_tenure,
            loan_purpose,
            consent_given,
            pan_document_name,
            aadhaar_document_name,
            kyc_uploaded,
            status,
            current_owner
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            application_id,
            now,
            now,
            customer_name,
            mobile,
            email,
            str(date_of_birth),
            employment,
            float(
                monthly_income
            ),
            float(
                requested_amount
            ),
            int(
                requested_tenure
            ),
            loan_purpose,
            int(
                bool(
                    consent_given
                )
            ),
            pan_document_name,
            aadhaar_document_name,
            kyc_uploaded,
            "SUBMITTED",
            "LOAN_OFFICER"
        )
    )


    conn.commit()
    conn.close()


    add_audit_event(
        application_id=
            application_id,

        actor_role=
            "CUSTOMER",

        action=
            "APPLICATION_SUBMITTED",

        details={
            "requested_amount":
                float(
                    requested_amount
                ),

            "requested_tenure":
                int(
                    requested_tenure
                )
        },

        db_path=
            db_path
    )


    return application_id


# ============================================================
# READ APPLICATION
# ============================================================

def get_application(
    application_id,
    db_path=None
):

    conn = _connect(
        db_path
    )

    row = conn.execute(
        """
        SELECT *
        FROM applications
        WHERE application_id = ?
        """,
        (
            application_id,
        )
    ).fetchone()

    conn.close()

    return _row_to_dict(
        row
    )


# ============================================================
# LIST APPLICATIONS
# ============================================================

def list_applications(
    owner=None,
    status=None,
    db_path=None
):

    conn = _connect(
        db_path
    )


    query = """
    SELECT *
    FROM applications
    WHERE 1 = 1
    """

    params = []


    if owner is not None:

        query += """
        AND current_owner = ?
        """

        params.append(
            owner
        )


    if status is not None:

        query += """
        AND status = ?
        """

        params.append(
            status
        )


    query += """
    ORDER BY created_at DESC
    """


    rows = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()


    return [
        dict(row)
        for row in rows
    ]


# ============================================================
# UPDATE STATUS / OWNER
# ============================================================

def update_application_status(
    application_id,
    status,
    current_owner,
    actor_role,
    action,
    details=None,
    actor_name=None,
    db_path=None
):

    conn = _connect(
        db_path
    )


    conn.execute(
        """
        UPDATE applications
        SET
            status = ?,
            current_owner = ?,
            updated_at = ?
        WHERE application_id = ?
        """,
        (
            status,
            current_owner,
            _now(),
            application_id
        )
    )


    conn.commit()
    conn.close()


    add_audit_event(
        application_id=
            application_id,

        actor_role=
            actor_role,

        actor_name=
            actor_name,

        action=
            action,

        details=
            details,

        db_path=
            db_path
    )


# ============================================================
# SAVE LOAN OFFICER ASSESSMENT
# ============================================================

def save_credit_assessment(
    application_id,
    assessment,
    assessed_by="Loan Officer",
    db_path=None
):

    now = _now()


    conn = _connect(
        db_path
    )


    conn.execute(
        """
        INSERT OR REPLACE INTO credit_assessments
        (
            application_id,
            assessed_at,
            assessed_by,
            cibil_score,
            avg_emi,
            active_loans,
            outstanding_balance,
            max_previous_credit,
            credit_history_months,
            months_since_last_loan,
            payment_count,
            successful_payment_count,
            repayment_success_rate,
            external_risk_score,
            risk_gradation,
            current_dpd,
            write_off_flag,
            settlement_flag,
            kyc_verified,
            loan_officer_notes
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            application_id,
            now,
            assessed_by,

            assessment.get(
                "cibil_score"
            ),

            assessment.get(
                "avg_emi"
            ),

            assessment.get(
                "active_loans"
            ),

            assessment.get(
                "outstanding_balance"
            ),

            assessment.get(
                "max_previous_credit"
            ),

            assessment.get(
                "credit_history_months"
            ),

            assessment.get(
                "months_since_last_loan"
            ),

            assessment.get(
                "payment_count"
            ),

            assessment.get(
                "successful_payment_count"
            ),

            assessment.get(
                "repayment_success_rate"
            ),

            assessment.get(
                "external_risk_score"
            ),

            assessment.get(
                "risk_gradation"
            ),

            assessment.get(
                "current_dpd"
            ),

            int(
                bool(
                    assessment.get(
                        "write_off_flag",
                        False
                    )
                )
            ),

            int(
                bool(
                    assessment.get(
                        "settlement_flag",
                        False
                    )
                )
            ),

            int(
                bool(
                    assessment.get(
                        "kyc_verified",
                        False
                    )
                )
            ),

            assessment.get(
                "loan_officer_notes"
            )
        )
    )


    conn.commit()
    conn.close()


    add_audit_event(
        application_id=
            application_id,

        actor_role=
            "LOAN_OFFICER",

        actor_name=
            assessed_by,

        action=
            "CREDIT_ASSESSMENT_SAVED",

        db_path=
            db_path
    )


# ============================================================
# GET CREDIT ASSESSMENT
# ============================================================

def get_credit_assessment(
    application_id,
    db_path=None
):

    conn = _connect(
        db_path
    )

    row = conn.execute(
        """
        SELECT *
        FROM credit_assessments
        WHERE application_id = ?
        """,
        (
            application_id,
        )
    ).fetchone()

    conn.close()

    return _row_to_dict(
        row
    )


# ============================================================
# SAVE MODEL RESULT
# ============================================================

def save_model_result(
    application_id,
    result,
    db_path=None
):

    conn = _connect(
        db_path
    )


    policy_reasons = result.get(
        "policy_reasons"
    )


    if isinstance(
        policy_reasons,
        (
            list,
            dict
        )
    ):

        policy_reasons = (
            json.dumps(
                policy_reasons
            )
        )


    conn.execute(
        """
        INSERT OR REPLACE INTO model_results
        (
            application_id,
            scored_at,
            engine_version,
            policy_status,
            policy_reasons,
            offer_anchor,
            relative_risk_score,
            risk_segment,
            guardrail_multiplier,
            smartlimit,
            confidence,
            nearest_distance,
            extreme_feature_count,
            stability_grade,
            stability_review,
            ood_review,
            recommended_amount,
            model_outcome,
            workflow_route
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
        """,
        (
            application_id,
            _now(),

            result.get(
                "engine_version",
                "SmartLimit V4"
            ),

            result.get(
                "policy_status"
            ),

            policy_reasons,

            result.get(
                "offer_anchor"
            ),

            result.get(
                "risk_score"
            ),

            result.get(
                "risk_segment"
            ),

            result.get(
                "multiplier"
            ),

            result.get(
                "smartlimit"
            ),

            result.get(
                "confidence",
                result.get(
                    "match_confidence"
                )
            ),

            result.get(
                "nearest_distance"
            ),

            result.get(
                "extreme_feature_count",
                len(
                    result.get(
                        "extreme_features",
                        []
                    )
                )
            ),

            result.get(
                "stability_grade"
            ),

            int(
                bool(
                    result.get(
                        "stability_review",
                        False
                    )
                )
            ),

            int(
                bool(
                    result.get(
                        "ood_review",
                        False
                    )
                )
            ),

            result.get(
                "recommended_amount"
            ),

            result.get(
                "model_outcome"
            ),

            result.get(
                "workflow_route"
            )
        )
    )


    conn.commit()
    conn.close()


    add_audit_event(
        application_id=
            application_id,

        actor_role=
            "SYSTEM",

        action=
            "SMARTLIMIT_V4_SCORED",

        details={
            "smartlimit":
                result.get(
                    "smartlimit"
                ),

            "risk_segment":
                result.get(
                    "risk_segment"
                )
        },

        db_path=
            db_path
    )


# ============================================================
# GET MODEL RESULT
# ============================================================

def get_model_result(
    application_id,
    db_path=None
):

    conn = _connect(
        db_path
    )

    row = conn.execute(
        """
        SELECT *
        FROM model_results
        WHERE application_id = ?
        """,
        (
            application_id,
        )
    ).fetchone()

    conn.close()

    return _row_to_dict(
        row
    )


# ============================================================
# SAVE BRANCH MANAGER DECISION
# ============================================================

def save_branch_decision(
    application_id,
    decision,
    approved_amount=None,
    notes=None,
    decided_by="Branch Manager",
    db_path=None
):

    conn = _connect(
        db_path
    )


    conn.execute(
        """
        INSERT OR REPLACE INTO branch_manager_decisions
        (
            application_id,
            decided_at,
            decided_by,
            decision,
            approved_amount,
            branch_manager_notes
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            application_id,
            _now(),
            decided_by,
            decision,
            approved_amount,
            notes
        )
    )


    conn.commit()
    conn.close()


    add_audit_event(
        application_id=
            application_id,

        actor_role=
            "BRANCH_MANAGER",

        actor_name=
            decided_by,

        action=
            f"APPLICATION_{decision}",

        details={
            "approved_amount":
                approved_amount
        },

        db_path=
            db_path
    )


# ============================================================
# GET BRANCH DECISION
# ============================================================

def get_branch_decision(
    application_id,
    db_path=None
):

    conn = _connect(
        db_path
    )

    row = conn.execute(
        """
        SELECT *
        FROM branch_manager_decisions
        WHERE application_id = ?
        """,
        (
            application_id,
        )
    ).fetchone()

    conn.close()

    return _row_to_dict(
        row
    )


# ============================================================
# AUDIT HISTORY
# ============================================================

def get_audit_history(
    application_id,
    db_path=None
):

    conn = _connect(
        db_path
    )


    rows = conn.execute(
        """
        SELECT *
        FROM audit_log
        WHERE application_id = ?
        ORDER BY audit_id ASC
        """,
        (
            application_id,
        )
    ).fetchall()


    conn.close()


    return [
        dict(row)
        for row in rows
    ]
