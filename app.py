
import streamlit as st
import textwrap
import pandas as pd
import numpy as np
import cloudpickle
import time
import os
import base64
from datetime import date
from smartlimit_engine_v4 import predict_smartlimit_v4, process_final_smartlimit_v4

from workflow_store_v4 import (
    init_db,
    create_application,
    get_application,
    list_applications,
    save_credit_assessment,
    get_credit_assessment,
    save_model_result,
    get_model_result,
    update_application_status,
    get_audit_history,
    save_branch_decision,
    get_branch_decision
)

init_db()


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="TVS SmartLimit",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="collapsed"
)



# ============================================================
# SAFE HTML RENDERER
# Prevents indented HTML from appearing as code blocks
# ============================================================

_original_streamlit_markdown = st.markdown

def _smartlimit_markdown(body, *args, **kwargs):
    if isinstance(body, str) and "<" in body and ">" in body:
        body = textwrap.dedent(body).strip()
    return _original_streamlit_markdown(body, *args, **kwargs)

st.markdown = _smartlimit_markdown

# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background:
            linear-gradient(
                180deg,
                #f6f9fd 0%,
                #ffffff 100%
            );
    }

    .main .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        background:
            linear-gradient(
                135deg,
                #102f5e 0%,
                #175394 100%
            );
        color: white;
        padding: 28px 32px;
        border-radius: 18px;
        margin-bottom: 24px;
        box-shadow:
            0 10px 30px
            rgba(15,47,92,0.16);
    }

    .hero-title {
        font-size: 38px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .hero-subtitle {
        font-size: 16px;
        opacity: 0.92;
    }

    .result-card {
        background:
            linear-gradient(
                135deg,
                #eef6ff 0%,
                #ffffff 100%
            );
        border: 1px solid #cfe0f3;
        border-radius: 20px;
        padding: 28px;
        margin-top: 16px;
        box-shadow:
            0 8px 28px
            rgba(17,58,104,0.08);
    }

    .result-label {
        font-size: 14px;
        font-weight: 700;
        color: #60768d;
        letter-spacing: 0.4px;
    }

    .result-value {
        font-size: 48px;
        font-weight: 800;
        color: #123f75;
        margin-top: 4px;
        margin-bottom: 5px;
    }

    .eligible-box {
        background: #edf9f1;
        border-left: 5px solid #278454;
        padding: 15px 18px;
        border-radius: 9px;
        margin-top: 18px;
    }

    .adjusted-box {
        background: #fff8e8;
        border-left: 5px solid #d3941d;
        padding: 15px 18px;
        border-radius: 9px;
        margin-top: 18px;
    }

    .manual-box {
        background: #fff3f1;
        border-left: 5px solid #b74c3c;
        padding: 18px;
        border-radius: 10px;
        margin-top: 18px;
    }

    .info-strip {
        background: #eef5fb;
        border-radius: 12px;
        padding: 14px 17px;
        margin-bottom: 18px;
        color: #34516d;
    }

    .small-note {
        color: #708091;
        font-size: 12px;
    }

    div.stButton > button {
        width: 100%;
        min-height: 3.2em;
        border-radius: 10px;
        font-weight: 700;
    }

    

    /* ===============================================
       TVS SMARTLIMIT PROFESSIONAL HEADER
       =============================================== */

    .tvs-brand-shell {
        width: 100%;
        box-sizing: border-box;

        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 28px;

        background:
            linear-gradient(
                120deg,
                #ffffff 0%,
                #f4f8fd 52%,
                #edf4fc 100%
            );

        border:
            1px solid #dce6f2;

        border-radius: 22px;

        padding:
            24px 30px;

        margin-bottom:
            18px;

        box-shadow:
            0 12px 34px
            rgba(18, 57, 104, 0.10);
    }


    .tvs-brand-left {
        display: flex;
        align-items: center;
        gap: 26px;
        min-width: 0;
    }


    .tvs-logo-panel {
        width: 165px;
        min-width: 165px;
        height: 92px;

        display: flex;
        align-items: center;
        justify-content: center;

        background: #ffffff;

        border:
            1px solid #e2e9f2;

        border-radius:
            16px;

        padding:
            12px 16px;

        box-shadow:
            0 5px 16px
            rgba(18, 57, 104, 0.06);
    }


    .tvs-logo-panel img {
        width: 100%;
        height: 100%;
        object-fit: contain;
    }


    .tvs-logo-fallback {
        font-size: 18px;
        font-weight: 800;
        color: #16457f;
        text-align: center;
        line-height: 1.2;
    }


    .tvs-brand-copy {
        min-width: 0;
    }


    .tvs-brand-eyebrow {
        font-size: 13px;
        font-weight: 800;

        letter-spacing:
            1.6px;

        color:
            #54708f;

        margin-bottom:
            5px;
    }


    .tvs-brand-title {
        margin: 0;

        font-size:
            38px;

        line-height:
            1.08;

        font-weight:
            800;

        color:
            #123c70;

        letter-spacing:
            -0.8px;
    }


    .tvs-brand-subtitle {
        margin-top:
            8px;

        font-size:
            16px;

        line-height:
            1.45;

        color:
            #5d7186;

        max-width:
            620px;
    }


    .tvs-ai-pill {
        flex-shrink: 0;

        background:
            #143f74;

        color:
            #ffffff;

        font-size:
            13px;

        font-weight:
            700;

        padding:
            10px 16px;

        border-radius:
            999px;

        box-shadow:
            0 5px 14px
            rgba(20, 63, 116, 0.14);
    }


    .tvs-intro-card {
        background:
            linear-gradient(
                90deg,
                #eef5fc 0%,
                #f7faff 100%
            );

        border-left:
            5px solid #1c5795;

        border-radius:
            12px;

        padding:
            15px 18px;

        margin:
            0 0 28px 0;

        font-size:
            15px;

        line-height:
            1.55;

        color:
            #405e79;
    }


    @media
    (max-width: 800px) {

        .tvs-brand-shell {
            flex-direction: column;
            align-items: stretch;
        }

        .tvs-brand-left {
            flex-direction: column;
            align-items: flex-start;
        }

        .tvs-logo-panel {
            width: 145px;
        }

        .tvs-ai-pill {
            width: fit-content;
        }

        .tvs-brand-title {
            font-size: 31px;
        }
    }




    /* ===============================================
       FINAL SMARTLIMIT UI POLISH
       =============================================== */


    /* Main page */
    .main .block-container {
        max-width: 1180px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }


    /* -----------------------------------------------
       FORM
       ----------------------------------------------- */

    div[data-testid="stForm"] {

        background:
            rgba(255, 255, 255, 0.96);

        border:
            1px solid #dde7f1;

        border-radius:
            20px;

        padding:
            28px 30px 30px 30px;

        box-shadow:
            0 10px 28px
            rgba(17, 54, 94, 0.07);

        margin-top:
            10px;

        margin-bottom:
            28px;
    }


    div[data-testid="stForm"] h3 {

        color:
            #173f70;

        font-weight:
            750;

        letter-spacing:
            -0.2px;

        margin-top:
            4px;

        margin-bottom:
            20px;
    }


    /* Labels */
    div[data-testid="stForm"] label {

        color:
            #27435f !important;

        font-weight:
            600 !important;

        font-size:
            14px !important;
    }


    /* Input fields */
    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {

        border-radius:
            10px !important;

        border-color:
            #d6e1ed !important;

        background:
            #fbfdff !important;
    }


    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input {

        border-radius:
            10px !important;
    }


    /* Divider */
    hr {

        border:
            none;

        border-top:
            1px solid #e6edf5;

        margin:
            25px 0;
    }


    /* Primary CTA */
    div[data-testid="stFormSubmitButton"] button {

        width:
            100%;

        min-height:
            54px;

        border-radius:
            12px;

        border:
            none;

        background:
            linear-gradient(
                90deg,
                #123d72,
                #1c5a9b
            );

        color:
            white;

        font-size:
            16px;

        font-weight:
            750;

        letter-spacing:
            0.25px;

        box-shadow:
            0 8px 20px
            rgba(24, 76, 132, 0.18);

        transition:
            0.2s ease;
    }


    div[data-testid="stFormSubmitButton"] button:hover {

        transform:
            translateY(-1px);

        box-shadow:
            0 10px 24px
            rgba(24, 76, 132, 0.24);
    }



    /* -----------------------------------------------
       RESULT HERO
       ----------------------------------------------- */

    .smart-result-shell {

        background:
            linear-gradient(
                135deg,
                #ffffff 0%,
                #f3f8fe 100%
            );

        border:
            1px solid #d8e5f2;

        border-radius:
            22px;

        padding:
            30px 32px;

        margin:
            18px 0 22px 0;

        box-shadow:
            0 14px 34px
            rgba(18, 59, 103, 0.09);
    }


    .smart-result-top {

        display:
            flex;

        justify-content:
            space-between;

        align-items:
            flex-start;

        gap:
            20px;
    }


    .smart-result-kicker {

        font-size:
            12px;

        font-weight:
            800;

        color:
            #647b92;

        letter-spacing:
            1.4px;

        text-transform:
            uppercase;

        margin-bottom:
            6px;
    }


    .smart-result-title {

        font-size:
            17px;

        color:
            #344e67;

        font-weight:
            650;

        margin-bottom:
            2px;
    }


    .smart-result-amount {

        font-size:
            52px;

        line-height:
            1.05;

        font-weight:
            850;

        color:
            #123f75;

        letter-spacing:
            -1px;

        margin-top:
            4px;
    }


    .smart-result-badge {

        background:
            #eaf2fb;

        color:
            #174b83;

        border:
            1px solid #d2e2f3;

        border-radius:
            999px;

        padding:
            9px 14px;

        font-size:
            12px;

        font-weight:
            750;

        white-space:
            nowrap;
    }


    /* Approved / requested within limit */
    .smart-decision-success {

        margin-top:
            23px;

        background:
            #ecf8f1;

        border:
            1px solid #ccead8;

        border-left:
            5px solid #288a56;

        border-radius:
            12px;

        padding:
            15px 17px;

        color:
            #24543b;

        line-height:
            1.5;
    }


    /* Adjusted */
    .smart-decision-warning {

        margin-top:
            23px;

        background:
            #fff8e9;

        border:
            1px solid #f0deb6;

        border-left:
            5px solid #d5971f;

        border-radius:
            12px;

        padding:
            15px 17px;

        color:
            #72551b;

        line-height:
            1.5;
    }


    .smart-decision-heading {

        font-size:
            15px;

        font-weight:
            800;

        margin-bottom:
            3px;
    }


    .smart-decision-copy {

        font-size:
            14px;
    }



    /* -----------------------------------------------
       METRICS
       ----------------------------------------------- */

    div[data-testid="stMetric"] {

        background:
            #ffffff;

        border:
            1px solid #e0e8f1;

        border-radius:
            14px;

        padding:
            15px 17px;

        min-height:
            112px;

        box-shadow:
            0 5px 16px
            rgba(19, 57, 97, 0.05);
    }


    div[data-testid="stMetricLabel"] {

        color:
            #65788b;

        font-weight:
            650;
    }


    div[data-testid="stMetricValue"] {

        color:
            #163e70;

        font-weight:
            750;
    }



    /* -----------------------------------------------
       EXPLANATION / EXPANDER
       ----------------------------------------------- */

    div[data-testid="stExpander"] {

        border:
            1px solid #dde7f1;

        border-radius:
            14px;

        background:
            #ffffff;
    }


    /* Caption */
    div[data-testid="stCaptionContainer"] {

        color:
            #738496;
    }



    /* -----------------------------------------------
       MANUAL REVIEW
       ----------------------------------------------- */

    .manual-review-card {

        background:
            linear-gradient(
                135deg,
                #fff9f6,
                #fffdfc
            );

        border:
            1px solid #efd8d1;

        border-left:
            6px solid #b84e3e;

        border-radius:
            16px;

        padding:
            22px 24px;

        margin:
            18px 0;

        box-shadow:
            0 8px 20px
            rgba(108, 51, 42, 0.06);
    }


    .manual-review-title {

        font-size:
            20px;

        font-weight:
            800;

        color:
            #833b31;

        margin-bottom:
            8px;
    }


    .manual-review-copy {

        font-size:
            14px;

        line-height:
            1.6;

        color:
            #654c47;
    }



    /* -----------------------------------------------
       REMOVE STREAMLIT CLUTTER
       ----------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }




    /* ==================================================
       TVS SMARTLIMIT — NATIVE STREAMLIT UI
       ================================================== */


    /* Overall page */
    .main .block-container {

        max-width:
            1220px;

        padding-top:
            1.2rem;

        padding-bottom:
            4rem;
    }


    /* --------------------------------------------------
       TOP BRAND BAR
       -------------------------------------------------- */

    .st-key-smartlimit_topbar {

        background:
            rgba(
                255,
                255,
                255,
                0.98
            );

        border:
            1px solid #e2eaf3;

        border-radius:
            18px;

        padding:
            15px 22px;

        margin-bottom:
            18px;

        box-shadow:
            0 5px 20px
            rgba(
                18,
                57,
                104,
                0.06
            );
    }


    .st-key-smartlimit_topbar img {

        max-height:
            58px;

        object-fit:
            contain;
    }


    .st-key-smartlimit_topbar h3 {

        color:
            #123f75;

        margin-bottom:
            0 !important;

        font-weight:
            800;

        letter-spacing:
            -0.4px;
    }


    .st-key-smartlimit_topbar p {

        color:
            #687b90;

        margin-top:
            0 !important;
    }



    /* --------------------------------------------------
       HERO CARD
       -------------------------------------------------- */

    .st-key-smartlimit_hero {

        background:
            linear-gradient(
                115deg,
                #f4f9ff 0%,
                #eaf4ff 52%,
                #edf7ff 100%
            );

        border:
            1px solid #d7e7f7;

        border-radius:
            24px;

        padding:
            28px 32px;

        margin-bottom:
            28px;

        box-shadow:
            0 12px 32px
            rgba(
                18,
                61,
                112,
                0.08
            );

        overflow:
            hidden;
    }


    .st-key-smartlimit_hero h1 {

        color:
            #103d75;

        font-size:
            44px;

        line-height:
            1.07;

        font-weight:
            850;

        letter-spacing:
            -1.3px;

        margin-top:
            8px;

        margin-bottom:
            13px;
    }


    .st-key-smartlimit_hero h3 {

        color:
            #144577;

        font-weight:
            800;
    }


    .st-key-smartlimit_hero p {

        color:
            #506a83;

        line-height:
            1.55;

        font-size:
            15px;
    }



    /* --------------------------------------------------
       HERO FEATURE BOXES
       -------------------------------------------------- */

    .st-key-feature_fast,
    .st-key-feature_personalised,
    .st-key-feature_trusted {

        background:
            rgba(
                255,
                255,
                255,
                0.70
            );

        border:
            1px solid
            rgba(
                210,
                227,
                244,
                0.9
            );

        border-radius:
            14px;

        padding:
            11px 13px;

        min-height:
            88px;
    }



    /* --------------------------------------------------
       RIGHT-SIDE HERO PANEL
       -------------------------------------------------- */

    .st-key-hero_right_panel {

        background:
            linear-gradient(
                145deg,
                #ffffff 0%,
                #eef6ff 100%
            );

        border:
            1px solid #d7e6f5;

        border-radius:
            20px;

        padding:
            19px;

        box-shadow:
            0 8px 22px
            rgba(
                21,
                68,
                119,
                0.07
            );
    }


    .st-key-hero_right_panel h2 {

        color:
            #12477d;

        line-height:
            1.2;

        font-weight:
            800;

        margin-bottom:
            18px;
    }


    .st-key-benefit_1,
    .st-key-benefit_2,
    .st-key-benefit_3 {

        background:
            white;

        border:
            1px solid #dfebf6;

        border-radius:
            12px;

        padding:
            9px 12px;

        margin-bottom:
            8px;
    }



    /* --------------------------------------------------
       LOAN FORM
       -------------------------------------------------- */

    div[data-testid="stForm"] {

        background:
            #ffffff;

        border:
            1px solid #dce7f2;

        border-radius:
            22px;

        padding:
            30px 32px;

        box-shadow:
            0 10px 28px
            rgba(
                17,
                54,
                94,
                0.07
            );
    }


    div[data-testid="stForm"] h3 {

        color:
            #123f75;

        font-weight:
            800;
    }


    /* Remove Streamlit menu */
    #MainMenu {

        visibility:
            hidden;
    }


    footer {

        visibility:
            hidden;
    }


    @media (
        max-width: 800px
    ) {

        .st-key-smartlimit_hero h1 {

            font-size:
                34px;
        }

        .st-key-smartlimit_hero {

            padding:
                20px;
        }
    }


