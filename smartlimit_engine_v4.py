
from pathlib import Path
import pickle
import numpy as np
import pandas as pd


# ============================================================
# LOAD V4 BUNDLE
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

BUNDLE_PATH = (
    BASE_DIR
    / "smartlimit_v4_bundle.pkl"
)


with open(
    BUNDLE_PATH,
    "rb"
) as f:

    bundle = pickle.load(f)


# ============================================================
# FEATURE SCHEMA
# ============================================================

BASE_FEATURES = bundle[
    "base_features_v4"
]

NUMERIC_FEATURES = bundle[
    "numeric_features_v4"
]

CATEGORICAL_FEATURES = bundle[
    "categorical_features_v4"
]

FEATURE_MEDIANS = bundle[
    "feature_medians_v4"
]


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value, default=0.0):

    try:

        return float(value)

    except Exception:

        return float(default)


def _canonical_employment(value):

    raw = (
        str(value)
        .strip()
        .upper()
    )

    aliases = {

        "SALARIED":
            "SALARIED",

        "SELF EMPLOYED":
            "SELF_EMPLOYED",

        "SELF-EMPLOYED":
            "SELF_EMPLOYED",

        "SELF_EMPLOYED":
            "SELF_EMPLOYED",

        "AGRICULTURE":
            "AGRICULTURE",

        "OTHER":
            "OTHER"
    }

    return aliases.get(
        raw,
        raw
    )


# ============================================================
# V4 FEATURE ENGINEERING
# ============================================================

def engineer_features(df):

    x = df.copy()


    numeric_raw = [

        "INCOME",
        "AVG_EMI",
        "ACTIVE_LOANS",
        "OUTSTANDING_BALANCE",
        "MAX_PREVIOUS_CREDIT",
        "CREDIT_HISTORY_MONTHS",
        "MONTHS_SINCE_LAST_LOAN",
        "PAYMENT_COUNT",
        "SUCCESSFUL_PAYMENT_COUNT",
        "EXTERNAL_RISK_SCORE",
        "RISK_GRADATION",
        "REPAYMENT_SUCCESS_RATE"
    ]


    for col in numeric_raw:

        x[col] = pd.to_numeric(
            x[col],
            errors="coerce"
        )


    x[
        "EMI_TO_INCOME"
    ] = (

        x["AVG_EMI"]

        /

        x["INCOME"]
        .replace(
            0,
            np.nan
        )

    )


    x[
        "OUTSTANDING_TO_PREVIOUS_CREDIT"
    ] = (

        x[
            "OUTSTANDING_BALANCE"
        ]

        /

        x[
            "MAX_PREVIOUS_CREDIT"
        ]
        .replace(
            0,
            np.nan
        )

    )


    x[
        "PAYMENT_ACTIVITY_PER_MONTH"
    ] = (

        x[
            "PAYMENT_COUNT"
        ]

        /

        x[
            "CREDIT_HISTORY_MONTHS"
        ]
        .replace(
            0,
            np.nan
        )

    )


    x[
        "SUCCESSFUL_ACTIVITY_PER_MONTH"
    ] = (

        x[
            "SUCCESSFUL_PAYMENT_COUNT"
        ]

        /

        x[
            "CREDIT_HISTORY_MONTHS"
        ]
        .replace(
            0,
            np.nan
        )

    )


    x[
        "CALCULATED_REPAYMENT_RATE"
    ] = (

        x[
            "SUCCESSFUL_PAYMENT_COUNT"
        ]

        /

        x[
            "PAYMENT_COUNT"
        ]
        .replace(
            0,
            np.nan
        )

    ).clip(
        0,
        1
    )


    x[
        "UNUTILISED_PREVIOUS_CREDIT"
    ] = (

        x[
            "MAX_PREVIOUS_CREDIT"
        ]

        -

        x[
            "OUTSTANDING_BALANCE"
        ]

    )


    log_cols = [

        "INCOME",
        "AVG_EMI",
        "OUTSTANDING_BALANCE",
        "MAX_PREVIOUS_CREDIT",
        "CREDIT_HISTORY_MONTHS",
        "MONTHS_SINCE_LAST_LOAN",
        "PAYMENT_COUNT",
        "SUCCESSFUL_PAYMENT_COUNT"
    ]


    for col in log_cols:

        x[
            f"LOG_{col}"
        ] = np.log1p(

            x[col]
            .clip(
                lower=0
            )

        )


    x = x.replace(
        [
            np.inf,
            -np.inf
        ],
        np.nan
    )


    return x


