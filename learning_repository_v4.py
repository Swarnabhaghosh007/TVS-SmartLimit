
from pathlib import Path
import sqlite3
import hashlib
import json
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "smartlimit_workflow.db"


def _now():
    return datetime.now().isoformat(timespec="seconds")


def _connect(db_path=None):
    path = Path(db_path or DEFAULT_DB_PATH)

    conn = sqlite3.connect(
        str(path),
        timeout=30
    )

    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


def _hash_identifier(value):
    if value is None:
        return None

    value = str(value).strip().lower()

    if not value:
        return None

    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


# ============================================================
# INITIALISE TABLES
# ============================================================

def init_learning_repository(db_path=None):

    conn = _connect(db_path)

    # --------------------------------------------------------
    # VERIFIED BANK CUSTOMER REPOSITORY
    # --------------------------------------------------------

    conn.execute("""
    CREATE TABLE IF NOT EXISTS bank_customer_repository (

        repository_id INTEGER PRIMARY KEY AUTOINCREMENT,

        application_id TEXT UNIQUE NOT NULL,

        added_at TEXT NOT NULL,
        last_updated_at TEXT NOT NULL,

        verified_by TEXT,

        customer_name TEXT,

        mobile_hash TEXT,
        email_hash TEXT,

        employment TEXT,
        monthly_income REAL,

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

        source_system TEXT DEFAULT 'SMARTLIMIT_V4',

        FOREIGN KEY(application_id)
            REFERENCES applications(application_id)

    )
    """)

    # --------------------------------------------------------
    # ACTUAL REPAYMENT / PERFORMANCE OUTCOME
    # --------------------------------------------------------

    conn.execute("""
    CREATE TABLE IF NOT EXISTS loan_performance_outcomes (

        application_id TEXT PRIMARY KEY,

        recorded_at TEXT NOT NULL,
        recorded_by TEXT,

        loan_disbursed INTEGER DEFAULT 0,

        disbursed_amount REAL,

        observation_months INTEGER,

        ever30_mob1_6 INTEGER,

        outcome_matured INTEGER DEFAULT 0,

        outcome_notes TEXT,

        FOREIGN KEY(application_id)
            REFERENCES applications(application_id)

    )
    """)

    # --------------------------------------------------------
    # FUTURE MODEL LEARNING QUEUE
    #
    # IMPORTANT:
    # Entry here does NOT modify live V4.
    # --------------------------------------------------------

    conn.execute("""
    CREATE TABLE IF NOT EXISTS model_learning_queue (

        application_id TEXT PRIMARY KEY,

        repository_id INTEGER,

        queued_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,

        learning_status TEXT NOT NULL,

        readiness_reason TEXT,

        approved_for_training INTEGER DEFAULT 0,

        training_batch_id TEXT,

        FOREIGN KEY(application_id)
            REFERENCES applications(application_id),

        FOREIGN KEY(repository_id)
            REFERENCES bank_customer_repository(repository_id)

    )
    """)

    conn.commit()
    conn.close()

    return True


# ============================================================
# ADD VERIFIED CUSTOMER TO BANK REPOSITORY
# ============================================================

def sync_verified_customer_to_repository(
    application_id,
    verified_by="Loan Officer",
    db_path=None
):

    conn = _connect(db_path)

    application = conn.execute(
        """
        SELECT *
        FROM applications
        WHERE application_id = ?
        """,
        (application_id,)
    ).fetchone()

    assessment = conn.execute(
        """
        SELECT *
        FROM credit_assessments
        WHERE application_id = ?
        """,
        (application_id,)
    ).fetchone()

    if application is None:
        conn.close()
        raise ValueError("Application not found.")

    if assessment is None:
        conn.close()
        raise ValueError("Credit assessment not found.")

    application = dict(application)
    assessment = dict(assessment)

    if not bool(
        assessment.get("kyc_verified", 0)
    ):
        conn.close()

        raise ValueError(
            "KYC must be verified before the customer "
            "can enter the bank repository."
        )

    now = _now()

    conn.execute(
        """
        INSERT INTO bank_customer_repository
        (
            application_id,
            added_at,
            last_updated_at,
            verified_by,

            customer_name,
            mobile_hash,
            email_hash,

            employment,
            monthly_income,

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

            source_system
        )

        VALUES
        (
            ?, ?, ?, ?,
            ?, ?, ?,
            ?, ?,
            ?, ?, ?, ?, ?,
            ?, ?,
            ?, ?, ?,
            ?, ?,
            ?,
            ?, ?,
            ?,
            ?
        )

        ON CONFLICT(application_id)
        DO UPDATE SET

            last_updated_at = excluded.last_updated_at,
            verified_by = excluded.verified_by,

            customer_name = excluded.customer_name,
            mobile_hash = excluded.mobile_hash,
            email_hash = excluded.email_hash,

            employment = excluded.employment,
            monthly_income = excluded.monthly_income,

            cibil_score = excluded.cibil_score,
            avg_emi = excluded.avg_emi,
            active_loans = excluded.active_loans,
            outstanding_balance = excluded.outstanding_balance,
            max_previous_credit = excluded.max_previous_credit,

            credit_history_months =
                excluded.credit_history_months,

            months_since_last_loan =
                excluded.months_since_last_loan,

            payment_count =
                excluded.payment_count,

            successful_payment_count =
                excluded.successful_payment_count,

            repayment_success_rate =
                excluded.repayment_success_rate,

            external_risk_score =
                excluded.external_risk_score,

            risk_gradation =
                excluded.risk_gradation,

            current_dpd =
                excluded.current_dpd,

            write_off_flag =
                excluded.write_off_flag,

            settlement_flag =
                excluded.settlement_flag,

            kyc_verified =
                excluded.kyc_verified
        """,

        (
            application_id,
            now,
            now,
            verified_by,

            application.get("customer_name"),

            _hash_identifier(
                application.get("mobile")
            ),

            _hash_identifier(
                application.get("email")
            ),

            application.get("employment"),
            application.get("monthly_income"),

            assessment.get("cibil_score"),
            assessment.get("avg_emi"),
            assessment.get("active_loans"),
            assessment.get("outstanding_balance"),
            assessment.get("max_previous_credit"),

            assessment.get("credit_history_months"),
            assessment.get("months_since_last_loan"),

            assessment.get("payment_count"),
            assessment.get("successful_payment_count"),
            assessment.get("repayment_success_rate"),

            assessment.get("external_risk_score"),
            assessment.get("risk_gradation"),

            assessment.get("current_dpd"),

            assessment.get("write_off_flag", 0),
            assessment.get("settlement_flag", 0),

            1,

            "SMARTLIMIT_V4"
        )
    )

    repo = conn.execute(
        """
        SELECT repository_id
        FROM bank_customer_repository
        WHERE application_id = ?
        """,
        (application_id,)
    ).fetchone()

    repository_id = int(
        repo["repository_id"]
    )

    conn.execute(
        """
        INSERT INTO model_learning_queue
        (
            application_id,
            repository_id,
            queued_at,
            updated_at,
            learning_status,
            readiness_reason,
            approved_for_training
        )

        VALUES
        (
            ?, ?, ?, ?, ?, ?, 0
        )

        ON CONFLICT(application_id)
        DO UPDATE SET

            repository_id =
                excluded.repository_id,

            updated_at =
                excluded.updated_at
        """,

        (
            application_id,
            repository_id,
            now,
            now,

            "AWAITING_OUTCOME",

            "Verified profile available. "
            "Waiting for mature repayment outcome."
        )
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
            now,
            "LOAN_OFFICER",
            verified_by,
            "CUSTOMER_ADDED_TO_BANK_REPOSITORY",

            json.dumps({
                "repository_id": repository_id,
                "live_model_changed": False
            })
        )
    )

    conn.commit()
    conn.close()

    return repository_id