</style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DEPLOYMENT BUNDLE
# ============================================================

@st.cache_resource
def load_bundle():

    path = os.path.join(
        os.path.dirname(__file__),
        "smartlimit_bundle (2).pkl"
    )

    with open(
        path,
        "rb"
    ) as f:

        return cloudpickle.load(f)


bundle = load_bundle()


# ============================================================
# HELPERS
# ============================================================

def indian_currency(value):

    value = int(
        round(
            float(value)
        )
    )

    s = str(value)

    if len(s) <= 3:
        return "₹" + s

    last_three = s[-3:]
    rest = s[:-3]

    groups = []

    while len(rest) > 2:

        groups.insert(
            0,
            rest[-2:]
        )

        rest = rest[:-2]

    if rest:
        groups.insert(
            0,
            rest
        )

    return (
        "₹"
        + ",".join(groups)
        + ","
        + last_three
    )


def canonical_employment(value):

    mapping = bundle.get(
        "employment_mapping_v3",
        {}
    )

    key = (
        str(value)
        .strip()
        .upper()
    )

    return mapping.get(
        key,
        "OTHER"
    )


# ============================================================
# DEPLOYMENT NUMERIC PREPARATION
# ============================================================

def prepare_numeric(df):

    out = pd.DataFrame(
        index=df.index
    )


    for col in bundle[
        "log_cols_v3"
    ]:

        low, high = (
            bundle[
                "caps_v3"
            ][col]
        )


        values = (
            pd.to_numeric(
                df[col],
                errors="coerce"
            )
            .fillna(
                bundle[
                    "historical_medians_v3"
                ][col]
            )
            .clip(
                lower=max(
                    0,
                    low
                ),
                upper=high
            )
        )


        out[col] = (
            np.log1p(
                values
            )
        )


    out[
        "REPAYMENT_SUCCESS_RATE"
    ] = (
        pd.to_numeric(
            df[
                "REPAYMENT_SUCCESS_RATE"
            ],
            errors="coerce"
        )
        .fillna(
            bundle[
                "historical_medians_v3"
            ][
                "REPAYMENT_SUCCESS_RATE"
            ]
        )
        .clip(
            0,
            100
        )
    )


    out[
        "EXTERNAL_RISK_SCORE"
    ] = (
        pd.to_numeric(
            df[
                "EXTERNAL_RISK_SCORE"
            ],
            errors="coerce"
        )
        .fillna(
            bundle[
                "historical_medians_v3"
            ][
                "EXTERNAL_RISK_SCORE"
            ]
        )
    )


    out[
        "RISK_GRADATION"
    ] = (
        pd.to_numeric(
            df[
                "RISK_GRADATION"
            ],
            errors="coerce"
        )
        .fillna(
            bundle[
                "historical_medians_v3"
            ][
                "RISK_GRADATION"
            ]
        )
    )


    return out


# ============================================================
# AUTOMATIC HISTORICAL PROFILE MATCHER
# ============================================================