# ============================================================
# DIRECT V4 AI
# ============================================================

def predict_direct_ai(profile):

    customer = pd.DataFrame(
        [profile]
    )


    x = engineer_features(
        customer
    )


    for col in NUMERIC_FEATURES:

        x[col] = (
            x[col]
            .fillna(
                FEATURE_MEDIANS[
                    col
                ]
            )
        )


    x[
        "EMPLOYMENT"
    ] = (

        x[
            "EMPLOYMENT"
        ]
        .astype(str)
        .fillna("OTHER")
    )


    model_input = x[
        NUMERIC_FEATURES
        +
        CATEGORICAL_FEATURES
    ]


    # --------------------------------------------------------
    # Capacity
    # --------------------------------------------------------

    cap_matrix = (
        bundle[
            "capacity_preprocessor_v4"
        ]
        .transform(
            model_input
        )
    )


    anchor = float(

        bundle[
            "capacity_model_v4"
        ]
        .predict(
            cap_matrix
        )[0]

    )


    # --------------------------------------------------------
    # Relative risk
    # --------------------------------------------------------

    risk_matrix = (
        bundle[
            "risk_preprocessor_v4"
        ]
        .transform(
            model_input
        )
    )


    risk_score = float(

        bundle[
            "risk_model_v4"
        ]
        .predict(
            risk_matrix
        )[0]

    )


    risk_score = float(
        np.clip(
            risk_score,
            0,
            100
        )
    )


    # --------------------------------------------------------
    # Guardrail B
    # --------------------------------------------------------

    if risk_score > 80:

        risk_segment = (
            "Highest Risk"
        )

        multiplier = 0.65


    elif risk_score > 60:

        risk_segment = (
            "High Risk"
        )

        multiplier = 0.80


    elif risk_score > 40:

        risk_segment = (
            "Medium Risk"
        )

        multiplier = 1.03


    elif risk_score > 20:

        risk_segment = (
            "Low Risk"
        )

        multiplier = 1.22


    else:

        risk_segment = (
            "Lowest Risk"
        )

        multiplier = 1.36


    guardrail = bundle[
        "guardrail_b"
    ]


    smartlimit = (
        anchor
        *
        multiplier
    )


    smartlimit = float(
        np.clip(
            smartlimit,
            guardrail[
                "min_offer"
            ],
            guardrail[
                "max_offer"
            ]
        )
    )


    rounding = float(
        guardrail[
            "rounding"
        ]
    )


    smartlimit = float(

        np.round(
            smartlimit
            /
            rounding
        )

        *
        rounding

    )


    return {

        "offer_anchor":
            anchor,

        "risk_score":
            risk_score,

        "risk_segment":
            risk_segment,

        "multiplier":
            multiplier,

        "smartlimit":
            smartlimit

    }


# ============================================================
# HISTORICAL CONFIDENCE / OOD SUPPORT
#
# IMPORTANT:
# Historical matching DOES NOT modify SmartLimit.
# ============================================================