# ============================================================
# RECORD REAL PERFORMANCE
# ============================================================

def record_loan_performance(
    application_id,
    loan_disbursed,
    disbursed_amount=None,
    observation_months=None,
    ever30_mob1_6=None,
    outcome_matured=False,
    notes=None,
    recorded_by="Bank System",
    db_path=None
):

    conn = _connect(db_path)

    now = _now()

    repository = conn.execute(
        """
        SELECT repository_id
        FROM bank_customer_repository
        WHERE application_id = ?
        """,
        (application_id,)
    ).fetchone()

    if repository is None:
        conn.close()

        raise ValueError(
            "Verified customer is not present "
            "in bank repository."
        )

    conn.execute(
        """
        INSERT OR REPLACE INTO loan_performance_outcomes
        (
            application_id,
            recorded_at,
            recorded_by,

            loan_disbursed,
            disbursed_amount,

            observation_months,
            ever30_mob1_6,

            outcome_matured,
            outcome_notes
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,

        (
            application_id,
            now,
            recorded_by,

            int(bool(loan_disbursed)),
            disbursed_amount,

            observation_months,
            ever30_mob1_6,

            int(bool(outcome_matured)),
            notes
        )
    )

    if (
        bool(loan_disbursed)
        and bool(outcome_matured)
        and ever30_mob1_6 is not None
    ):

        learning_status = (
            "READY_FOR_FUTURE_TRAINING"
        )

        reason = (
            "Verified profile and mature repayment "
            "outcome are available."
        )

    elif not bool(loan_disbursed):

        learning_status = "NOT_READY"

        reason = (
            "Loan was not disbursed; no repayment "
            "performance target exists."
        )

    else:

        learning_status = "AWAITING_OUTCOME"

        reason = (
            "Loan exists but repayment outcome "
            "is not yet mature."
        )

    conn.execute(
        """
        UPDATE model_learning_queue

        SET
            updated_at = ?,
            learning_status = ?,
            readiness_reason = ?

        WHERE application_id = ?
        """,

        (
            now,
            learning_status,
            reason,
            application_id
        )
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
            now,
            "SYSTEM",
            recorded_by,
            "PERFORMANCE_OUTCOME_UPDATED",

            json.dumps({
                "learning_status": learning_status,
                "live_model_changed": False
            })
        )
    )

    conn.commit()
    conn.close()

    return learning_status


def get_repository_profile(
    application_id,
    db_path=None
):

    conn = _connect(db_path)

    row = conn.execute(
        """
        SELECT *
        FROM bank_customer_repository
        WHERE application_id = ?
        """,
        (application_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def get_learning_status(
    application_id,
    db_path=None
):

    conn = _connect(db_path)

    row = conn.execute(
        """
        SELECT *
        FROM model_learning_queue
        WHERE application_id = ?
        """,
        (application_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


def repository_summary(db_path=None):

    conn = _connect(db_path)

    verified = conn.execute(
        """
        SELECT COUNT(*)
        FROM bank_customer_repository
        """
    ).fetchone()[0]

    ready = conn.execute(
        """
        SELECT COUNT(*)
        FROM model_learning_queue
        WHERE learning_status =
        'READY_FOR_FUTURE_TRAINING'
        """
    ).fetchone()[0]

    awaiting = conn.execute(
        """
        SELECT COUNT(*)
        FROM model_learning_queue
        WHERE learning_status =
        'AWAITING_OUTCOME'
        """
    ).fetchone()[0]

    conn.close()

    return {
        "verified_customers": int(verified),
        "ready_for_future_training": int(ready),
        "awaiting_outcome": int(awaiting),
        "live_model_auto_retraining": False
    }