def predict_smartlimit(

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


    # --------------------------------------------------------
    # Repayment success rate
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Customer matching frame
    # --------------------------------------------------------

    customer = pd.DataFrame({

        "INCOME":
            [income],

        "AVG_EMI":
            [avg_emi],

        "ACTIVE_LOANS":
            [active_loans],

        "OUTSTANDING_BALANCE":
            [outstanding_balance],

        "MAX_PREVIOUS_CREDIT":
            [max_previous_credit],

        "CREDIT_HISTORY_MONTHS":
            [credit_history_months],

        "MONTHS_SINCE_LAST_LOAN":
            [months_since_last_loan],

        "PAYMENT_COUNT":
            [payment_count],

        "SUCCESSFUL_PAYMENT_COUNT":
            [successful_payment_count],

        "REPAYMENT_SUCCESS_RATE":
            [repayment_rate],

        "EXTERNAL_RISK_SCORE":
            [external_risk_score],

        "RISK_GRADATION":
            [risk_gradation],

        "EMPLOYMENT":
            [
                canonical_employment(
                    employment
                )
            ]
    })


    # --------------------------------------------------------
    # Numeric encoding
    # --------------------------------------------------------

    numeric = (
        prepare_numeric(
            customer
        )
    )


    scaled = (
        bundle[
            "profile_scaler_v3"
        ]
        .transform(
            numeric[
                bundle[
                    "numeric_cols_v3"
                ]
            ]
        )
    )


    weighted = (

        scaled

        *

        np.sqrt(
            bundle[
                "weights_v3"
            ]
        )
    )


    # --------------------------------------------------------
    # Risk signature
    # --------------------------------------------------------

    col_index = {

        col: i

        for i, col in enumerate(
            bundle[
                "numeric_cols_v3"
            ]
        )
    }


    risk_signature = np.zeros(
        scaled.shape[0]
    )

    total_importance = 0


    for (
        feature,
        direction,
        importance
    ) in bundle[
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

          # ============================================================
            *
            importance
        )

        total_importance += (
            importance
        )


    # --------------------------------------------------------
    # Complete risk signature
    # --------------------------------------------------------

    risk_signature = (
        risk_signature
        /
        total_importance
    )


    # --------------------------------------------------------
    # Employment encoding
    # --------------------------------------------------------

    employment_matrix = (
        bundle[
            "employment_encoder_v3"
        ]
        .transform(
            customer[
                ["EMPLOYMENT"]
            ]
        )
        *
        np.sqrt(
            bundle[
                "employment_weight_v3"
            ]
        )
    )


    # --------------------------------------------------------
    # Final customer similarity vector
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
                bundle[
                    "risk_signature_weight_v3"
                ]
            )
        ),

        employment_matrix

    ])


    # --------------------------------------------------------
    # Retrieve 25 nearest historical analogues
    # --------------------------------------------------------

    distances, indices = (
        bundle[
            "profile_matcher_v3"
        ]
        .kneighbors(
            vector
        )
    )


    distances = distances[0]
    indices = indices[0]


    nearest_distance = float(
        distances[0]
    )


    thresholds = (
        bundle[
            "distance_thresholds_v3"
        ]
    )


    # --------------------------------------------------------
    # Matching confidence
    # --------------------------------------------------------

    if nearest_distance <= thresholds[
        "p50"
    ]:

        confidence = "High"


    elif nearest_distance <= thresholds[
        "p80"
    ]:

        confidence = "Medium"


    elif nearest_distance <= thresholds[
        "p95"
    ]:

        confidence = "Low"


    elif nearest_distance <= thresholds[
        "p99"
    ]:

        confidence = "Very Low"


    else:

        confidence = "Out of Range"


    reliable = (
        nearest_distance
        <=
        thresholds[
            "p95"
        ]
    )


    # --------------------------------------------------------
    # Historical neighbours
    # --------------------------------------------------------

    neighbours = (
        bundle[
            "match_reference_v3"
        ]
        .iloc[
            indices
        ]
        .copy()
    )


    neighbours[
        "MATCH_DISTANCE"
    ] = distances


    # --------------------------------------------------------
    # Similarity weighting
    # --------------------------------------------------------

    raw_weights = (
        1
        /
        (
            distances
            +
            1e-6
        ) ** 2
    )


    weights = (
        raw_weights
        /
        raw_weights.sum()
    )


    # --------------------------------------------------------
    # Frozen-model offer anchor
    # --------------------------------------------------------

    anchor = float(
        np.sum(
            neighbours[
                "FROZEN_OFFER_ANCHOR"
            ].values
            *
            weights
        )
    )


    # --------------------------------------------------------
    # Frozen-model risk
    # --------------------------------------------------------

    risk_score = float(
        np.sum(
            neighbours[
                "FROZEN_RISK_SCORE"
            ].values
            *
            weights
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


    # --------------------------------------------------------
    # Final SmartLimit
    # --------------------------------------------------------

    smartlimit = (
        anchor
        *
        multiplier
    )


    smartlimit = np.clip(
        smartlimit,
        bundle[
            "min_offer"
        ],
        bundle[
            "max_offer"
        ]
    )


    smartlimit = (
        np.round(
            smartlimit
            /
            bundle[
                "rounding"
            ]
        )
        *
        bundle[
            "rounding"
        ]
    )


    smartlimit = float(
        np.clip(
            smartlimit,
            bundle[
                "min_offer"
            ],
            bundle[
                "max_offer"
            ]
        )
    )


    return {

        "repayment_rate":
            repayment_rate,

        "nearest_distance":
            nearest_distance,

        "match_confidence":
            confidence,

        "reliable":
            reliable,

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
# SMARTLIMIT ROLE NAVIGATION — STEP 7L
# ============================================================

st.markdown(
    """
    <div style="
        margin-top: 2px;
        margin-bottom: 5px;
        color: #60758b;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.7px;
        text-transform: uppercase;
    ">
        SmartLimit Workspace
    </div>
    """,
    unsafe_allow_html=True
)


selected_role = st.radio(

    "SmartLimit Workspace",

    [
        "Customer Portal",
        "Loan Officer Workspace",
        "Branch Manager Console"
    ],

    horizontal=True,

    label_visibility="collapsed",

    key="smartlimit_role_navigation"

)


st.write("")


# ============================================================
# CUSTOMER PORTAL
#
# IMPORTANT:
# Existing customer UI continues below WITHOUT redesign.
# ============================================================

if selected_role == "Customer Portal":

    # ============================================================
    # TVS SMARTLIMIT — SAFE NATIVE HEADER
    # ============================================================


    # ------------------------------------------------------------
    # TOP BRAND BAR
    # ------------------------------------------------------------

    logo_col, brand_col, badge_col = st.columns(
        [1.5, 5.8, 1.7],
        vertical_alignment="center"
    )


    with logo_col:

        st.image(
            os.path.join(
                os.path.dirname(__file__),
                "tvs_credit_logo.png"
            ),
            width=180
        )


    with brand_col:

        st.markdown(
            "## TVS SmartLimit"
        )

        st.caption(
            "Intelligent Personal Loan pre-qualification"
        )


    with badge_col:

        st.markdown(
            "**Risk-Calibrated AI**"
        )

        st.caption(
            "Smart • Personalised"
        )


    st.divider()


    # ------------------------------------------------------------
    # HERO SECTION
    # ------------------------------------------------------------

    with st.container(
        border=True
    ):

        hero_left, hero_right = st.columns(
            [1.55, 0.85],
            gap="large",
            vertical_alignment="center"
        )


        with hero_left:

            st.caption(
                "PERSONAL LOANS MADE SMARTER"
            )


            st.markdown(
                "# Discover your personalised SmartLimit."
            )


            st.markdown(
                """
    Our intelligent engine analyses historical credit
    behaviour, evaluates credit capacity and relative risk,
    and recommends an appropriate maximum Personal Loan offer.
                """
            )


            st.write("")


            feature_1, feature_2, feature_3 = st.columns(
                3
            )


            with feature_1:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "### ⚡"
                    )

                    st.markdown(
                        "**Fast & Secure**"
                    )

                    st.caption(
                        "Quick assessment"
                    )


            with feature_2:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "### 🛡"
                    )

                    st.markdown(
                        "**Personalised**"
                    )

                    st.caption(
                        "Tailored to your profile"
                    )


            with feature_3:

                with st.container(
                    border=True
                ):

                    st.markdown(
                        "### 📊"
                    )

                    st.markdown(
                        "**Data Driven**"
                    )

                    st.caption(
                        "Risk-calibrated offers"
                    )


        with hero_right:

            with st.container(
                border=True
            ):

                st.markdown(
                    "### A Brighter Tomorrow, Together"
                )


                st.caption(
                    "Smart borrowing. Responsible lending."
                )


                st.write("")


                st.markdown(
                    "**₹ Bigger Possibilities**"
                )

                st.caption(
                    "Offers aligned with credit capacity"
                )


                st.markdown(
                    "**◉ Personalised Credit**"
                )

                st.caption(
                    "Based on comparable borrower behaviour"
                )


                st.markdown(
                    "**↗ Responsible Growth**"
                )

                st.caption(
                    "More headroom for safer customers"
                )


    st.write("")



    # ============================================================
    # CUSTOMER WORKFLOW — STEP 7O-B
    # ============================================================

    st.html(
        """
        <div style="
            margin-top: 8px;
            margin-bottom: 18px;
        ">
            <div style="
                font-size: 24px;
                font-weight: 750;
                color: #173E67;
            ">
                Personal Loan Application
            </div>

            <div style="
                color: #6C7D90;
                margin-top: 5px;
                font-size: 14px;
            ">
                Submit your request securely. Your application
                will be reviewed by a TVS Credit Loan Officer.
            </div>
        </div>
        """
    )


    # ========================================================
    # CUSTOMER APPLICATION FORM
    # ========================================================

    with st.form(
        "smartlimit_customer_application"
    ):

        # ----------------------------------------------------
        # SECTION 1 — APPLICANT DETAILS
        # ----------------------------------------------------

        st.subheader(
            "1. Applicant Details"
        )

        a1, a2 = st.columns(2)


        with a1:

            full_name = st.text_input(
                "Full Name",
                placeholder="Enter applicant name"
            )


            mobile = st.text_input(
                "Mobile Number",
                placeholder="10-digit mobile number"
            )


            dob = st.date_input(
                "Date of Birth",
                value=date(
                    1995,
                    1,
                    1
                )
            )


        with a2:

            email = st.text_input(
                "Email Address",
                placeholder="name@example.com"
            )


            employment = st.selectbox(
                "Employment Type",
                [
                    "SALARIED",
                    "SELF_EMPLOYED",
                    "AGRICULTURE",
                    "OTHER"
                ]
            )


            income = st.number_input(
                "Monthly Income (₹)",
                min_value=0,
                max_value=10000000,
                value=50000,
                step=5000
            )


        st.write("")


        # ----------------------------------------------------
        # SECTION 2 — LOAN REQUEST
        # ----------------------------------------------------

        st.subheader(
            "2. Loan Requirement"
        )


        l1, l2 = st.columns(2)


        with l1:

            requested_amount = st.number_input(
                "Requested Loan Amount (₹)",
                min_value=0,
                max_value=2000000,
                value=200000,
                step=10000
            )


            requested_tenure = st.selectbox(
                "Preferred Tenure",
                [
                    6,
                    12,
                    18,
                    24,
                    30,
                    36,
                    48,
                    60
                ],
                index=3,
                format_func=lambda x:
                    f"{x} months"
            )


        with l2:

            loan_purpose = st.selectbox(
                "Purpose of Loan",
                [
                    "Education",
                    "Wedding",
                    "Travel",
                    "Home Improvement",
                    "Consumer Purchase",
                    "Debt Consolidation",
                    "Medical",
                    "Business / Working Capital",
                    "Other"
                ]
            )


        st.write("")


        # ----------------------------------------------------
        # SECTION 3 — KYC & CONSENT
        # ----------------------------------------------------

        st.subheader(
            "3. KYC & Consent"
        )


        st.caption(
            "Prototype note: uploaded documents are used only "
            "to demonstrate the application workflow. "
            "Identity/KYC data is not used by the SmartLimit "
            "prediction model."
        )


        k1, k2 = st.columns(2)


        with k1:

            pan_upload = st.file_uploader(
                "PAN Document (optional in prototype)",
                type=[
                    "pdf",
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="customer_pan_upload"
            )


        with k2:

            aadhaar_upload = st.file_uploader(
                "Aadhaar / ID Document (optional in prototype)",
                type=[
                    "pdf",
                    "png",
                    "jpg",
                    "jpeg"
                ],
                key="customer_aadhaar_upload"
            )


        consent = st.checkbox(
            "I consent to TVS Credit using the information "
            "submitted in this application for credit assessment "
            "and loan processing."
        )


        submitted = st.form_submit_button(
            "SUBMIT LOAN APPLICATION",
            type="primary",
            use_container_width=True
        )


    # ========================================================
    # HANDLE CUSTOMER SUBMISSION
    # ========================================================

    if submitted:

        errors = []


        if not full_name.strip():

            errors.append(
                "Please enter your full name."
            )


        digits = "".join(
            ch
            for ch in mobile
            if ch.isdigit()
        )


        if len(digits) != 10:

            errors.append(
                "Please enter a valid 10-digit mobile number."
            )


        if income <= 0:

            errors.append(
                "Monthly income must be greater than zero."
            )


        if requested_amount <= 0:

            errors.append(
                "Requested loan amount must be greater than zero."
            )


        if not consent:

            errors.append(
                "Consent is required before the application "
                "can be submitted."
            )


        if errors:

            for error in errors:

                st.error(
                    error
                )


        else:

            application_id = create_application(

                customer_name=
                    full_name.strip(),

                mobile=
                    digits,

                email=
                    email.strip(),

                date_of_birth=
                    str(dob),

                employment=
                    employment,

                monthly_income=
                    float(income),

                requested_amount=
                    float(requested_amount),

                requested_tenure=
                    int(requested_tenure),

                loan_purpose=
                    loan_purpose,

                consent_given=
                    True,

                pan_document_name=
                    (
                        pan_upload.name
                        if pan_upload
                        else None
                    ),

                aadhaar_document_name=
                    (
                        aadhaar_upload.name
                        if aadhaar_upload
                        else None
                    )
            )


            st.session_state[
                "customer_application_id"
            ] = application_id


            st.success(
                "Your loan application has been "
                "submitted successfully."
            )


            st.html(
                f"""
                <div style="
                    padding: 18px 20px;
                    margin-top: 12px;
                    border-radius: 14px;
                    background: #F4F9FD;
                    border: 1px solid #DCECF7;
                ">

                    <div style="
                        color:#60758B;
                        font-size:12px;
                        font-weight:700;
                        text-transform:uppercase;
                        letter-spacing:0.8px;
                    ">
                        Application ID
                    </div>

                    <div style="
                        margin-top:5px;
                        color:#173E67;
                        font-size:25px;
                        font-weight:800;
                    ">
                        {application_id}
                    </div>

                    <div style="
                        margin-top:10px;
                        color:#536779;
                        font-size:14px;
                    ">
                        Status: <b>Submitted</b><br>
                        Your application is now with a
                        <b>Loan Officer</b> for credit and
                        bureau verification.
                    </div>

                </div>
                """
            )


            st.info(
                "SmartLimit is not generated directly from "
                "customer-entered information. A Loan Officer "
                "must first verify the required bank-side "
                "credit information."
            )


    # ========================================================
    # APPLICATION STATUS TRACKER
    # ========================================================

    st.write("")
    st.divider()

    st.subheader(
        "Track Your Application"
    )


    default_tracking_id = (
        st.session_state.get(
            "customer_application_id",
            ""
        )
    )


    tracking_id = st.text_input(
        "Application ID",
        value=default_tracking_id,
        placeholder="Example: TVS-20260906-ABC123",
        key="customer_tracking_id"
    )


    if tracking_id.strip():

        tracked_application = get_application(
            tracking_id.strip().upper()
        )


        if tracked_application is None:

            st.warning(
                "No application was found with this ID."
            )


        else:

            status = tracked_application[
                "status"
            ]

            owner = tracked_application[
                "current_owner"
            ]


            status_labels = {

                "SUBMITTED":
                    "Submitted",

                "UNDER_CREDIT_REVIEW":
                    "Under Credit Review",

                "LOAN_OFFICER_POLICY_REVIEW":
                    "Loan Officer Review",

                "LOAN_OFFICER_PROFILE_REVIEW":
                    "Loan Officer Review",

                "LOAN_OFFICER_STABILITY_REVIEW":
                    "Loan Officer Review",

                "FORWARDED_TO_BRANCH_MANAGER":
                    "Branch Manager Review",

                "APPROVED":
                    "Approved",

                "REJECTED":
                    "Not Proceeding",

                "RETURNED":
                    "Returned for Review"
            }


            display_status = (
                status_labels.get(
                    status,
                    status.replace(
                        "_",
                        " "
                    ).title()
                )
            )


            st.html(
                f"""
                <div style="
                    padding:18px 20px;
                    border-radius:14px;
                    background:#FAFCFE;
                    border:1px solid #E4ECF3;
                ">

                    <div style="
                        font-size:13px;
                        color:#6B7E90;
                    ">
                        Application
                    </div>

                    <div style="
                        font-size:18px;
                        font-weight:750;
                        color:#173E67;
                    ">
                        {tracked_application['application_id']}
                    </div>

                    <div style="
                        margin-top:12px;
                        font-size:14px;
                    ">
                        Current Status:
                        <b>{display_status}</b>
                    </div>

                    <div style="
                        margin-top:4px;
                        font-size:13px;
                        color:#6B7E90;
                    ">
                        Current stage:
                        {owner.replace("_", " ").title()}
                    </div>

                </div>
                """
            )


            # ====================================================
            # CUSTOMER FINAL DECISION EXPERIENCE — STEP 7R-B
            # ====================================================

            if status == "SUBMITTED":

                st.caption(
                    "Submitted → Credit Review → "
                    "Branch Manager Review → Final Decision"
                )


            elif status == "UNDER_CREDIT_REVIEW":

                st.info(
                    "Your application is currently undergoing "
                    "credit and bureau verification."
                )


            elif status in {

                "LOAN_OFFICER_POLICY_REVIEW",
                "LOAN_OFFICER_PROFILE_REVIEW",
                "LOAN_OFFICER_STABILITY_REVIEW"

            }:

                st.info(
                    "Your application is under additional "
                    "verification by the credit team."
                )


            elif status == "FORWARDED_TO_BRANCH_MANAGER":

                st.info(
                    "Your application has completed credit review "
                    "and is currently under final branch approval."
                )


            elif status == "APPROVED":

                final_decision = get_branch_decision(
                    tracked_application[
                        "application_id"
                    ]
                )


                approved_amount = None

                if final_decision:

                    approved_amount = (
                        final_decision.get(
                            "approved_amount"
                        )
                    )


                requested_value = float(
                    tracked_application.get(
                        "requested_amount"
                    )
                    or
                    0
                )


                if approved_amount is not None:

                    approved_amount = float(
                        approved_amount
                    )


                    st.success(
                        "Congratulations! Your Personal Loan "
                        "application has been approved."
                    )


                    st.html(
                        f"""
                        <div style="
                            padding:24px 26px;
                            margin-top:12px;
                            border-radius:16px;
                            background:#F3FAF7;
                            border:1px solid #CFE9DA;
                        ">

                            <div style="
                                color:#4F6F60;
                                font-size:12px;
                                font-weight:700;
                                text-transform:uppercase;
                                letter-spacing:0.8px;
                            ">
                                Approved Loan Amount
                            </div>

                            <div style="
                                margin-top:7px;
                                color:#143F2E;
                                font-size:34px;
                                font-weight:850;
                            ">
                                ₹{approved_amount:,.0f}
                            </div>

                            <div style="
                                margin-top:12px;
                                color:#50665C;
                                font-size:14px;
                                line-height:1.6;
                            ">
                                Requested Amount:
                                <b>₹{requested_value:,.0f}</b>
                            </div>

                        </div>
                        """
                    )


                    if approved_amount < requested_value:

                        st.info(
                            f"Based on the completed credit assessment, "
                            f"your application has been approved for up to "
                            f"₹{approved_amount:,.0f} against your requested "
                            f"amount of ₹{requested_value:,.0f}."
                        )

                    else:

                        st.info(
                            "Your requested loan amount has been "
                            "approved in full."
                        )


                    st.markdown(
                        "#### What happens next?"
                    )

                    st.write(
                        "A TVS Credit representative / Loan Officer "
                        "can complete the remaining documentation and "
                        "disbursement formalities with you."
                    )


                else:

                    st.success(
                        "Your Personal Loan application has "
                        "been approved."
                    )


            elif status == "REJECTED":

                st.warning(
                    "Your application is not proceeding at this stage."
                )

                st.caption(
                    "Please contact the Loan Officer or branch for "
                    "any permitted next steps or future eligibility."
                )


            elif status == "RETURNED":

                st.info(
                    "Your application has been returned for additional "
                    "verification and is being reviewed again."
                )


    st.html(
        """
        <div class="small-note" style="text-align:center; margin-top:25px;">

        TVS SmartLimit — Case Competition Prototype<br>
        Customer-submitted data is verified by the Loan Officer
        before SmartLimit V4 assessment. Production implementation
        would use authenticated TVS and bureau data retrieval.

        </div>
        """
    )



# ============================================================
# LOAN OFFICER WORKSPACE
# ============================================================

elif selected_role == "Loan Officer Workspace":

    st.markdown(
        "## Loan Officer Workspace"
    )

    st.caption(
        "Internal credit assessment • Policy validation • "
        "SmartLimit V4 recommendation"
    )


    # --------------------------------------------------------
    # SAFE LEARNING-REPOSITORY SYNC
    # --------------------------------------------------------

    def _sync_verified_repository_safe(
        application_id
    ):

        try:

            import inspect

            from learning_repository_v4 import (
                sync_verified_customer_to_repository
            )

            fn = (
                sync_verified_customer_to_repository
            )

            sig = inspect.signature(
                fn
            )

            application_row = (
                get_application(
                    application_id
                )
            )

            assessment_row = (
                get_credit_assessment(
                    application_id
                )
            )

            kwargs = {}

            unsupported_required = []


            for name, parameter in (
                sig.parameters.items()
            ):

                if name == "application_id":

                    kwargs[
                        name
                    ] = application_id


                elif name in [
                    "application",
                    "app",
                    "application_data"
                ]:

                    kwargs[
                        name
                    ] = application_row


                elif name in [
                    "credit_assessment",
                    "assessment",
                    "credit_data"
                ]:

                    kwargs[
                        name
                    ] = assessment_row


                elif name == "kyc_verified":

                    kwargs[
                        name
                    ] = bool(
                        assessment_row
                        and
                        assessment_row.get(
                            "kyc_verified"
                        )
                    )


                elif name == "db_path":

                    # Let repository module use
                    # its own canonical DB path.
                    pass


                elif (
                    parameter.default
                    is
                    inspect._empty
                ):

                    unsupported_required.append(
                        name
                    )


            if unsupported_required:

                return {

                    "synced":
                        False,

                    "message":
                        (
                            "Repository sync deferred; "
                            "unsupported required argument(s): "
                            +
                            ", ".join(
                                unsupported_required
                            )
                        )

                }


            response = fn(
                **kwargs
            )


            return {

                "synced":
                    True,

                "response":
                    response,

                "message":
                    (
                        "Verified customer synchronized "
                        "to the learning repository."
                    )

            }


        except Exception as exc:

            return {

                "synced":
                    False,

                "message":
                    (
                        "Assessment saved successfully. "
                        "Learning-repository sync could "
                        "not be completed in this UI run: "
                        f"{exc}"
                    )

            }


    # --------------------------------------------------------
    # LOAD LOAN OFFICER QUEUE
    # --------------------------------------------------------

    loan_officer_queue = (
        list_applications(
            owner="LOAN_OFFICER"
        )
    )


    allowed_lo_statuses = {

        "SUBMITTED",

        "UNDER_CREDIT_REVIEW",

        "RETURN_TO_LOAN_OFFICER",

        "LOAN_OFFICER_POLICY_REVIEW",

        "LOAN_OFFICER_PROFILE_REVIEW",

        "LOAN_OFFICER_STABILITY_REVIEW",

        "OUTSIDE_PRODUCT_POLICY"

    }


    loan_officer_queue = [

        row

        for row
        in loan_officer_queue

        if row.get(
            "status"
        )
        in allowed_lo_statuses

    ]


    # --------------------------------------------------------
    # QUEUE SUMMARY
    # --------------------------------------------------------

    q1, q2, q3 = st.columns(
        3
    )


    with q1:

        st.metric(
            "Applications in Queue",
            len(
                loan_officer_queue
            )
        )


    with q2:

        new_count = sum(

            1

            for row
            in loan_officer_queue

            if row.get(
                "status"
            )
            ==
            "SUBMITTED"

        )

        st.metric(
            "New Applications",
            new_count
        )


    with q3:

        review_count = sum(

            1

            for row
            in loan_officer_queue

            if row.get(
                "status"
            )
            not in {
                "SUBMITTED",
                "UNDER_CREDIT_REVIEW"
            }

        )

        st.metric(
            "Review Cases",
            review_count
        )


    st.divider()


    # --------------------------------------------------------
    # EMPTY QUEUE
    # --------------------------------------------------------

    if not loan_officer_queue:

        st.success(
            "No applications are currently pending "
            "with the Loan Officer."
        )


    # --------------------------------------------------------
    # APPLICATION SELECTION
    # --------------------------------------------------------

    else:

        option_map = {}

        for row in loan_officer_queue:

            label = (

                f"{row['application_id']}  |  "
                f"{row.get('customer_name', 'Customer')}  |  "
                f"₹{float(row.get('requested_amount') or 0):,.0f}  |  "
                f"{row.get('status', '')}"

            )

            option_map[
                label
            ] = row[
                "application_id"
            ]


        selected_label = st.selectbox(

            "Select Application",

            options=list(
                option_map.keys()
            ),

            key="loan_officer_application_selector"

        )


        selected_application_id = (
            option_map[
                selected_label
            ]
        )


        application = (
            get_application(
                selected_application_id
            )
        )


        existing_assessment = (
            get_credit_assessment(
                selected_application_id
            )
            or
            {}
        )


        existing_model_result = (
            get_model_result(
                selected_application_id
            )
        )


        # ====================================================
        # CUSTOMER APPLICATION SUMMARY
        # ====================================================

        st.markdown(
            "### Customer Application"
        )


        with st.container(
            border=True
        ):

            c1, c2, c3 = st.columns(
                3
            )


            with c1:

                st.caption(
                    "APPLICATION"
                )

                st.write(
                    f"**{application['application_id']}**"
                )

                st.write(
                    application.get(
                        "customer_name",
                        ""
                    )
                )


            with c2:

                st.caption(
                    "REQUEST"
                )

                st.write(
                    f"**₹{float(application.get('requested_amount') or 0):,.0f}**"
                )

                st.write(
                    f"{application.get('requested_tenure') or '-'} months"
                )


            with c3:

                st.caption(
                    "CURRENT STATUS"
                )

                st.write(
                    f"**{application.get('status', '')}**"
                )

                st.write(
                    "Owner: Loan Officer"
                )


            st.divider()


            x1, x2, x3 = st.columns(
                3
            )


            with x1:

                st.write(
                    "**Employment**"
                )

                st.write(
                    application.get(
                        "employment",
                        "-"
                    )
                )


            with x2:

                st.write(
                    "**Monthly Income**"
                )

                st.write(
                    f"₹{float(application.get('monthly_income') or 0):,.0f}"
                )


            with x3:

                st.write(
                    "**Loan Purpose**"
                )

                st.write(
                    application.get(
                        "loan_purpose",
                        "-"
                    )
                )


            st.caption(
                "Customer identity and contact information are "
                "used for workflow/KYC only. They are not "
                "predictive SmartLimit features."
            )


        # ====================================================
        # CREDIT & BUREAU ASSESSMENT
        # ====================================================

        st.markdown(
            "### Credit & Bureau Verification"
        )

        st.caption(
            "Enter verified bank/bureau information. "
            "CIBIL is a policy input and is separate from "
            "the V4 External Risk Score model feature."
        )


        def _existing_float(
            field,
            default
        ):

            value = (
                existing_assessment.get(
                    field
                )
            )

            if value is None:

                return float(
                    default
                )

            return float(
                value
            )


        def _existing_int(
            field,
            default
        ):

            value = (
                existing_assessment.get(
                    field
                )
            )

            if value is None:

                return int(
                    default
                )

            return int(
                round(
                    float(
                        value
                    )
                )
            )


        with st.form(
            key=(
                "loan_officer_credit_form_"
                +
                selected_application_id
            )
        ):

            # ------------------------------------------------
            # Bureau / affordability
            # ------------------------------------------------

            a1, a2, a3 = st.columns(
                3
            )


            with a1:

                cibil_score = st.number_input(

                    "CIBIL Score",

                    min_value=300,

                    max_value=900,

                    value=_existing_int(
                        "cibil_score",
                        750
                    ),

                    step=1,

                    help=(
                        "Policy/workflow input. "
                        "Not used as the V4 Direct AI "
                        "model feature."
                    )

                )


            with a2:

                avg_emi = st.number_input(

                    "Average Monthly EMI (₹)",

                    min_value=0.0,

                    value=_existing_float(
                        "avg_emi",
                        0
                    ),

                    step=1000.0

                )


            with a3:

                active_loans = st.number_input(

                    "Active Loans",

                    min_value=0,

                    value=_existing_int(
                        "active_loans",
                        0
                    ),

                    step=1

                )


            # ------------------------------------------------
            # Existing leverage
            # ------------------------------------------------

            b1, b2 = st.columns(
                2
            )


            with b1:

                outstanding_balance = st.number_input(

                    "Outstanding Balance (₹)",

                    min_value=0.0,

                    value=_existing_float(
                        "outstanding_balance",
                        0
                    ),

                    step=5000.0

                )


            with b2:

                max_previous_credit = st.number_input(

                    "Maximum Previous Credit (₹)",

                    min_value=0.0,

                    value=_existing_float(
                        "max_previous_credit",
                        100000
                    ),

                    step=5000.0

                )


            # ------------------------------------------------
            # Credit history
            # ------------------------------------------------

            c1, c2 = st.columns(
                2
            )


            with c1:

                credit_history_months = st.number_input(

                    "Credit History (Months)",

                    min_value=0,

                    value=_existing_int(
                        "credit_history_months",
                        24
                    ),

                    step=1

                )


            with c2:

                months_since_last_loan = st.number_input(

                    "Months Since Last Loan",

                    min_value=0,

                    value=_existing_int(
                        "months_since_last_loan",
                        6
                    ),

                    step=1

                )


            # ------------------------------------------------
            # Repayment history
            # ------------------------------------------------

            d1, d2 = st.columns(
                2
            )


            with d1:

                payment_count = st.number_input(

                    "Total Payment Count",

                    min_value=0,

                    value=_existing_int(
                        "payment_count",
                        24
                    ),

                    step=1

                )


            with d2:

                successful_payment_count = st.number_input(

                    "Successful Payment Count",

                    min_value=0,

                    value=_existing_int(
                        "successful_payment_count",
                        24
                    ),

                    step=1

                )


            if payment_count > 0:

                repayment_success_rate = (

                    successful_payment_count
                    /
                    payment_count
                    *
                    100

                )

            else:

                repayment_success_rate = 0.0


            repayment_success_rate = max(
                0.0,
                min(
                    100.0,
                    float(
                        repayment_success_rate
                    )
                )
            )


            st.caption(
                f"Calculated repayment success rate: "
                f"**{repayment_success_rate:.1f}%**"
            )


            # ------------------------------------------------
            # Risk fields
            # ------------------------------------------------

            e1, e2 = st.columns(
                2
            )


            with e1:

                external_risk_score = st.number_input(

                    "External Risk Score",

                    value=_existing_float(
                        "external_risk_score",
                        750
                    ),

                    step=1.0,

                    help=(
                        "Verified external/bureau risk field "
                        "used by the V4 model. "
                        "It is not automatically assumed "
                        "to be the same as CIBIL."
                    )

                )


            with e2:

                risk_gradation = st.number_input(

                    "Internal Risk Gradation",

                    value=_existing_float(
                        "risk_gradation",
                        3
                    ),

                    step=1.0,

                    help=(
                        "Use the verified internal "
                        "risk-gradation value."
                    )

                )


            # ------------------------------------------------
            # Adverse flags
            # ------------------------------------------------

            f1, f2, f3 = st.columns(
                3
            )


            with f1:

                current_dpd = st.number_input(

                    "Current DPD",

                    min_value=0,

                    value=_existing_int(
                        "current_dpd",
                        0
                    ),

                    step=1

                )


            with f2:

                write_off_flag = st.checkbox(

                    "Previous Write-off",

                    value=bool(
                        existing_assessment.get(
                            "write_off_flag",
                            False
                        )
                    )

                )


            with f3:

                settlement_flag = st.checkbox(

                    "Previous Settlement",

                    value=bool(
                        existing_assessment.get(
                            "settlement_flag",
                            False
                        )
                    )

                )


            # ------------------------------------------------
            # KYC
            # ------------------------------------------------

            st.markdown(
                "**KYC Verification**"
            )


            uploaded_docs = []

            if application.get(
                "pan_document_name"
            ):

                uploaded_docs.append(
                    "PAN document uploaded"
                )


            if application.get(
                "aadhaar_document_name"
            ):

                uploaded_docs.append(
                    "Aadhaar document uploaded"
                )


            if uploaded_docs:

                st.caption(
                    " • ".join(
                        uploaded_docs
                    )
                )

            else:

                st.caption(
                    "No prototype KYC document filename "
                    "is attached. Loan Officer may verify "
                    "through the bank's approved KYC process."
                )


            kyc_verified = st.checkbox(

                "I confirm KYC has been verified",

                value=bool(
                    existing_assessment.get(
                        "kyc_verified",
                        False
                    )
                )

            )


            loan_officer_notes = st.text_area(

                "Loan Officer Notes",

                value=(
                    existing_assessment.get(
                        "loan_officer_notes"
                    )
                    or
                    ""
                ),

                placeholder=(
                    "Add verification notes, exceptions "
                    "or relevant credit observations..."
                )

            )


            st.caption(
                "Demo policy thresholds shown in this "
                "prototype are configurable and require "
                "actual lender approval."
            )


            button_col1, button_col2 = st.columns(
                2
            )


            with button_col1:

                save_assessment_clicked = (
                    st.form_submit_button(
                        "SAVE CREDIT ASSESSMENT",
                        use_container_width=True
                    )
                )


            with button_col2:

                run_smartlimit_clicked = (
                    st.form_submit_button(
                        "RUN SMARTLIMIT V4",
                        type="primary",
                        use_container_width=True
                    )
                )


        # ====================================================
        # HANDLE FORM ACTION
        # ====================================================

        if (
            save_assessment_clicked
            or
            run_smartlimit_clicked
        ):

            if (
                successful_payment_count
                >
                payment_count
            ):

                st.error(
                    "Successful Payment Count cannot "
                    "exceed Total Payment Count."
                )


            else:

                assessment_payload = {

                    "cibil_score":
                        float(
                            cibil_score
                        ),

                    "avg_emi":
                        float(
                            avg_emi
                        ),

                    "active_loans":
                        float(
                            active_loans
                        ),

                    "outstanding_balance":
                        float(
                            outstanding_balance
                        ),

                    "max_previous_credit":
                        float(
                            max_previous_credit
                        ),

                    "credit_history_months":
                        float(
                            credit_history_months
                        ),

                    "months_since_last_loan":
                        float(
                            months_since_last_loan
                        ),

                    "payment_count":
                        float(
                            payment_count
                        ),

                    "successful_payment_count":
                        float(
                            successful_payment_count
                        ),

                    "repayment_success_rate":
                        float(
                            repayment_success_rate
                        ),

                    "external_risk_score":
                        float(
                            external_risk_score
                        ),

                    "risk_gradation":
                        float(
                            risk_gradation
                        ),

                    "current_dpd":
                        float(
                            current_dpd
                        ),

                    "write_off_flag":
                        bool(
                            write_off_flag
                        ),

                    "settlement_flag":
                        bool(
                            settlement_flag
                        ),

                    "kyc_verified":
                        bool(
                            kyc_verified
                        ),

                    "loan_officer_notes":
                        loan_officer_notes

                }


                # --------------------------------------------
                # Save assessment
                # --------------------------------------------

                save_credit_assessment(

                    selected_application_id,

                    assessment_payload,

                    assessed_by=(
                        "Loan Officer"
                    )

                )


                # --------------------------------------------
                # Move to active credit review
                # --------------------------------------------

                if not run_smartlimit_clicked:

                    update_application_status(

                        application_id=
                            selected_application_id,

                        status=
                            "UNDER_CREDIT_REVIEW",

                        current_owner=
                            "LOAN_OFFICER",

                        actor_role=
                            "LOAN_OFFICER",

                        actor_name=
                            "Loan Officer",

                        action=
                            "CREDIT_REVIEW_STARTED",

                        details={
                            "kyc_verified":
                                bool(
                                    kyc_verified
                                )
                        }

                    )


                # --------------------------------------------
                # Learning repository:
                # verified data only
                # --------------------------------------------

                repository_sync = None

                if kyc_verified:

                    repository_sync = (
                        _sync_verified_repository_safe(
                            selected_application_id
                        )
                    )


                if save_assessment_clicked:

                    st.success(
                        "Credit assessment saved successfully."
                    )

                    if repository_sync:

                        if repository_sync.get(
                            "synced"
                        ):

                            st.caption(
                                "✓ Verified customer information "
                                "has been synchronized to the "
                                "bank learning repository."
                            )

                        else:

                            st.caption(
                                repository_sync.get(
                                    "message",
                                    ""
                                )
                            )


                # ============================================
                # RUN FINAL V4 ORCHESTRATOR
                # ============================================

                if run_smartlimit_clicked:

                    model_application = {

                        # ------------------------------------
                        # Workflow / policy inputs
                        # ------------------------------------

                        "KYC_COMPLETED":
                            bool(
                                kyc_verified
                            ),

                        "CONSENT_GIVEN":
                            bool(
                                application.get(
                                    "consent_given"
                                )
                            ),

                        "REQUESTED_AMOUNT":
                            float(
                                application.get(
                                    "requested_amount"
                                )
                            ),

                        "CIBIL_SCORE":
                            float(
                                cibil_score
                            ),

                        "CURRENT_DPD":
                            float(
                                current_dpd
                            ),

                        "WRITE_OFF_FLAG":
                            bool(
                                write_off_flag
                            ),

                        "SETTLEMENT_FLAG":
                            bool(
                                settlement_flag
                            ),


                        # ------------------------------------
                        # V4 AI fields
                        # ------------------------------------

                        "INCOME":
                            float(
                                application.get(
                                    "monthly_income"
                                )
                            ),

                        "AVG_EMI":
                            float(
                                avg_emi
                            ),

                        "ACTIVE_LOANS":
                            float(
                                active_loans
                            ),

                        "OUTSTANDING_BALANCE":
                            float(
                                outstanding_balance
                            ),

                        "MAX_PREVIOUS_CREDIT":
                            float(
                                max_previous_credit
                            ),

                        "CREDIT_HISTORY_MONTHS":
                            float(
                                credit_history_months
                            ),

                        "MONTHS_SINCE_LAST_LOAN":
                            float(
                                months_since_last_loan
                            ),

                        "PAYMENT_COUNT":
                            float(
                                payment_count
                            ),

                        "SUCCESSFUL_PAYMENT_COUNT":
                            float(
                                successful_payment_count
                            ),

                        "EXTERNAL_RISK_SCORE":
                            float(
                                external_risk_score
                            ),

                        "RISK_GRADATION":
                            float(
                                risk_gradation
                            ),

                        "EMPLOYMENT":
                            application.get(
                                "employment"
                            ),

                        "REPAYMENT_SUCCESS_RATE":
                            float(
                                repayment_success_rate
                            )

                    }


                    result = (
                        process_final_smartlimit_v4(
                            model_application
                        )
                    )


                    # ----------------------------------------
                    # Persist exact result using DB contract
                    # ----------------------------------------

                    db_result = dict(
                        result
                    )

                    db_result[
                        "engine_version"
                    ] = "SmartLimit V4"

                    db_result[
                        "multiplier"
                    ] = result.get(
                        "guardrail_multiplier"
                    )

                    db_result[
                        "model_outcome"
                    ] = result.get(
                        "application_outcome"
                    )

                    db_result[
                        "workflow_route"
                    ] = result.get(
                        "workflow_status"
                    )


                    save_model_result(

                        selected_application_id,

                        db_result

                    )


                    # ----------------------------------------
                    # ROUTING
                    # ----------------------------------------

                    if result.get(
                        "forward_to_branch_manager"
                    ):

                        new_status = (
                            "FORWARDED_TO_BRANCH_MANAGER"
                        )

                        new_owner = (
                            "BRANCH_MANAGER"
                        )

                        action = (
                            "APPLICATION_FORWARDED_TO_BRANCH_MANAGER"
                        )


                    else:

                        new_status = (

                            result.get(
                                "workflow_status"
                            )

                            or

                            "UNDER_CREDIT_REVIEW"

                        )

                        new_owner = (
                            "LOAN_OFFICER"
                        )

                        action = (
                            "SMARTLIMIT_REVIEW_REQUIRED"
                        )


                    update_application_status(

                        application_id=
                            selected_application_id,

                        status=
                            new_status,

                        current_owner=
                            new_owner,

                        actor_role=
                            "LOAN_OFFICER",

                        actor_name=
                            "Loan Officer",

                        action=
                            action,

                        details={

                            "policy_status":
                                result.get(
                                    "policy_status"
                                ),

                            "model_outcome":
                                result.get(
                                    "application_outcome"
                                ),

                            "recommended_amount":
                                result.get(
                                    "recommended_amount"
                                )

                        }

                    )


                    st.session_state[
                        "lo_last_scored_application"
                    ] = selected_application_id


                    st.success(
                        "SmartLimit V4 assessment completed."
                    )


        # ====================================================
        # DISPLAY LATEST SAVED MODEL RESULT
        # ====================================================

        latest_result = (
            get_model_result(
                selected_application_id
            )
        )


        if latest_result:

            st.divider()

            st.markdown(
                "### SmartLimit V4 Recommendation"
            )


            r1, r2, r3, r4 = st.columns(
                4
            )


            with r1:

                value = (
                    latest_result.get(
                        "offer_anchor"
                    )
                )

                st.metric(

                    "Base Eligible Amount",

                    (
                        f"₹{float(value):,.0f}"
                        if value is not None
                        else "—"
                    )

                )


            with r2:

                value = (
                    latest_result.get(
                        "smartlimit"
                    )
                )

                st.metric(

                    "SmartLimit",

                    (
                        f"₹{float(value):,.0f}"
                        if value is not None
                        else "—"
                    )

                )


            with r3:

                risk_value = (
                    latest_result.get(
                        "relative_risk_score"
                    )
                )

                risk_segment_value = (
                    latest_result.get(
                        "risk_segment"
                    )
                    or
                    "—"
                )

                st.metric(

                    "Relative Risk",

                    (
                        f"{float(risk_value):.1f}"
                        if risk_value is not None
                        else "—"
                    ),

                    risk_segment_value

                )


            with r4:

                multiplier_value = (
                    latest_result.get(
                        "guardrail_multiplier"
                    )
                )

                st.metric(

                    "Risk Multiplier",

                    (
                        f"{float(multiplier_value):.2f}×"
                        if multiplier_value is not None
                        else "—"
                    )

                )


            s1, s2, s3 = st.columns(
                3
            )


            with s1:

                st.metric(

                    "Confidence",

                    latest_result.get(
                        "confidence"
                    )
                    or
                    "—"

                )


            with s2:

                st.metric(

                    "Stability",

                    latest_result.get(
                        "stability_grade"
                    )
                    or
                    "—"

                )


            with s3:

                recommended = (
                    latest_result.get(
                        "recommended_amount"
                    )
                )

                st.metric(

                    "Recommended Amount",

                    (
                        f"₹{float(recommended):,.0f}"
                        if recommended is not None
                        else "—"
                    )

                )


            route = (
                latest_result.get(
                    "workflow_route"
                )
            )


            outcome = (
                latest_result.get(
                    "model_outcome"
                )
            )


            policy_status = (
                latest_result.get(
                    "policy_status"
                )
            )


            if route == (
                "FORWARD_TO_BRANCH_MANAGER"
            ):

                st.success(
                    "Assessment is ready for Branch Manager review."
                )

            elif route:

                st.warning(
                    "Application remains with the Loan Officer "
                    "for verification before it can proceed."
                )


            with st.container(
                border=True
            ):

                st.write(
                    f"**Policy Status:** "
                    f"{policy_status or '—'}"
                )

                st.write(
                    f"**Model Outcome:** "
                    f"{outcome or '—'}"
                )

                st.write(
                    f"**Workflow Route:** "
                    f"{route or '—'}"
                )


            policy_reasons = (
                latest_result.get(
                    "policy_reasons"
                )
            )


            if policy_reasons:

                try:

                    import json

                    parsed_reasons = (
                        json.loads(
                            policy_reasons
                        )
                    )

                except Exception:

                    parsed_reasons = [
                        str(
                            policy_reasons
                        )
                    ]


                if parsed_reasons:

                    with st.expander(
                        "Policy / Review Reasons"
                    ):

                        for reason in parsed_reasons:

                            st.write(
                                "•",
                                reason
                            )


            st.info(
                "The risk score is a relative risk rank, "
                "not a probability of default. "
                "Historical matching supports confidence/"
                "explainability only and does not determine "
                "the SmartLimit amount. Final sanction remains "
                "with the Branch Manager."
            )


            # ====================================================
            # LOAN OFFICER MANUAL REVIEW RESOLUTION — STEP 7P-G
            # ====================================================

            review_routes = {

                "LOAN_OFFICER_POLICY_REVIEW",

                "LOAN_OFFICER_PROFILE_REVIEW",

                "LOAN_OFFICER_STABILITY_REVIEW"

            }


            if route in review_routes:

                st.divider()

                st.markdown(
                    "### Manual Review & Resolution"
                )

                st.warning(
                    "This case requires Loan Officer verification "
                    "before it can proceed to the Branch Manager."
                )


                with st.container(
                    border=True
                ):

                    st.write(
                        f"**Review Trigger:** {route}"
                    )

                    st.write(
                        f"**Confidence:** "
                        f"{latest_result.get('confidence') or '—'}"
                    )

                    st.write(
                        f"**Stability:** "
                        f"{latest_result.get('stability_grade') or '—'}"
                    )

                    st.write(
                        f"**Indicative SmartLimit:** "
                        f"₹{float(latest_result.get('smartlimit') or 0):,.0f}"
                    )


                manual_review_confirmed = st.checkbox(

                    "I confirm that I have manually verified "
                    "the flagged credit/profile information.",

                    key=(
                        "manual_review_confirmed_"
                        +
                        selected_application_id
                    )

                )


                manual_review_note = st.text_area(

                    "Manual Review Note",

                    placeholder=(
                        "Example: Bureau profile verified, "
                        "income consistency checked and no "
                        "material discrepancy identified."
                    ),

                    key=(
                        "manual_review_note_"
                        +
                        selected_application_id
                    )

                )


                resolve_review_clicked = st.button(

                    "RESOLVE REVIEW & FORWARD TO BRANCH MANAGER",

                    type="primary",

                    use_container_width=True,

                    key=(
                        "resolve_review_"
                        +
                        selected_application_id
                    )

                )


                if resolve_review_clicked:

                    if not manual_review_confirmed:

                        st.error(
                            "Please confirm that manual verification "
                            "has been completed."
                        )


                    elif not manual_review_note.strip():

                        st.error(
                            "Please enter a short Manual Review Note."
                        )


                    else:

                        update_application_status(

                            application_id=
                                selected_application_id,

                            status=
                                "FORWARDED_TO_BRANCH_MANAGER",

                            current_owner=
                                "BRANCH_MANAGER",

                            actor_role=
                                "LOAN_OFFICER",

                            actor_name=
                                "Loan Officer",

                            action=
                                "MANUAL_REVIEW_RESOLVED_AND_FORWARDED",

                            details={

                                "original_review_route":
                                    route,

                                "confidence":
                                    latest_result.get(
                                        "confidence"
                                    ),

                                "stability_grade":
                                    latest_result.get(
                                        "stability_grade"
                                    ),

                                "smartlimit":
                                    latest_result.get(
                                        "smartlimit"
                                    ),

                                "recommended_amount":
                                    latest_result.get(
                                        "recommended_amount"
                                    ),

                                "manual_verification_completed":
                                    True,

                                "manual_review_note":
                                    manual_review_note.strip(),

                                "final_decision":
                                    "PENDING_BRANCH_MANAGER"

                            }

                        )


                        st.success(
                            "Manual review resolved. "
                            "Application forwarded to the "
                            "Branch Manager for final decision."
                        )


                        st.rerun()



# ============================================================


# BRANCH MANAGER CONSOLE
# ============================================================

elif selected_role == "Branch Manager Console":

    st.markdown(
        "## Branch Manager Console"
    )

    st.caption(
        "Final human credit review • SmartLimit decision support • Sanction control"
    )


    # --------------------------------------------------------
    # LOAD BRANCH MANAGER QUEUE
    # --------------------------------------------------------

    bm_queue = list_applications(
        owner="BRANCH_MANAGER"
    )


    bm_queue = [

        row

        for row in bm_queue

        if row.get(
            "status"
        )
        ==
        "FORWARDED_TO_BRANCH_MANAGER"

    ]


    # --------------------------------------------------------
    # QUEUE METRICS
    # --------------------------------------------------------

    q1, q2, q3 = st.columns(
        3
    )


    with q1:

        st.metric(
            "Pending Final Review",
            len(
                bm_queue
            )
        )


    with q2:

        total_requested = sum(

            float(
                row.get(
                    "requested_amount"
                )
                or
                0
            )

            for row
            in bm_queue

        )

        st.metric(
            "Requested Value",
            f"₹{total_requested:,.0f}"
        )


    with q3:

        st.metric(
            "Decision Authority",
            "Branch Manager"
        )


    st.divider()


    # --------------------------------------------------------
    # EMPTY QUEUE
    # --------------------------------------------------------

    if not bm_queue:

        st.success(
            "No applications are currently pending "
            "Branch Manager approval."
        )


    # --------------------------------------------------------
    # APPLICATION SELECTION
    # --------------------------------------------------------

    else:

        bm_option_map = {}


        for row in bm_queue:

            label = (

                f"{row['application_id']}  |  "
                f"{row.get('customer_name', 'Customer')}  |  "
                f"₹{float(row.get('requested_amount') or 0):,.0f}"

            )

            bm_option_map[
                label
            ] = row[
                "application_id"
            ]


        selected_bm_label = st.selectbox(

            "Select Application for Final Review",

            options=list(
                bm_option_map.keys()
            ),

            key="branch_manager_application_selector"

        )


        selected_bm_application_id = (
            bm_option_map[
                selected_bm_label
            ]
        )


        application = get_application(
            selected_bm_application_id
        )


        credit_assessment = (
            get_credit_assessment(
                selected_bm_application_id
            )
            or
            {}
        )


        model_result = (
            get_model_result(
                selected_bm_application_id
            )
            or
            {}
        )


        existing_decision = (
            get_branch_decision(
                selected_bm_application_id
            )
        )


        audit_history = (
            get_audit_history(
                selected_bm_application_id
            )
        )


        # ====================================================
        # APPLICATION SUMMARY
        # ====================================================

        st.markdown(
            "### Application Summary"
        )


        with st.container(
            border=True
        ):

            a1, a2, a3 = st.columns(
                3
            )


            with a1:

                st.caption(
                    "CUSTOMER"
                )

                st.write(
                    f"**{application.get('customer_name', '—')}**"
                )

                st.write(
                    application.get(
                        "application_id",
                        "—"
                    )
                )


            with a2:

                requested_amount = float(
                    application.get(
                        "requested_amount"
                    )
                    or
                    0
                )

                st.caption(
                    "REQUESTED AMOUNT"
                )

                st.write(
                    f"**₹{requested_amount:,.0f}**"
                )

                st.write(
                    f"{application.get('requested_tenure') or '—'} months"
                )


            with a3:

                st.caption(
                    "CURRENT STATUS"
                )

                st.write(
                    f"**{application.get('status', '—')}**"
                )

                st.write(
                    "Final human review pending"
                )


            st.divider()


            x1, x2, x3 = st.columns(
                3
            )


            with x1:

                st.write(
                    "**Employment**"
                )

                st.write(
                    application.get(
                        "employment",
                        "—"
                    )
                )


            with x2:

                st.write(
                    "**Monthly Income**"
                )

                st.write(
                    f"₹{float(application.get('monthly_income') or 0):,.0f}"
                )


            with x3:

                st.write(
                    "**Loan Purpose**"
                )

                st.write(
                    application.get(
                        "loan_purpose",
                        "—"
                    )
                )


        # ====================================================
        # CREDIT & BUREAU REVIEW
        # ====================================================

        st.markdown(
            "### Credit & Bureau Review"
        )


        with st.container(
            border=True
        ):

            c1, c2, c3, c4 = st.columns(
                4
            )


            with c1:

                cibil = credit_assessment.get(
                    "cibil_score"
                )

                st.metric(
                    "CIBIL",
                    (
                        f"{float(cibil):.0f}"
                        if cibil is not None
                        else "—"
                    )
                )


            with c2:

                emi = credit_assessment.get(
                    "avg_emi"
                )

                st.metric(
                    "Monthly EMI",
                    (
                        f"₹{float(emi):,.0f}"
                        if emi is not None
                        else "—"
                    )
                )


            with c3:

                dpd = credit_assessment.get(
                    "current_dpd"
                )

                st.metric(
                    "Current DPD",
                    (
                        f"{float(dpd):.0f}"
                        if dpd is not None
                        else "—"
                    )
                )


            with c4:

                kyc = bool(
                    credit_assessment.get(
                        "kyc_verified",
                        False
                    )
                )

                st.metric(
                    "KYC",
                    (
                        "Verified"
                        if kyc
                        else
                        "Pending"
                    )
                )


            b1, b2, b3 = st.columns(
                3
            )


            with b1:

                st.write(
                    "**Active Loans:**",
                    int(
                        float(
                            credit_assessment.get(
                                "active_loans"
                            )
                            or
                            0
                        )
                    )
                )


                st.write(
                    "**Outstanding:**",
                    f"₹{float(credit_assessment.get('outstanding_balance') or 0):,.0f}"
                )


            with b2:

                st.write(
                    "**Repayment Success:**",
                    f"{float(credit_assessment.get('repayment_success_rate') or 0):.1f}%"
                )


                st.write(
                    "**External Risk Score:**",
                    credit_assessment.get(
                        "external_risk_score",
                        "—"
                    )
                )


            with b3:

                st.write(
                    "**Write-off Flag:**",
                    (
                        "Yes"
                        if credit_assessment.get(
                            "write_off_flag"
                        )
                        else
                        "No"
                    )
                )


                st.write(
                    "**Settlement Flag:**",
                    (
                        "Yes"
                        if credit_assessment.get(
                            "settlement_flag"
                        )
                        else
                        "No"
                    )
                )


            if credit_assessment.get(
                "loan_officer_notes"
            ):

                st.divider()

                st.write(
                    "**Loan Officer Notes**"
                )

                st.write(
                    credit_assessment.get(
                        "loan_officer_notes"
                    )
                )


        # ====================================================
        # SMARTLIMIT V4 RECOMMENDATION
        # ====================================================

        st.markdown(
            "### SmartLimit V4 Recommendation"
        )


        m1, m2, m3, m4 = st.columns(
            4
        )


        offer_anchor = model_result.get(
            "offer_anchor"
        )

        smartlimit = model_result.get(
            "smartlimit"
        )

        risk_score = model_result.get(
            "relative_risk_score"
        )

        risk_segment = model_result.get(
            "risk_segment"
        )

        multiplier = model_result.get(
            "guardrail_multiplier"
        )

        recommended_amount = model_result.get(
            "recommended_amount"
        )


        with m1:

            st.metric(

                "Base Eligible Amount",

                (
                    f"₹{float(offer_anchor):,.0f}"
                    if offer_anchor is not None
                    else "—"
                )

            )


        with m2:

            st.metric(

                "SmartLimit",

                (
                    f"₹{float(smartlimit):,.0f}"
                    if smartlimit is not None
                    else "—"
                )

            )


        with m3:

            st.metric(

                "Relative Risk",

                (
                    f"{float(risk_score):.1f}"
                    if risk_score is not None
                    else "—"
                ),

                risk_segment
                or
                "—"

            )


        with m4:

            st.metric(

                "Risk Multiplier",

                (
                    f"{float(multiplier):.2f}×"
                    if multiplier is not None
                    else "—"
                )

            )


        r1, r2, r3 = st.columns(
            3
        )


        with r1:

            st.metric(
                "Confidence",
                model_result.get(
                    "confidence"
                )
                or
                "—"
            )


        with r2:

            st.metric(
                "Stability",
                model_result.get(
                    "stability_grade"
                )
                or
                "—"
            )


        with r3:

            st.metric(

                "Recommended Amount",

                (
                    f"₹{float(recommended_amount):,.0f}"
                    if recommended_amount is not None
                    else
                    "—"
                )

            )


        with st.container(
            border=True
        ):

            st.write(
                "**Policy Status:**",
                model_result.get(
                    "policy_status"
                )
                or
                "—"
            )

            st.write(
                "**Model Outcome:**",
                model_result.get(
                    "model_outcome"
                )
                or
                "—"
            )

            st.write(
                "**Original Workflow Route:**",
                model_result.get(
                    "workflow_route"
                )
                or
                "—"
            )


        st.info(
            "SmartLimit V4 is decision support. "
            "Requested amount is not an AI model input. "
            "Historical similarity affects confidence/review only, "
            "not the recommended amount. "
            "Final sanction remains a human Branch Manager decision."
        )


        # ====================================================
        # AUDIT TRAIL
        # ====================================================

        with st.expander(
            "Application Audit Trail"
        ):

            if not audit_history:

                st.write(
                    "No audit events available."
                )

            else:

                for event in audit_history:

                    st.write(
                        f"**{event.get('action', 'EVENT')}** "
                        f"— {event.get('actor_role', 'SYSTEM')} "
                        f"— {event.get('created_at', event.get('event_at', ''))}"
                    )


        # ====================================================
        # FINAL BRANCH MANAGER DECISION
        # ====================================================

        st.divider()

        st.markdown(
            "### Final Branch Manager Decision"
        )


        # ====================================================
        # BRANCH MANAGER CONTROLLED OVERRIDE ENGINE — STEP 7Q-C
        # ====================================================

        ai_smartlimit = float(
            smartlimit
            if smartlimit is not None
            else
            0
        )


        customer_requested_amount = float(
            requested_amount
        )


        # ----------------------------------------------------
        # Model-aligned sanction:
        # Cannot exceed what the customer requested.
        # ----------------------------------------------------

        if ai_smartlimit > 0:

            model_aligned_amount = min(
                customer_requested_amount,
                ai_smartlimit
            )

        else:

            model_aligned_amount = (
                customer_requested_amount
            )


        st.caption(
            "SmartLimit remains the AI recommendation. "
            "The Branch Manager may exercise controlled "
            "human judgement, but the final sanction cannot "
            "exceed the amount requested by the customer."
        )


        # ----------------------------------------------------
        # BM SANCTION CONTROL
        # ----------------------------------------------------

        proposed_sanction_amount = st.number_input(

            "Branch Manager Proposed Sanction Amount (₹)",

            min_value=0.0,

            max_value=float(
                customer_requested_amount
            ),

            value=float(
                model_aligned_amount
            ),

            step=5000.0,

            format="%.0f",

            help=(
                "You may reduce or increase the sanction. "
                "An upward override may exceed SmartLimit, "
                "but never the customer's requested amount."
            ),

            key=(
                "bm_proposed_amount_"
                +
                selected_bm_application_id
            )

        )


        proposed_sanction_amount = float(
            proposed_sanction_amount
        )


        # ----------------------------------------------------
        # DEVIATION FROM SMARTLIMIT
        # ----------------------------------------------------

        if ai_smartlimit > 0:

            override_rupees = (
                proposed_sanction_amount
                -
                ai_smartlimit
            )

            override_pct = (
                override_rupees
                /
                ai_smartlimit
            )

        else:

            override_rupees = 0.0
            override_pct = 0.0


        # ----------------------------------------------------
        # DETERMINE OVERRIDE TYPE
        # ----------------------------------------------------

        tolerance = 1.0


        customer_request_caps_model = bool(

            ai_smartlimit > 0

            and

            customer_requested_amount
            <
            ai_smartlimit

        )


        if (

            customer_request_caps_model

            and

            abs(
                proposed_sanction_amount
                -
                customer_requested_amount
            )
            <=
            tolerance

        ):

            override_direction = (
                "CUSTOMER_REQUEST_CAP"
            )

            warning_level = (
                "MODEL_ALIGNED"
            )


        elif (

            ai_smartlimit > 0

            and

            abs(
                proposed_sanction_amount
                -
                ai_smartlimit
            )
            <=
            tolerance

        ):

            override_direction = (
                "MODEL_ALIGNED"
            )

            warning_level = (
                "MODEL_ALIGNED"
            )


        elif (

            ai_smartlimit > 0

            and

            proposed_sanction_amount
            <
            ai_smartlimit

        ):

            override_direction = (
                "DOWNWARD_OVERRIDE"
            )

            warning_level = (
                "CONSERVATIVE"
            )


        elif (

            ai_smartlimit > 0

            and

            proposed_sanction_amount
            >
            ai_smartlimit

        ):

            override_direction = (
                "UPWARD_OVERRIDE"
            )


            if override_pct <= 0.10:

                warning_level = (
                    "CAUTION"
                )


            elif override_pct <= 0.20:

                warning_level = (
                    "MATERIAL"
                )


            else:

                warning_level = (
                    "HIGH"
                )


        else:

            override_direction = (
                "MANUAL_AMOUNT"
            )

            warning_level = (
                "CAUTION"
            )


        # ----------------------------------------------------
        # EXISTING RISK SIGNALS
        # ----------------------------------------------------

        current_risk_segment = (
            model_result.get(
                "risk_segment"
            )
            or
            ""
        )


        current_confidence = (
            model_result.get(
                "confidence"
            )
            or
            ""
        )


        current_stability = (
            model_result.get(
                "stability_grade"
            )
            or
            ""
        )


        current_ood_review = bool(
            model_result.get(
                "ood_review",
                False
            )
        )


        elevated_signals = []


        if current_risk_segment in {

            "Highest Risk",
            "High Risk"

        }:

            elevated_signals.append(
                f"{current_risk_segment} profile"
            )


        if current_confidence in {

            "Very Low",
            "Low"

        }:

            elevated_signals.append(
                f"{current_confidence} confidence"
            )


        if current_stability == "Review":

            elevated_signals.append(
                "stability review flag"
            )


        if current_ood_review:

            elevated_signals.append(
                "unusual / out-of-distribution profile"
            )


        # ----------------------------------------------------
        # ESCALATE UPWARD OVERRIDE WARNING WHEN OTHER
        # RISK / CONFIDENCE SIGNALS ARE PRESENT
        # ----------------------------------------------------

        if (

            override_direction
            ==
            "UPWARD_OVERRIDE"

            and

            elevated_signals

        ):

            if warning_level == "CAUTION":

                warning_level = "MATERIAL"

            elif warning_level == "MATERIAL":

                warning_level = "HIGH"


        # ----------------------------------------------------
        # INTERNAL DECISION DASHBOARD
        # ----------------------------------------------------

        o1, o2, o3, o4 = st.columns(
            4
        )


        with o1:

            st.metric(
                "Customer Requested",
                f"₹{customer_requested_amount:,.0f}"
            )


        with o2:

            st.metric(
                "SmartLimit",
                (
                    f"₹{ai_smartlimit:,.0f}"
                    if ai_smartlimit > 0
                    else
                    "—"
                )
            )


        with o3:

            st.metric(
                "Proposed Sanction",
                f"₹{proposed_sanction_amount:,.0f}"
            )


        with o4:

            if ai_smartlimit > 0:

                st.metric(
                    "Vs SmartLimit",
                    f"{override_pct:+.1%}"
                )

                st.caption(
                    f"Amount difference: "
                    f"₹{override_rupees:+,.0f}"
                )

            else:

                st.metric(
                    "Vs SmartLimit",
                    "—"
                )


        # ----------------------------------------------------
        # WARNING / IMPLICATION ENGINE
        # ----------------------------------------------------

        if override_direction == "CUSTOMER_REQUEST_CAP":

            st.success(
                "Customer-request aligned: the SmartLimit "
                "supports a higher amount, but approval is "
                "correctly capped at the amount requested "
                "by the customer."
            )


        elif warning_level == "MODEL_ALIGNED":

            st.success(
                "Model-aligned sanction: proposed approval "
                "is aligned with the SmartLimit recommendation."
            )


        elif warning_level == "CONSERVATIVE":

            st.info(
                "Conservative override: the proposed sanction "
                "is below SmartLimit. This reduces credit "
                "exposure, but may also reduce customer utility, "
                "loan fulfilment and booked value."
            )


        elif warning_level == "CAUTION":

            st.warning(
                "Upward override — Caution: the proposed sanction "
                "is above the AI-supported SmartLimit. A higher "
                "sanction may improve customer fulfilment or "
                "conversion, but increases credit exposure beyond "
                "the risk-calibrated recommendation."
            )


        elif warning_level == "MATERIAL":

            st.warning(
                "Material Model Override: the proposed sanction "
                "meaningfully exceeds SmartLimit. This may improve "
                "customer fulfilment, but creates additional exposure "
                "beyond the model-supported amount. If repayment "
                "performance deteriorates, potential loss severity "
                "could also be higher."
            )


        elif warning_level == "HIGH":

            st.error(
                "High Model Override Warning: the proposed sanction "
                "materially exceeds the risk-calibrated SmartLimit. "
                "This creates substantially greater exposure than "
                "the AI recommendation. Strong business rationale "
                "and explicit human accountability are required."
            )


        if (

            override_direction
            ==
            "UPWARD_OVERRIDE"

            and

            elevated_signals

        ):

            st.warning(
                "Additional warning signal(s): "
                +
                ", ".join(
                    elevated_signals
                )
                +
                ". These signals strengthen the case for "
                "careful human review before an upward override."
            )


        st.caption(
            "These are decision-support implications, not "
            "predicted probabilities or guaranteed outcomes."
        )


        # ----------------------------------------------------
        # OVERRIDE JUSTIFICATION
        # ----------------------------------------------------

        discretionary_override = bool(

            abs(
                proposed_sanction_amount
                -
                model_aligned_amount
            )
            >
            tolerance

        )


        override_justification = st.text_area(

            "Override Justification",

            placeholder=(
                "Required when sanction differs from the "
                "model-aligned amount. Example: verified "
                "additional income source, strong relationship "
                "history, business exception, or conservative "
                "exposure reduction."
            ),

            key=(
                "bm_override_justification_"
                +
                selected_bm_application_id
            )

        )


        # ----------------------------------------------------
        # EXPLICIT UPWARD OVERRIDE ACKNOWLEDGEMENT
        # ----------------------------------------------------

        upward_override_acknowledged = True


        if override_direction == "UPWARD_OVERRIDE":

            upward_override_acknowledged = st.checkbox(

                "I acknowledge that the proposed sanction "
                "exceeds SmartLimit and accept responsibility "
                "for this documented human override.",

                key=(
                    "bm_upward_override_ack_"
                    +
                    selected_bm_application_id
                )

            )


        branch_manager_notes = st.text_area(

            "Branch Manager Notes",

            placeholder=(
                "Record final credit observations, "
                "background-verification findings or "
                "reason for decision..."
            ),

            key=(
                "bm_notes_"
                +
                selected_bm_application_id
            )

        )


        background_check_confirmed = st.checkbox(

            "I confirm that required branch-level "
            "background checks have been completed.",

            key=(
                "bm_background_check_"
                +
                selected_bm_application_id
            )

        )


        approve_col, reject_col, return_col = st.columns(
            3
        )


        # ----------------------------------------------------
        # APPROVE
        # ----------------------------------------------------

        with approve_col:

            approve_clicked = st.button(

                "APPROVE",

                type="primary",

                use_container_width=True,

                key=(
                    "bm_approve_"
                    +
                    selected_bm_application_id
                )

            )


        # ----------------------------------------------------
        # REJECT
        # ----------------------------------------------------

        with reject_col:

            reject_clicked = st.button(

                "REJECT",

                use_container_width=True,

                key=(
                    "bm_reject_"
                    +
                    selected_bm_application_id
                )

            )


        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        with return_col:

            return_clicked = st.button(

                "RETURN TO LOAN OFFICER",

                use_container_width=True,

                key=(
                    "bm_return_"
                    +
                    selected_bm_application_id
                )

            )


        # ====================================================
        # APPROVAL ACTION
        # ====================================================

        if approve_clicked:

            if not background_check_confirmed:

                st.error(
                    "Please confirm completion of "
                    "branch-level background checks."
                )


            elif proposed_sanction_amount <= 0:

                st.error(
                    "Approved sanction amount must be "
                    "greater than zero."
                )


            elif (
                proposed_sanction_amount
                >
                customer_requested_amount
            ):

                st.error(
                    "Final sanction cannot exceed the "
                    "amount requested by the customer."
                )


            elif (
                discretionary_override
                and
                not override_justification.strip()
            ):

                st.error(
                    "Please provide an Override Justification "
                    "because the proposed sanction differs from "
                    "the model-aligned amount."
                )


            elif (
                override_direction
                ==
                "UPWARD_OVERRIDE"

                and

                not upward_override_acknowledged
            ):

                st.error(
                    "Please acknowledge the upward SmartLimit "
                    "override before approving."
                )


            else:

                # --------------------------------------------
                # Build decision note
                # --------------------------------------------

                decision_note_parts = []


                if branch_manager_notes.strip():

                    decision_note_parts.append(
                        branch_manager_notes.strip()
                    )


                if discretionary_override:

                    decision_note_parts.append(

                        "Override justification: "
                        +
                        override_justification.strip()

                    )


                decision_note_parts.append(

                    "SmartLimit: "
                    f"₹{ai_smartlimit:,.0f}; "
                    "Final sanction: "
                    f"₹{proposed_sanction_amount:,.0f}; "
                    "Override: "
                    f"₹{override_rupees:+,.0f} "
                    f"({override_pct:+.1%}); "
                    "Warning level: "
                    f"{warning_level}"

                )


                final_decision_notes = (
                    "\n".join(
                        decision_note_parts
                    )
                )


                # --------------------------------------------
                # SAVE FINAL HUMAN DECISION
                # --------------------------------------------

                save_branch_decision(

                    application_id=
                        selected_bm_application_id,

                    decision=
                        "APPROVED",

                    approved_amount=
                        float(
                            proposed_sanction_amount
                        ),

                    notes=
                        final_decision_notes,

                    decided_by=
                        "Branch Manager"

                )


                # --------------------------------------------
                # UPDATE WORKFLOW + FULL OVERRIDE AUDIT
                # --------------------------------------------

                update_application_status(

                    application_id=
                        selected_bm_application_id,

                    status=
                        "APPROVED",

                    current_owner=
                        "CUSTOMER",

                    actor_role=
                        "BRANCH_MANAGER",

                    actor_name=
                        "Branch Manager",

                    action=
                        "FINAL_APPROVAL_COMPLETED",

                    details={

                        "requested_amount":
                            float(
                                customer_requested_amount
                            ),

                        "smartlimit":
                            (
                                float(
                                    ai_smartlimit
                                )
                                if ai_smartlimit > 0
                                else
                                None
                            ),

                        "model_aligned_amount":
                            float(
                                model_aligned_amount
                            ),

                        "approved_amount":
                            float(
                                proposed_sanction_amount
                            ),

                        "override_direction":
                            override_direction,

                        "override_amount":
                            float(
                                override_rupees
                            ),

                        "override_pct":
                            float(
                                override_pct
                            ),

                        "override_warning_level":
                            warning_level,

                        "override_justification":
                            (
                                override_justification.strip()
                                if discretionary_override
                                else
                                None
                            ),

                        "upward_override_acknowledged":
                            bool(
                                upward_override_acknowledged
                            ),

                        "elevated_warning_signals":
                            elevated_signals,

                        "human_override":
                            bool(
                                discretionary_override
                            ),

                        "final_decision":
                            "APPROVED"

                    }

                )


                st.success(
                    f"Application approved for "
                    f"₹{proposed_sanction_amount:,.0f}. "
                    f"Customer status has been updated."
                )


                st.rerun()


        # ====================================================
        # REJECTION ACTION
        # ====================================================

        if reject_clicked:

            if not background_check_confirmed:

                st.error(
                    "Please confirm completion of "
                    "branch-level background checks."
                )


            elif not branch_manager_notes.strip():

                st.error(
                    "Please enter a reason for rejection "
                    "in Branch Manager Notes."
                )


            else:

                save_branch_decision(

                    application_id=
                        selected_bm_application_id,

                    decision=
                        "REJECTED",

                    approved_amount=
                        None,

                    notes=
                        branch_manager_notes.strip(),

                    decided_by=
                        "Branch Manager"

                )


                update_application_status(

                    application_id=
                        selected_bm_application_id,

                    status=
                        "REJECTED",

                    current_owner=
                        "CUSTOMER",

                    actor_role=
                        "BRANCH_MANAGER",

                    actor_name=
                        "Branch Manager",

                    action=
                        "FINAL_REJECTION_COMPLETED",

                    details={

                        "reason":
                            branch_manager_notes.strip(),

                        "final_decision":
                            "REJECTED"

                    }

                )


                st.success(
                    "Application rejected. "
                    "Customer status has been updated."
                )


                st.rerun()


        # ====================================================
        # RETURN TO LOAN OFFICER
        # ====================================================

        if return_clicked:

            if not branch_manager_notes.strip():

                st.error(
                    "Please enter the reason for returning "
                    "the application to the Loan Officer."
                )


            else:

                save_branch_decision(

                    application_id=
                        selected_bm_application_id,

                    decision=
                        "RETURNED",

                    approved_amount=
                        None,

                    notes=
                        branch_manager_notes.strip(),

                    decided_by=
                        "Branch Manager"

                )


                update_application_status(

                    application_id=
                        selected_bm_application_id,

                    status=
                        "RETURNED",

                    current_owner=
                        "LOAN_OFFICER",

                    actor_role=
                        "BRANCH_MANAGER",

                    actor_name=
                        "Branch Manager",

                    action=
                        "APPLICATION_RETURNED_TO_LOAN_OFFICER",

                    details={

                        "reason":
                            branch_manager_notes.strip(),

                        "final_decision":
                            "PENDING_REASSESSMENT"

                    }

                )


                st.success(
                    "Application returned to the Loan Officer "
                    "for reassessment."
                )


                st.rerun()