def historical_confidence(profile):

    support = bundle[
        "historical_support"
    ]


    customer = pd.DataFrame(
        [profile]
    )


    x = customer.copy()


    numeric_cols = support[
        "numeric_cols_v3"
    ]


    # --------------------------------------------------------
    # Exact finalized V4 numeric preparation
    # --------------------------------------------------------

    for col in numeric_cols:

        x[col] = pd.to_numeric(
            x[col],
            errors="coerce"
        )


    # --------------------------------------------------------
    # Fill historical medians
    # --------------------------------------------------------

    for col in numeric_cols:

        x[col] = x[col].fillna(
            support[
                "historical_medians_v3"
            ][col]
        )


    # --------------------------------------------------------
    # Exact finalized V4 log transforms
    #
    # IMPORTANT:
    # No caps_v3 clipping is applied here.
    # --------------------------------------------------------

    for col in support[
        "log_cols_v3"
    ]:

        x[col] = np.log1p(
            x[col]
            .clip(
                lower=0
            )
        )


    # --------------------------------------------------------
    # Scale
    # --------------------------------------------------------

    scaled = (

        support[
            "profile_scaler_v3"
        ]
        .transform(
            x[
                numeric_cols
            ]
        )

    )


    # --------------------------------------------------------
    # Feature weights
    # --------------------------------------------------------

    weighted = (

        scaled

        *

        np.sqrt(
            support[
                "weights_v3"
            ]
        )

    )


    # --------------------------------------------------------
    # Risk signature
    # --------------------------------------------------------

    col_index = {

        col:
            i

        for i, col
        in enumerate(
            numeric_cols
        )

    }


    risk_signature = np.zeros(
        scaled.shape[0]
    )


    total_importance = 0.0


    for (
        feature,
        direction,
        importance
    ) in support[
        "risk_signature_terms_v3"
    ]:

        risk_signature += (

            scaled[
                :,
                col_index[
                    feature
                ]
            ]

            *

            direction

            *

            importance

        )


        total_importance += (
            importance
        )


    risk_signature = (

        risk_signature

        /

        total_importance

    )


    # --------------------------------------------------------
    # Employment
    # --------------------------------------------------------

    mapping = (
        support.get(
            "employment_mapping_v3"
        )
        or
        {}
    )


    raw_employment = (

        str(
            profile[
                "EMPLOYMENT"
            ]
        )
        .strip()
        .upper()

    )


    mapped_employment = mapping.get(
        raw_employment,
        "OTHER"
    )


    x[
        "EMPLOYMENT"
    ] = mapped_employment


    emp = (

        support[
            "employment_encoder_v3"
        ]
        .transform(
            x[
                [
                    "EMPLOYMENT"
                ]
            ]
        )

    )


    emp = (

        emp

        *

        np.sqrt(
            support[
                "employment_weight_v3"
            ]
        )

    )


    # --------------------------------------------------------
    # EXACT FINALIZED VECTOR ORDER:
    #
    # weighted
    # + risk signature
    # + employment
    # --------------------------------------------------------

    vector = np.hstack([

        weighted,

        (
            risk_signature
            .reshape(
                -1,
                1
            )

            *

            np.sqrt(
                support[
                    "risk_signature_weight_v3"
                ]
            )
        ),

        emp

    ])


    # --------------------------------------------------------
    # Historical nearest-neighbour distance
    # --------------------------------------------------------

    distances, indices = (

        support[
            "profile_matcher_v3"
        ]
        .kneighbors(
            vector
        )

    )


    nearest_distance = float(
        distances[
            0
        ][
            0
        ]
    )


    t = support[
        "distance_thresholds_v3"
    ]


    # --------------------------------------------------------
    # Similarity level
    # --------------------------------------------------------

    if nearest_distance <= t["p50"]:

        similarity_level = "High"

    elif nearest_distance <= t["p80"]:

        similarity_level = "Good"

    elif nearest_distance <= t["p95"]:

        similarity_level = "Moderate"

    elif nearest_distance <= t["p99"]:

        similarity_level = "Low"

    else:

        similarity_level = "Very Low"


    # --------------------------------------------------------
    # Feature-level extreme check
    # --------------------------------------------------------

    extreme_features = []


    bounds = bundle[
        "historical_bounds_v4"
    ]


    for col in bundle[
        "ood_features_v4"
    ]:

        value = pd.to_numeric(

            pd.Series(
                [
                    profile[
                        col
                    ]
                ]
            ),

            errors="coerce"

        ).iloc[0]


        if pd.isna(
            value
        ):

            continue


        lower = bounds[
            col
        ][
            "p005"
        ]


        upper = bounds[
            col
        ][
            "p995"
        ]


        if (

            value < lower

            or

            value > upper

        ):

            extreme_features.append(
                col
            )


    extreme_count = len(
        extreme_features
    )


    # --------------------------------------------------------
    # Exact finalized V4 confidence policy
    # --------------------------------------------------------

    if (

        nearest_distance <= t["p50"]

        and

        extreme_count == 0

    ):

        confidence = "High"


    elif (

        nearest_distance <= t["p80"]

        and

        extreme_count <= 1

    ):

        confidence = "Good"


    elif (

        nearest_distance <= t["p95"]

        and

        extreme_count <= 2

    ):

        confidence = "Moderate"


    elif (

        nearest_distance <= t["p99"]

        and

        extreme_count <= 3

    ):

        confidence = "Low"


    else:

        confidence = "Very Low"


    review_flag = bool(

        confidence
        ==
        "Very Low"

    )


    return {

        "nearest_distance":
            nearest_distance,

        "match_confidence":
            confidence,

        "similarity_level":
            similarity_level,

        "extreme_feature_count":
            extreme_count,

        "extreme_features":
            extreme_features,

        "review_flag":
            review_flag,

        "nearest_indices":
            indices[
                0
            ].tolist()

    }


# ============================================================
# STABILITY GUARD
# ============================================================

