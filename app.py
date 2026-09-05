
import streamlit as st
import textwrap
import pandas as pd
import numpy as np
import cloudpickle
import time
import os
import base64
from datetime import date


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
        "smartlimit_bundle.pkl"
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
# APPLICATION FORM
# ============================================================

with st.form(
    "smartlimit_application"
):


    # ========================================================
    # SECTION 1
    # ========================================================

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
            ),

            min_value=date(
                1940,
                1,
                1
            ),

            max_value=date.today()
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
            "Net Monthly Income (₹)",
            min_value=10000,
            max_value=2000000,
            value=50000,
            step=5000
        )


    st.divider()


    # ========================================================
    # SECTION 2
    # ========================================================

    st.subheader(
        "2. Credit & Repayment Profile"
    )


    st.caption(
        "In a production system these variables would normally "
        "be retrieved automatically from TVS and credit-bureau "
        "records. They are manually entered here only for the demo."
    )


    c1, c2, c3 = st.columns(3)


    with c1:

        avg_emi = st.number_input(
            "Existing Average Monthly EMI (₹)",
            min_value=0,
            max_value=500000,
            value=5000,
            step=1000
        )


        active_loans = st.number_input(
            "Number of Active Loans",
            min_value=0,
            max_value=20,
            value=1,
            step=1
        )


        outstanding_balance = st.number_input(
            "Total Outstanding Credit (₹)",
            min_value=0,
            max_value=10000000,
            value=50000,
            step=10000
        )


    with c2:

        max_previous_credit = st.number_input(
            "Highest Previous Credit Amount (₹)",
            min_value=0,
            max_value=10000000,
            value=150000,
            step=10000
        )


        credit_history_months = st.number_input(
            "Credit History Length (Months)",
            min_value=0,
            max_value=360,
            value=48,
            step=6
        )


        months_since_last_loan = st.number_input(
            "Months Since Last Loan",
            min_value=0,
            max_value=180,
            value=8,
            step=1
        )


    with c3:

        payment_count = st.number_input(
            "Total Historical Repayment Records",
            min_value=1,
            max_value=3000,
            value=50,
            step=1
        )


        successful_payment_count = st.number_input(
            "Successful Repayment Records",
            min_value=0,
            max_value=3000,
            value=48,
            step=1
        )


        external_risk_score = st.number_input(
            "External Credit Score",
            min_value=600,
            max_value=900,
            value=760,
            step=5,
            help=(
                "Demo representation of the external credit "
                "risk score available in the case dataset."
            )
        )


    risk_gradation = st.slider(
        "Internal Credit Risk Gradation",
        min_value=1,
        max_value=9,
        value=4,
        help=(
            "1 = stronger internal credit profile; "
            "9 = weaker / higher-risk profile."
        )
    )


    st.divider()


    # ========================================================
    # SECTION 3
    # ========================================================

    st.subheader(
        "3. Loan Requirement"
    )


    l1, l2, l3 = st.columns(3)


    with l1:

        requested_amount = st.number_input(
            "Requested Personal Loan (₹)",
            min_value=40000,
            max_value=600000,
            value=200000,
            step=5000
        )


    with l2:

        tenure = st.selectbox(
            "Preferred Tenure",
            [
                12,
                18,
                24,
                30,
                36,
                48,
                60
            ],
            format_func=
                lambda x:
                f"{x} months"
        )


    with l3:

        purpose = st.selectbox(
            "Loan Purpose",
            [
                "Medical",
                "Education",
                "Wedding",
                "Travel",
                "Home Improvement",
                "Consumer Purchase",
                "Debt Consolidation",
                "Other"
            ]
        )


    consent = st.checkbox(
        "I consent to the use of my credit information "
        "for this eligibility assessment."
    )


    submitted = st.form_submit_button(
        "REQUEST LOAN & CHECK SMARTLIMIT",
        type="primary"
    )


# ============================================================
# RUN ASSESSMENT
# ============================================================

