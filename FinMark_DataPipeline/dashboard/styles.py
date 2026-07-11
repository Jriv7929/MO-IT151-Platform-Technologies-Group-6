APP_CSS = """
<style>
    :root {
        --teal-950: #042F2E;
        --teal-900: #134E4A;
        --teal-800: #115E59;
        --teal-700: #0F766E;
        --teal-600: #0D9488;
        --cyan-500: #06B6D4;
        --cyan-400: #22D3EE;
        --cyan-300: #67E8F9;
        --cyan-100: #CFFAFE;
        --surface: #FFFFFF;
        --surface-soft: #F0FDFA;
        --page: #F5FAFA;
        --text: #083344;
        --muted: #5F7A7D;
        --border: #CCFBF1;
    }

    html,
    body,
    [class*="css"] {
        font-family: Inter, ui-sans-serif, system-ui, -apple-system,
            BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at top right,
                rgba(34, 211, 238, 0.10),
                transparent 32%
            ),
            linear-gradient(
                180deg,
                #F8FEFE 0%,
                var(--page) 100%
            );
        color: var(--text);
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1500px;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                var(--teal-950) 0%,
                var(--teal-900) 48%,
                var(--teal-800) 100%
            );
        border-right: 1px solid rgba(103, 232, 249, 0.18);
    }

    section[data-testid="stSidebar"] * {
        color: #ECFEFF;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(207, 250, 254, 0.16);
    }

    section[data-testid="stSidebar"] label {
        color: #CFFAFE !important;
        font-weight: 650;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 10px;
        padding: 0.34rem 0.45rem;
        transition: all 0.18s ease;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background-color: rgba(34, 211, 238, 0.12);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background:
            linear-gradient(
                90deg,
                rgba(6, 182, 212, 0.30),
                rgba(13, 148, 136, 0.18)
            );
        border-left: 3px solid var(--cyan-400);
    }

    .dashboard-title {
        font-size: 2.15rem;
        line-height: 1.1;
        font-weight: 850;
        letter-spacing: -0.02em;
        color: var(--teal-950);
        margin-bottom: 0;
    }

    .dashboard-subtitle {
        color: var(--muted);
        font-size: 0.96rem;
        margin-top: 0.4rem;
        margin-bottom: 1.5rem;
    }

    .kpi-card {
        position: relative;
        overflow: hidden;
        background:
            linear-gradient(
                145deg,
                rgba(255, 255, 255, 0.98),
                rgba(240, 253, 250, 0.96)
            );
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.1rem 1.25rem;
        box-shadow:
            0 10px 28px rgba(15, 118, 110, 0.08),
            0 2px 6px rgba(4, 47, 46, 0.04);
        min-height: 128px;
        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease;
    }

    .kpi-card::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 4px;
        background:
            linear-gradient(
                90deg,
                var(--teal-600),
                var(--cyan-400)
            );
    }

    .kpi-card::after {
        content: "";
        position: absolute;
        width: 90px;
        height: 90px;
        right: -32px;
        top: -36px;
        border-radius: 999px;
        background: rgba(34, 211, 238, 0.08);
    }

    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow:
            0 14px 34px rgba(15, 118, 110, 0.12),
            0 3px 8px rgba(4, 47, 46, 0.05);
    }

    .kpi-label {
        position: relative;
        z-index: 1;
        color: var(--teal-700);
        font-size: 0.80rem;
        font-weight: 750;
        text-transform: uppercase;
        letter-spacing: 0.055em;
    }

    .kpi-value {
        position: relative;
        z-index: 1;
        color: var(--teal-950);
        font-size: 1.82rem;
        font-weight: 850;
        margin-top: 0.42rem;
    }

    .kpi-caption {
        position: relative;
        z-index: 1;
        color: #6B8587;
        font-size: 0.78rem;
        margin-top: 0.38rem;
    }

    .section-card {
        background:
            linear-gradient(
                160deg,
                #FFFFFF,
                #F7FFFF
            );
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 1.05rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 118, 110, 0.06);
    }

    h1,
    h2,
    h3 {
        color: var(--teal-950);
        letter-spacing: -0.015em;
    }

    .status-healthy,
    .status-warning,
    .status-critical {
        display: inline-block;
        border-radius: 999px;
        padding: 0.33rem 0.78rem;
        font-weight: 750;
        font-size: 0.76rem;
        letter-spacing: 0.02em;
    }

    .status-healthy {
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #6EE7B7;
    }

    .status-warning {
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FCD34D;
    }

    .status-critical {
        background-color: #FEE2E2;
        color: #991B1B;
        border: 1px solid #FCA5A5;
    }

    button[data-baseweb="tab"] {
        font-weight: 700;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 5px 18px rgba(15, 118, 110, 0.05);
    }

    div[data-testid="stPlotlyChart"] {
        background-color: rgba(255, 255, 255, 0.94);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 0.25rem;
        box-shadow: 0 8px 24px rgba(15, 118, 110, 0.06);
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    .stDateInput > div > div {
        border-color: #99F6E4 !important;
        border-radius: 10px !important;
    }

    .stDownloadButton button,
    .stButton button {
        border-radius: 10px;
        font-weight: 720;
        border: 1px solid var(--cyan-500);
        background:
            linear-gradient(
                90deg,
                var(--teal-600),
                var(--cyan-500)
            );
        color: #FFFFFF;
        transition: all 0.18s ease;
    }

    .stDownloadButton button:hover,
    .stButton button:hover {
        border-color: var(--cyan-300);
        background:
            linear-gradient(
                90deg,
                var(--teal-700),
                var(--cyan-400)
            );
        color: #FFFFFF;
        box-shadow: 0 6px 18px rgba(6, 182, 212, 0.22);
    }

    .stAlert {
        border-radius: 12px;
    }

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }
</style>
"""