def evaluate_stability(profile):

    cfg = bundle[
        "stability_config"
    ]


    baseline = predict_direct_ai(
        profile
    )


    baseline_limit = float(
        baseline[
            "smartlimit"
        ]
    )


    baseline_risk = float(
        baseline[
            "risk_score"
        ]
    )


    baseline_segment = baseline[
        "risk_segment"
    ]


    tests = []


    # Income ±10%
    income = float(
        profile[
            "INCOME"
        ]
    )

    tests += [

        (
            "INCOME",
            income * 0.90
        ),

        (
            "INCOME",
            income * 1.10
        )

    ]


    # EMI ±10%
    emi = float(
        profile[
            "AVG_EMI"
        ]
    )

    tests += [

        (
            "AVG_EMI",
            max(
                0,
                emi * 0.90
            )
        ),

        (
            "AVG_EMI",
            emi * 1.10
        )

    ]


    # Outstanding ±10%
    outstanding = float(
        profile[
            "OUTSTANDING_BALANCE"
        ]
    )

    tests += [

        (
            "OUTSTANDING_BALANCE",
            max(
                0,
                outstanding * 0.90
            )
        ),

        (
            "OUTSTANDING_BALANCE",
            outstanding * 1.10
        )

    ]


    # Repayment ±3 percentage points
    repayment = float(
        profile[
            "REPAYMENT_SUCCESS_RATE"
        ]
    )

    tests += [

        (
            "REPAYMENT_SUCCESS_RATE",
            max(
                0,
                repayment - 3
            )
        ),

        (
            "REPAYMENT_SUCCESS_RATE",
            min(
                100,
                repayment + 3
            )
        )

    ]


    # External score ±25
    score = float(
        profile[
            "EXTERNAL_RISK_SCORE"
        ]
    )

    tests += [

        (
            "EXTERNAL_RISK_SCORE",
            score - 25
        ),

        (
            "EXTERNAL_RISK_SCORE",
            score + 25
        )

    ]


    changes = []
    segment_flips = 0


    for feature, new_value in tests:

        perturbed = (
            profile.copy()
        )


        perturbed[
            feature
        ] = new_value


        if (
            feature
            ==
            "REPAYMENT_SUCCESS_RATE"
        ):

            payment_count = int(
                perturbed[
                    "PAYMENT_COUNT"
                ]
            )


            successful_count = int(

                round(

                    payment_count

                    *

                    new_value

                    /

                    100

                )

            )


            successful_count = min(
                max(
                    successful_count,
                    0
                ),
                payment_count
            )


            perturbed[
                "SUCCESSFUL_PAYMENT_COUNT"
            ] = successful_count


        result = predict_direct_ai(
            perturbed
        )


        new_limit = float(
            result[
                "smartlimit"
            ]
        )


        change = abs(
            new_limit
            -
            baseline_limit
        )


        change_pct = (

            change

            /

            max(
                baseline_limit,
                1
            )

        )


        changes.append(
            (
                change,
                change_pct
            )
        )


        if (
            result[
                "risk_segment"
            ]
            !=
            baseline_segment
        ):

            segment_flips += 1


    largest_abs = max(
        x[0]
        for x in changes
    )


    largest_pct = max(
        x[1]
        for x in changes
    )


    boundaries = [
        20,
        40,
        60,
        80
    ]


    boundary_distance = min(

        abs(
            baseline_risk
            -
            boundary
        )

        for boundary
        in boundaries

    )


    material = bool(

        largest_abs
        >
        float(
            cfg[
                "max_absolute_movement"
            ]
        )

        and

        largest_pct
        >
        float(
            cfg[
                "max_relative_movement"
            ]
        )

    )


    boundary_sensitive = bool(

        segment_flips > 0

        and

        boundary_distance
        <=
        float(
            cfg[
                "risk_boundary_margin"
            ]
        )

    )


    review = bool(
        material
        or
        boundary_sensitive
    )


    if review:

        grade = "Review"


    elif (

        boundary_distance
        <= 2

        or

        largest_pct
        > 0.075

    ):

        grade = "Watch"


    else:

        grade = "Stable"


    return {

        "stability_grade":
            grade,

        "stability_review":
            review,

        "largest_change":
            largest_abs,

        "largest_change_pct":
            largest_pct,

        "segment_flips":
            segment_flips,

        "boundary_distance":
            boundary_distance

    }


# ============================================================
# MAIN V4 INFERENCE FUNCTION
# ============================================================