if submitted:


    errors = []


    if not full_name.strip():

        errors.append(
            "Please enter the applicant's name."
        )


    digits = "".join(
        filter(
            str.isdigit,
            mobile
        )
    )


    if len(digits) != 10:

        errors.append(
            "Please enter a valid 10-digit mobile number."
        )


    if successful_payment_count > payment_count:

        errors.append(
            "Successful repayment records cannot exceed "
            "total repayment records."
        )


    if not consent:

        errors.append(
            "Consent is required to run the assessment."
        )


    if errors:

        for error in errors:

            st.error(
                error
            )


    else:


        # ====================================================
        # BACKEND PROCESS
        # ====================================================

        with st.status(
            "Running SmartLimit assessment...",
            expanded=True
        ) as status:


            st.write(
                "Reading applicant and credit profile..."
            )

            time.sleep(0.4)


            st.write(
                "Searching 37,498 historical borrower profiles..."
            )

            time.sleep(0.5)


            st.write(
                "Identifying the 25 closest historical analogues..."
            )

            time.sleep(0.5)


            st.write(
                "Estimating historical offer capacity..."
            )

            time.sleep(0.5)


            st.write(
                "Evaluating relative credit risk..."
            )

            time.sleep(0.5)


            result = predict_smartlimit(

                income=income,

                avg_emi=avg_emi,

                active_loans=active_loans,

                outstanding_balance=outstanding_balance,

                max_previous_credit=max_previous_credit,

                credit_history_months=credit_history_months,

                months_since_last_loan=months_since_last_loan,

                payment_count=payment_count,

                successful_payment_count=successful_payment_count,

                external_risk_score=external_risk_score,

                risk_gradation=risk_gradation,

                employment=employment
            )


            st.write(
                "Applying Guardrail B risk calibration..."
            )

            time.sleep(0.4)


            status.update(
                label="SmartLimit assessment complete",
                state="complete",
                expanded=False
            )


        # ====================================================
        # OUT-OF-RANGE CASE
        # ====================================================

        if not result[
            "reliable"
        ]:


            # ====================================================
            # NATIVE MANUAL REVIEW RESULT
            # ====================================================

            st.subheader(
                "Assessment Result"
            )


            with st.container(
                border=True
            ):

                st.error(
                    "Manual Review Recommended",
                    icon="⚠️"
                )


                st.write(
                    "This applicant's credit profile falls outside "
                    "the reliable historical range of the SmartLimit "
                    "matching engine."
                )


                st.write(
                    "No automatic loan offer has been generated. "
                    "The application should be routed to an "
                    "underwriter for manual assessment."
                )


            m1, m2 = st.columns(2)


            with m1:

                st.metric(
                    "Profile Match Confidence",
                    result[
                        "match_confidence"
                    ]
                )


            with m2:

                st.metric(
                    "Historical Match Distance",
                    f"{result['nearest_distance']:.2f}"
                )


            st.info(
                "This safety rule prevents SmartLimit from "
                "extrapolating to customer profiles that are "
                "too different from historical borrowers."
            )


        # ====================================================
        # RELIABLE CUSTOMER
        # ====================================================

        else:


            smartlimit = (
                result[
                    "smartlimit"
                ]
            )


            if requested_amount <= smartlimit:


                message_class = (
                    "eligible-box"
                )


                heading = (
                    "Requested amount is within your SmartLimit"
                )


                message = (
                    f"You requested "
                    f"{indian_currency(requested_amount)}. "
                    f"The request is within the model-recommended "
                    f"maximum offer."
                )


            else:


                message_class = (
                    "adjusted-box"
                )


                heading = (
                    "Recommended amount adjusted"
                )


                difference = (
                    requested_amount
                    -
                    smartlimit
                )


                message = (
                    f"The requested amount exceeds SmartLimit by "
                    f"{indian_currency(difference)}. "
                    f"A maximum offer of "
                    f"{indian_currency(smartlimit)} "
                    f"is recommended."
                )


            # =================================================
            # NATIVE SMARTLIMIT RESULT
            # =================================================

            st.subheader(
                "SmartLimit Assessment Result"
            )


            with st.container(
                border=True
            ):

                st.caption(
                    "RECOMMENDED MAXIMUM PERSONAL LOAN OFFER"
                )


                st.metric(
                    "Your SmartLimit",
                    indian_currency(
                        smartlimit
                    )
                )


                if requested_amount <= smartlimit:

                    st.success(
                        f"Requested amount is within SmartLimit. "
                        f"You requested "
                        f"{indian_currency(requested_amount)}, "
                        f"which is within the model-recommended "
                        f"maximum offer.",
                        icon="✅"
                    )


                else:

                    difference = (
                        requested_amount
                        -
                        smartlimit
                    )


                    st.warning(
                        f"Requested amount exceeds SmartLimit by "
                        f"{indian_currency(difference)}. "
                        f"The recommended maximum offer is "
                        f"{indian_currency(smartlimit)}.",
                        icon="⚠️"
                    )