def predict_smartlimit_v4(

    income,

    avg_emi,

    active_loans,

    outstanding_balance,

    max_previous_credit,

    credit_history_months,

    months_since_last_loan,

    payment_count,

    successful_payment_count,

    external_risk_score,

    risk_gradation,

    employment

):


    if payment_count <= 0:

        repayment_rate = 0.0

    else:

        repayment_rate = (

            successful_payment_count

            /

            payment_count

            *

            100

        )


    repayment_rate = float(
        np.clip(
            repayment_rate,
            0,
            100
        )
    )


    profile = {

        "INCOME":
            income,

        "AVG_EMI":
            avg_emi,

        "ACTIVE_LOANS":
            active_loans,

        "OUTSTANDING_BALANCE":
            outstanding_balance,

        "MAX_PREVIOUS_CREDIT":
            max_previous_credit,

        "CREDIT_HISTORY_MONTHS":
            credit_history_months,

        "MONTHS_SINCE_LAST_LOAN":
            months_since_last_loan,

        "PAYMENT_COUNT":
            payment_count,

        "SUCCESSFUL_PAYMENT_COUNT":
            successful_payment_count,

        "EXTERNAL_RISK_SCORE":
            external_risk_score,

        "RISK_GRADATION":
            risk_gradation,

        "EMPLOYMENT":
            _canonical_employment(
                employment
            ),

        "REPAYMENT_SUCCESS_RATE":
            repayment_rate

    }


    ai = predict_direct_ai(
        profile
    )


    confidence = historical_confidence(
        profile
    )


    stability = evaluate_stability(
        profile
    )


    return {

        "repayment_rate":
            repayment_rate,

        "offer_anchor":
            ai[
                "offer_anchor"
            ],

        "risk_score":
            ai[
                "risk_score"
            ],

        "risk_segment":
            ai[
                "risk_segment"
            ],

        "multiplier":
            ai[
                "multiplier"
            ],

        "smartlimit":
            ai[
                "smartlimit"
            ],

        "nearest_distance":
            confidence[
                "nearest_distance"
            ],

        "match_confidence":
            confidence[
                "match_confidence"
            ],

        "similarity_level":
            confidence[
                "similarity_level"
            ],

        "extreme_features":
            confidence[
                "extreme_features"
            ],

        "ood_review":
            confidence[
                "review_flag"
            ],

        "stability_grade":
            stability[
                "stability_grade"
            ],

        "stability_review":
            stability[
                "stability_review"
            ],

        # -----------------------------------------------
        # VERY IMPORTANT:
        # V4 always generates an AI prediction.
        # Historical distance no longer hard-rejects.
        # -----------------------------------------------

        "reliable":
            True,

        "manual_review":
            bool(
                confidence[
                    "review_flag"
                ]
                or
                stability[
                    "stability_review"
                ]
            )

    }



# ============================================================
# FINAL POLICY / WORKFLOW ORCHESTRATOR — STEP 7P-D
# ============================================================

AI_REQUIRED_FIELDS = [

    "INCOME",
    "AVG_EMI",
    "ACTIVE_LOANS",
    "OUTSTANDING_BALANCE",
    "MAX_PREVIOUS_CREDIT",
    "CREDIT_HISTORY_MONTHS",
    "MONTHS_SINCE_LAST_LOAN",
    "PAYMENT_COUNT",
    "SUCCESSFUL_PAYMENT_COUNT",
    "EXTERNAL_RISK_SCORE",
    "RISK_GRADATION",
    "EMPLOYMENT",
    "REPAYMENT_SUCCESS_RATE"

]


# ------------------------------------------------------------
# Use exact packaged demo policy configuration
# ------------------------------------------------------------

_policy_container = bundle.get(
    "policy_config",
    {}
)

V4_POLICY = dict(
    _policy_container.get(
        "policy",
        _policy_container
    )
)


# Safety fallback only if bundle policy is unavailable
if not V4_POLICY:

    V4_POLICY = {

        "MIN_REQUEST_AMOUNT":
            50000,

        "MAX_REQUEST_AMOUNT":
            600000,

        "MIN_CIBIL_SCORE":
            650,

        "MIN_MONTHLY_INCOME":
            15000,

        "MAX_EMI_TO_INCOME":
            0.60,

        "CURRENT_DPD_MANUAL_REVIEW_AT":
            30,

        "WRITE_OFF_REQUIRES_REVIEW":
            True,

        "SETTLEMENT_REQUIRES_REVIEW":
            True,

        "KYC_REQUIRED":
            True,

        "CONSENT_REQUIRED":
            True,

        "LOW_CIBIL_ACTION":
            "MANUAL_REVIEW",

        "HIGH_EMI_BURDEN_ACTION":
            "MANUAL_REVIEW",

        "SEVERE_DPD_ACTION":
            "MANUAL_REVIEW",

        "ADVERSE_BUREAU_ACTION":
            "MANUAL_REVIEW",

        "FINAL_APPROVAL":
            "HUMAN_BRANCH_MANAGER"

    }


# ============================================================
# AI INPUT VALIDATION
# ============================================================

def validate_ai_inputs(
    application
):

    missing = []

    for field in AI_REQUIRED_FIELDS:

        if field not in application:

            missing.append(
                field
            )

        elif application[
            field
        ] is None:

            missing.append(
                field
            )

    return missing


# ============================================================
# POLICY GATE
# ============================================================

def evaluate_policy_gate(
    application
):

    reasons = []
    review_reasons = []
    incomplete_reasons = []
    outside_product_reasons = []


    # --------------------------------------------------------
    # A. KYC
    # --------------------------------------------------------

    if V4_POLICY[
        "KYC_REQUIRED"
    ]:

        if not application.get(
            "KYC_COMPLETED",
            False
        ):

            incomplete_reasons.append(
                "KYC verification incomplete"
            )


    # --------------------------------------------------------
    # B. CONSENT
    # --------------------------------------------------------

    if V4_POLICY[
        "CONSENT_REQUIRED"
    ]:

        if not application.get(
            "CONSENT_GIVEN",
            False
        ):

            incomplete_reasons.append(
                "Customer consent not available"
            )


    # --------------------------------------------------------
    # C. REQUESTED AMOUNT
    # --------------------------------------------------------

    requested_amount = application.get(
        "REQUESTED_AMOUNT"
    )

    if requested_amount is None:

        incomplete_reasons.append(
            "Requested loan amount missing"
        )

    else:

        requested_amount = float(
            requested_amount
        )

        if requested_amount < V4_POLICY[
            "MIN_REQUEST_AMOUNT"
        ]:

            outside_product_reasons.append(

                f"Requested amount ₹{requested_amount:,.0f} "
                f"is below configured minimum "
                f"₹{V4_POLICY['MIN_REQUEST_AMOUNT']:,.0f}"

            )

        if requested_amount > V4_POLICY[
            "MAX_REQUEST_AMOUNT"
        ]:

            outside_product_reasons.append(

                f"Requested amount ₹{requested_amount:,.0f} "
                f"is above configured maximum "
                f"₹{V4_POLICY['MAX_REQUEST_AMOUNT']:,.0f}"

            )


    # --------------------------------------------------------
    # D. CIBIL
    # --------------------------------------------------------

    cibil = application.get(
        "CIBIL_SCORE"
    )

    if cibil is None:

        incomplete_reasons.append(
            "CIBIL score not available"
        )

    else:

        cibil = float(
            cibil
        )

        if (
            cibil < 300
            or
            cibil > 900
        ):

            incomplete_reasons.append(
                "CIBIL score outside valid 300–900 range"
            )

        elif cibil < V4_POLICY[
            "MIN_CIBIL_SCORE"
        ]:

            review_reasons.append(

                f"CIBIL score {cibil:.0f} is below "
                f"configured policy threshold "
                f"{V4_POLICY['MIN_CIBIL_SCORE']}"

            )


    # --------------------------------------------------------
    # E. INCOME
    # --------------------------------------------------------

    income = application.get(
        "INCOME"
    )

    if income is None:

        incomplete_reasons.append(
            "Monthly income missing"
        )

    else:

        income = float(
            income
        )

        if income <= 0:

            incomplete_reasons.append(
                "Monthly income must be positive"
            )

        elif income < V4_POLICY[
            "MIN_MONTHLY_INCOME"
        ]:

            review_reasons.append(

                f"Monthly income ₹{income:,.0f} is below "
                f"configured threshold "
                f"₹{V4_POLICY['MIN_MONTHLY_INCOME']:,.0f}"

            )


    # --------------------------------------------------------
    # F. EMI BURDEN
    # --------------------------------------------------------

    emi = application.get(
        "AVG_EMI"
    )

    if (
        income is not None
        and
        income > 0
        and
        emi is not None
    ):

        emi = float(
            emi
        )

        if emi < 0:

            incomplete_reasons.append(
                "Average EMI cannot be negative"
            )

        else:

            emi_to_income = (
                emi
                /
                income
            )

            if emi_to_income > V4_POLICY[
                "MAX_EMI_TO_INCOME"
            ]:

                review_reasons.append(

                    f"EMI-to-income ratio "
                    f"{emi_to_income:.1%} exceeds "
                    f"configured threshold "
                    f"{V4_POLICY['MAX_EMI_TO_INCOME']:.0%}"

                )

    else:

        emi_to_income = None


    # --------------------------------------------------------
    # G. CURRENT DPD
    # --------------------------------------------------------

    current_dpd = application.get(
        "CURRENT_DPD",
        0
    )

    if current_dpd is not None:

        current_dpd = float(
            current_dpd
        )

        if current_dpd < 0:

            incomplete_reasons.append(
                "Current DPD cannot be negative"
            )

        elif current_dpd >= V4_POLICY[
            "CURRENT_DPD_MANUAL_REVIEW_AT"
        ]:

            review_reasons.append(

                f"Current DPD {current_dpd:.0f} days "
                f"requires credit review"

            )


    # --------------------------------------------------------
    # H. ADVERSE CREDIT FLAGS
    # --------------------------------------------------------

    if (

        V4_POLICY[
            "WRITE_OFF_REQUIRES_REVIEW"
        ]

        and

        application.get(
            "WRITE_OFF_FLAG",
            False
        )

    ):

        review_reasons.append(
            "Previous write-off flag present"
        )


    if (

        V4_POLICY[
            "SETTLEMENT_REQUIRES_REVIEW"
        ]

        and

        application.get(
            "SETTLEMENT_FLAG",
            False
        )

    ):

        review_reasons.append(
            "Previous settlement flag present"
        )


    # --------------------------------------------------------
    # FINAL POLICY STATUS
    # --------------------------------------------------------

    if incomplete_reasons:

        status = "INCOMPLETE"

    elif outside_product_reasons:

        status = "OUTSIDE_PRODUCT"

    elif review_reasons:

        status = "MANUAL_REVIEW"

    else:

        status = "AI_READY"


    reasons.extend(
        incomplete_reasons
    )

    reasons.extend(
        outside_product_reasons
    )

    reasons.extend(
        review_reasons
    )


    return {

        "status":
            status,

        "reasons":
            reasons,

        "incomplete_reasons":
            incomplete_reasons,

        "outside_product_reasons":
            outside_product_reasons,

        "review_reasons":
            review_reasons,

        "emi_to_income":
            emi_to_income,

        "ai_prediction_allowed":
            status in [
                "AI_READY",
                "MANUAL_REVIEW"
            ],

        "automatic_sanction":
            False,

        "final_approval":
            V4_POLICY[
                "FINAL_APPROVAL"
            ]

    }