# KEY METRICS
            # =================================================

            k1, k2, k3, k4 = st.columns(4)


            with k1:

                st.metric(
                    "Requested Amount",
                    indian_currency(
                        requested_amount
                    )
                )


            with k2:

                st.metric(
                    "Historical Offer Anchor",
                    indian_currency(
                        result[
                            "offer_anchor"
                        ]
                    )
                )


            with k3:

                st.metric(
                    "Relative Risk Score",
                    f"{result['risk_score']:.0f} / 100"
                )


            with k4:

                st.metric(
                    "Risk Segment",
                    result[
                        "risk_segment"
                    ]
                )


            # =================================================
            # EXPLAINABILITY
            # =================================================

            st.divider()

            st.subheader(
                "Why this offer?"
            )


            e1, e2 = st.columns(
                [1.35, 1]
            )


            with e1:

                multiplier_change = (
                    (
                        result[
                            "multiplier"
                        ]
                        -
                        1
                    )
                    *
                    100
                )


                st.markdown(
                    f"""
                    **Historical profile matching**

                    The applicant was compared with the full
                    historical reference population and matched
                    to the **25 most similar borrowers**.

                    **Historical Offer Anchor**

                    The similarity-weighted historical anchor is
                    approximately
                    **{indian_currency(result["offer_anchor"])}**.

                    **Risk calibration**

                    The applicant's relative risk score is
                    **{result["risk_score"]:.0f}/100**, placing
                    the profile in the
                    **{result["risk_segment"]}** segment.

                    Guardrail B therefore applies a
                    **{result["multiplier"]:.2f}×**
                    adjustment
                    (**{multiplier_change:+.0f}%**).
                    """
                )


            with e2:

                st.metric(
                    "Profile Match Confidence",
                    result[
                        "match_confidence"
                    ]
                )


                st.metric(
                    "Repayment Success Rate",
                    f"{result['repayment_rate']:.1f}%"
                )


                st.metric(
                    "Guardrail Multiplier",
                    f"{result['multiplier']:.2f}×"
                )


            # =================================================
            # APPLICATION SUMMARY
            # =================================================

            with st.expander(
                "View application summary"
            ):


                summary = pd.DataFrame({

                    "Applicant Information": [

                        "Applicant",
                        "Employment Type",
                        "Monthly Income",
                        "Average Existing EMI",
                        "Active Loans",
                        "Outstanding Credit",
                        "Maximum Previous Credit",
                        "Credit History",
                        "Repayment Success Rate",
                        "External Credit Score",
                        "Internal Risk Gradation",
                        "Requested Loan",
                        "Preferred Tenure",
                        "Purpose",
                        "Recommended SmartLimit"
                    ],


                    "Value": [

                        full_name,

                        employment,

                        indian_currency(
                            income
                        ),

                        indian_currency(
                            avg_emi
                        ),

                        str(
                            active_loans
                        ),

                        indian_currency(
                            outstanding_balance
                        ),

                        indian_currency(
                            max_previous_credit
                        ),

                        f"{credit_history_months} months",

                        f"{result['repayment_rate']:.1f}%",

                        str(
                            external_risk_score
                        ),

                        str(
                            risk_gradation
                        ),

                        indian_currency(
                            requested_amount
                        ),

                        f"{tenure} months",

                        purpose,

                        indian_currency(
                            smartlimit
                        )
                    ]
                })


                st.dataframe(
                    summary,
                    hide_index=True,
                    use_container_width=True
                )


            st.info(
                "SmartLimit is a decision-support recommendation. "
                "A production lending decision would additionally "
                "remain subject to KYC, fraud checks, credit policy, "
                "regulatory requirements and lender approval."
            )


# ============================================================
# MODEL ARCHITECTURE
# ============================================================

st.divider()


with st.expander(
    "How SmartLimit works"
):


    st.markdown(
        """
        **Applicant + Credit Profile**  
        ↓  
        **Historical Profile Matching Engine**  
        Searches 37,498 historical borrowers  
        ↓  
        **25 Closest Historical Analogues**  
        ↓  
        **Frozen XGBoost Offer Anchor**  
        ↓  
        **Frozen Logistic Risk Ranker**  
        ↓  
        **Guardrail B Risk Calibration**  
        ↓  
        **₹40,000 – ₹6,00,000 Business Limits**  
        ↓  
        **₹5,000 Operational Rounding**  
        ↓  
        **Recommended SmartLimit**
        """
    )


    st.caption(
        "Guardrail B multipliers — Highest → Lowest Risk: "
        "0.65× | 0.80× | 1.03× | 1.22× | 1.36×"
    )


st.markdown(
    """
    <div class="small-note" style="text-align:center; margin-top:25px;">

    TVS SmartLimit — Case Competition Prototype<br>
    Historical analogue matching is used for demonstration.
    Production implementation would use authenticated TVS
    and bureau data retrieval.

    </div>
    """,
    unsafe_allow_html=True
)