# ============================================================
# FINAL SMARTLIMIT V4 ORCHESTRATOR
# ============================================================

def process_final_smartlimit_v4(
    application
):

    # --------------------------------------------------------
    # STEP 1 — POLICY
    # --------------------------------------------------------

    policy = evaluate_policy_gate(
        application
    )


    result = {

        "policy_status":
            policy[
                "status"
            ],

        "policy_reasons":
            policy[
                "reasons"
            ],

        "requested_amount":
            application.get(
                "REQUESTED_AMOUNT"
            ),

        "ai_prediction_generated":
            False,

        "offer_anchor":
            None,

        "risk_score":
            None,

        "risk_segment":
            None,

        "guardrail_multiplier":
            None,

        "smartlimit":
            None,

        "confidence":
            None,

        "similarity":
            None,

        "ood_review":
            False,

        "stability_grade":
            None,

        "stability_review":
            False,

        "workflow_status":
            None,

        "recommended_amount":
            None,

        "application_outcome":
            None,

        "forward_to_branch_manager":
            False,

        "final_approval_required":
            True,

        "final_approver":
            "Branch Manager",

        "automatic_sanction":
            False

    }


    # ========================================================
    # CASE 1 — INCOMPLETE
    # ========================================================

    if policy[
        "status"
    ] == "INCOMPLETE":

        result[
            "workflow_status"
        ] = "RETURN_TO_LOAN_OFFICER"

        result[
            "application_outcome"
        ] = (
            "Additional information required"
        )

        return result


    # ========================================================
    # CASE 2 — OUTSIDE PRODUCT
    # ========================================================

    if policy[
        "status"
    ] == "OUTSIDE_PRODUCT":

        result[
            "workflow_status"
        ] = "OUTSIDE_PRODUCT_POLICY"

        result[
            "application_outcome"
        ] = (
            "Requested amount is outside "
            "the configured Personal Loan range"
        )

        return result


    # ========================================================
    # STEP 2 — VERIFY AI INPUTS
    # ========================================================

    missing_ai_fields = validate_ai_inputs(
        application
    )

    if missing_ai_fields:

        result[
            "policy_status"
        ] = "INCOMPLETE"

        result[
            "policy_reasons"
        ] = [

            "Missing assessment field(s): "
            +
            ", ".join(
                missing_ai_fields
            )

        ]

        result[
            "workflow_status"
        ] = "RETURN_TO_LOAN_OFFICER"

        result[
            "application_outcome"
        ] = (
            "Additional credit information required"
        )

        return result


    # ========================================================
    # STEP 3 — MODEL PROFILE
    # ========================================================

    ai_profile = {

        field:
            application[
                field
            ]

        for field
        in AI_REQUIRED_FIELDS

    }


    # ========================================================
    # STEP 4 — DIRECT AI
    # ========================================================

    ai = predict_direct_ai(
        ai_profile
    )

    confidence = historical_confidence(
        ai_profile
    )

    stability = evaluate_stability(
        ai_profile
    )


    result[
        "ai_prediction_generated"
    ] = True

    result[
        "offer_anchor"
    ] = ai[
        "offer_anchor"
    ]

    result[
        "risk_score"
    ] = ai[
        "risk_score"
    ]

    result[
        "risk_segment"
    ] = ai[
        "risk_segment"
    ]

    result[
        "guardrail_multiplier"
    ] = ai[
        "multiplier"
    ]

    result[
        "smartlimit"
    ] = ai[
        "smartlimit"
    ]

    result[
        "confidence"
    ] = confidence[
        "match_confidence"
    ]

    result[
        "similarity"
    ] = confidence[
        "similarity_level"
    ]

    result[
        "ood_review"
    ] = confidence[
        "review_flag"
    ]

    result[
        "stability_grade"
    ] = stability[
        "stability_grade"
    ]

    result[
        "stability_review"
    ] = stability[
        "stability_review"
    ]


    # ========================================================
    # STEP 5 — POLICY MANUAL REVIEW
    # ========================================================

    if policy[
        "status"
    ] == "MANUAL_REVIEW":

        result[
            "workflow_status"
        ] = (
            "LOAN_OFFICER_POLICY_REVIEW"
        )

        result[
            "application_outcome"
        ] = (
            "Manual credit verification required"
        )

        result[
            "recommended_amount"
        ] = ai[
            "smartlimit"
        ]

        return result


    # ========================================================
    # STEP 6 — OOD REVIEW
    # ========================================================

    if confidence[
        "review_flag"
    ]:

        result[
            "workflow_status"
        ] = (
            "LOAN_OFFICER_PROFILE_REVIEW"
        )

        result[
            "application_outcome"
        ] = (
            "Indicative SmartLimit available; "
            "unusual profile requires verification"
        )

        result[
            "recommended_amount"
        ] = ai[
            "smartlimit"
        ]

        return result


    # ========================================================
    # STEP 7 — STABILITY REVIEW
    # ========================================================

    if stability[
        "stability_review"
    ]:

        result[
            "workflow_status"
        ] = (
            "LOAN_OFFICER_STABILITY_REVIEW"
        )

        result[
            "application_outcome"
        ] = (
            "Indicative SmartLimit available; "
            "prediction is locally sensitive and "
            "requires verification"
        )

        result[
            "recommended_amount"
        ] = ai[
            "smartlimit"
        ]

        return result


    # ========================================================
    # STEP 8 — REQUEST COMPARISON
    # ========================================================

    requested = float(
        application[
            "REQUESTED_AMOUNT"
        ]
    )

    smartlimit = float(
        ai[
            "smartlimit"
        ]
    )


    if smartlimit >= requested:

        result[
            "application_outcome"
        ] = (
            "FULL_REQUEST_CAN_BE_CONSIDERED"
        )

        result[
            "recommended_amount"
        ] = requested

    else:

        result[
            "application_outcome"
        ] = (
            "LOWER_AMOUNT_RECOMMENDED"
        )

        result[
            "recommended_amount"
        ] = smartlimit


    result[
        "workflow_status"
    ] = "FORWARD_TO_BRANCH_MANAGER"

    result[
        "forward_to_branch_manager"
    ] = True


    return result

