import base64
import datetime
import io
import json
import re
import urllib.request
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Weekday Assembly | Executive CRO Audit Engine",
    page_icon="⚡",
    layout="wide",
)

def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

card_base64 = get_base64_image("Card.png")

# Function to fetch data directly from Microsoft Clarity Data Export API
def fetch_clarity_api_data(project_id, api_token, start_date, end_date, page_path=".*"):
    url = f"https://www.clarity.ms/export-data/api/v1/project/{project_id}/heatmaps"
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }
    
    num_days = (end_date - start_date).days + 1
    payload = {
        "numOfDays": num_days if num_days > 0 else 1,
        "dimension": "URL",
        "regex": page_path
    }
    
    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error connecting to Clarity API: {e}")
        return None

# Brand CSS Injection
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

    html, body, [class*="css"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        color: #181916 !important;
    }}

    .stApp {{
        background-color: #EAE4D8 !important;
    }}

    h1, h2, h3, h4, h5, h6, label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 700 !important;
        color: #564941 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
    }}

    p, span, div {{
        font-family: 'IBM Plex Mono', monospace !important;
        line-height: 1.45 !important;
    }}

    .brand-card {{
        background-image: url('data:image/png;base64,{card_base64}');
        background-size: 100% 100%;
        background-repeat: no-repeat;
        background-position: center;
        aspect-ratio: 1.34 / 1;
        width: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 12% 8% 18% 8%;
        box-sizing: border-box;
        text-align: center;
    }}

    .brand-card-label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        color: #564941 !important;
        text-transform: uppercase !important;
    }}

    .brand-card-value {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #181916 !important;
    }}

    .report-section {{
        background-color: #FFFEF0 !important;
        border: 1px solid #564941 !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }}

    div[data-testid="stButton"] > button, .stDownloadButton > button {{
        background-color: #564941 !important;
        color: #FFFEF0 !important;
        border-radius: 0px !important;
        border: 1px solid #181916 !important;
        padding: 0.75rem 1.5rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
    }}

    section[data-testid="stFileUploader"] {{
        background-color: #FFFEF0 !important;
        border: 1px solid #564941 !important;
        padding: 0.75rem 1rem !important;
    }}

    section[data-testid="stFileUploader"] button {{
        background-color: #564941 !important;
        color: #FFFEF0 !important;
        border-radius: 0px !important;
        border: none !important;
        padding: 0.4rem 0.8rem !important;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

# Sidebar Controls
st.sidebar.image("weekday assembly._NPGoat.png", width=200)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.title("CLIENT WORKSPACE")
active_client = st.sidebar.selectbox(
    "SELECT CLIENT PROJECT",
    ["DU/ER UK", "PARKIT EU", "HUF Worldwide EU", "Jansport EU"]
)

st.sidebar.title("DATE TIMEFRAME")
today = datetime.date.today()
start_date = st.sidebar.date_input("START DATE", today - datetime.timedelta(days=30))
end_date = st.sidebar.date_input("END DATE", today)

st.sidebar.title("JOURNEY SCOPE")
journey_scope = st.sidebar.selectbox(
    "SELECT WEBSITE SCOPE",
    ["ENTIRE SITE (FULL JOURNEY)", "PRODUCT PAGES (PDP)", "COLLECTION PAGES (PLP)", "HOMEPAGE"]
)

st.sidebar.markdown("---")
page = st.sidebar.radio(
    "NAVIGATION",
    [
        "1. CLARITY API DATA SYNC",
        "2. EXECUTIVE SUMMARY",
        "3. COMPONENT AUDIT",
        "4. DYNAMIC CRO RECOMMENDATIONS",
    ],
)

# Categorisation logic
def categorise_selector(selector):
    sel = str(selector).lower()

    if "pandectes" in sel or "cc-btn" in sel or "cc-close" in sel or "cookie" in sel or "cc-window" in sel:
        return "COOKIE CONSENT BANNER"

    if "klaviyo" in sel or ("needsclick" in sel and ("form" in sel or "input" in sel or "circle" in sel or "button" in sel or "div" in sel)):
        return "EMAIL POPUP / NEWSLETTER FORM"

    if "product-form__submit" in sel or "product-form__buttons" in sel or "button--sticky-atc" in sel or "add-to-cart" in sel:
        return "ADD TO CART BUTTON"
    if "product-form__input_size" in sel or "product-form__variant-input" in sel or "variant-picker" in sel or "size" in sel or "ks-chart" in sel or "_ks_text" in sel:
        if "ks-chart" in sel or "_ks_text" in sel or "size-chart" in sel:
            return "SIZE CHART WIDGET"
        return "SIZE SELECTOR OPTIONS"
    if "quantity__button" in sel or "icon-minus" in sel or "icon-plus" in sel or "quantity__input" in sel:
        return "QUANTITY SELECTOR (+/-)"
    if "swatch-circle" in sel or "sibling-swatch" in sel or "swatch-thumbnail" in sel or "card__swatch" in sel:
        if "card-wrapper" in sel or "product-grid" in sel or "card--product" in sel:
            return "PRODUCT CARD COLOUR SWATCH"
        return "COLOUR / SIBLING SWATCH"
    if "summary__title" in sel or "accordion__title" in sel or "product__accordion" in sel or ("summary" in sel and "product" in sel):
        return "PRODUCT ACCORDION / EXPANDABLE INFO TAB"
    if "product__media-list" in sel or "product__modal-opener" in sel or "product__media" in sel:
        match = re.search(r'slider__slide--full-width:nth-of-type\((\d+)\)', str(selector))
        slide_num = match.group(1) if match else "MAIN"
        return f"PRODUCT GALLERY (IMAGE {slide_num})"

    if "grid__toggle" in sel or "grid-toggle" in sel:
        return "PLP GRID LAYOUT TOGGLE (1-COL / 2-COL)"
    if "mobile-facets__open-wrapper" in sel or "mobile-facets__wrapper" in sel:
        return "PLP FILTER & SORT TOGGLE"
    if "facetfiltersformmobile" in sel or "mobile-facets" in sel or "filter-price" in sel or "price-lte" in sel or "price-gte" in sel or "facetswrapperdesktop" in sel or "facet-checkbox" in sel or "facets__disclosure" in sel:
        if "sort-radio" in sel or "sort" in sel or "sort_by" in sel:
            return "PLP SORTING OPTIONS"
        return "PLP FILTER DRAWER / APPLY BUTTON"
    if "breadcrumb" in sel:
        return "BREADCRUMB NAVIGATION LINK"

    if "slideshow-component" in sel or "banner__buttons" in sel or "banner--adapt" in sel or "hero" in sel:
        return "HERO SLIDESHOW / BANNER BUTTON"
    if "multicolumn-card" in sel or "multicolumn" in sel:
        return "FEATURED CATEGORY / MULTICOLUMN CARD"

    if "slider-button--next" in sel:
        return "GALLERY / CAROUSEL ARROW (NEXT)"
    if "slider-button--prev" in sel:
        return "GALLERY / CAROUSEL ARROW (PREV)"

    if "product-grid" in sel or "product-card" in sel or "card--product" in sel or "card-wrapper" in sel:
        return "PRODUCT CARD CLICK (GRID ITEM)"

    if "flag-selector" in sel or "localization-form" in sel:
        return "COUNTRY / LOCALIZATION SELECTOR"
    if "cart-modal" in sel or "cartmodal" in sel or "cart-drawer" in sel or "mini-cart" in sel:
        return "CART DRAWER / MODAL"
    if "search-in-modal" in sel or "header__search" in sel or "predictive-search" in sel or "search__button" in sel or "header__icon--search" in sel:
        return "HEADER SEARCH BAR / MODAL"
    if "icon-hamburger" in sel or "header__icon--menu" in sel or "menu-drawer" in sel or "site-nav" in sel or "header__inline-menu" in sel:
        if "menu-drawer__menu-item" in sel or "list-menu__item" in sel or "site-nav__link" in sel:
            return "NAVIGATION MENU LINK"
        return "MOBILE MENU TOGGLE (HAMBURGER)"
    if "header__heading-link" in sel or "header__logo" in sel:
        return "HEADER LOGO LINK"
    if "cart-icon-bubble" in sel or "cart-count-bubble" in sel or "header__icon--cart" in sel:
        return "HEADER CART BUBBLE"
    if "header-group" in sel or "announcement" in sel:
        return "ANNOUNCEMENT BAR LINK"
    if "footer" in sel or "newsletter" in sel or "subscribe" in sel:
        return "FOOTER / NEWSLETTER SIGNUP"

    last_node = str(selector).split(">")[-1]
    clean_node = re.sub(r':nth-of-type\(\d+\)', '', last_node)
    return f"OTHER: {clean_node.strip().upper()}"

# Main App Header
col_logo, col_space = st.columns([1, 3])
with col_logo:
    st.image("weekday assembly._NPGoat.png", width=260)

st.markdown("<br>", unsafe_allow_html=True)

# Shared Session State Initialization
if "consolidated" not in st.session_state:
    st.session_state.consolidated = None
if "report_title" not in st.session_state:
    st.session_state.report_title = ""
if "project_name" not in st.session_state:
    st.session_state.project_name = active_client

# PAGE 1: Clarity API Data Sync
if page == "1. CLARITY API DATA SYNC":
    st.title("Clarity API Journey Analytics")
    st.subheader(f"DIRECT SYNC — {active_client}")
    st.write(f"Fetching analytics for **{journey_scope}** from **{start_date}** to **{end_date}**.")

    if st.button("⚡ FETCH LIVE CLARITY API DATA"):
        client_key = active_client.lower().replace(" ", "_").replace("/", "")
        
        if "clarity_projects" in st.secrets and client_key in st.secrets["clarity_projects"]:
            proj_id = st.secrets["clarity_projects"][client_key]["project_id"]
            api_tok = st.secrets["clarity_projects"][client_key]["api_token"]
            
            regex_pattern = ".*"
            if journey_scope == "PRODUCT PAGES (PDP)":
                regex_pattern = ".*/products/.*"
            elif journey_scope == "COLLECTION PAGES (PLP)":
                regex_pattern = ".*/collections/.*"
            elif journey_scope == "HOMEPAGE":
                regex_pattern = "^https?://[^/]+/?$"

            with st.spinner("Connecting to Microsoft Clarity API..."):
                api_df = fetch_clarity_api_data(proj_id, api_tok, start_date, end_date, page_path=regex_pattern)
                if api_df is not None and not api_df.empty:
                    st.success("Successfully synchronized data from Microsoft Clarity!")
                    st.dataframe(api_df)
                else:
                    st.warning("No data returned for this date range and journey scope.")
        else:
            st.warning(f"⚠️ API credentials for '{active_client}' not found in Streamlit Secrets. Please configure `st.secrets`.")

    st.markdown("---")
    st.subheader("OR MANUAL CSV FALLBACK")
    uploaded_file = st.file_uploader("UPLOAD RAW CLARITY CSV EXPORT", type=["csv"])

    if uploaded_file is not None:
        try:
            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            raw_lines = content.splitlines()
            header_idx = next((i for i, line in enumerate(raw_lines) if '"Rank","Button"' in line), None)

            if header_idx is not None:
                data_str = "\n".join(raw_lines[header_idx:])
                df = pd.read_csv(io.StringIO(data_str))

                count_col = 'Clicks' if 'Clicks' in df.columns else 'Taps' if 'Taps' in df.columns else df.columns[2]
                df[count_col] = df[count_col].astype(str).str.replace(",", "").astype(int)
                df["Clean Label"] = df["Button"].apply(categorise_selector)
                df = df[df["Clean Label"] != "COOKIE CONSENT BANNER"]

                consolidated = (
                    df.groupby("Clean Label", as_index=False)
                    .agg(Clicks=(count_col, "sum"), Elements_Merged=("Button", "count"))
                    .sort_values(by="Clicks", ascending=False)
                )

                total_clicks = consolidated["Clicks"].sum()
                pct_col_name = f"% OF TOTAL {count_col.upper()}"
                consolidated[pct_col_name] = ((consolidated["Clicks"] / total_clicks) * 100 if total_clicks > 0 else 0).round(2)

                st.session_state.consolidated = consolidated
                st.session_state.count_col = count_col
                st.session_state.pct_col_name = pct_col_name

                st.success("CSV Uploaded and Consolidated Successfully!")
                st.dataframe(consolidated)
        except Exception as e:
            st.error(f"Error processing CSV: {e}")

# PAGE 2: Executive Summary
elif page == "2. EXECUTIVE SUMMARY":
    st.title("EXECUTIVE CRO AUDIT SUMMARY")
    st.markdown(
        f"""
        <div class="report-section">
            <h3>CLIENT: {active_client}</h3>
            <p><strong>JOURNEY SCOPE:</strong> {journey_scope}</p>
            <p><strong>TIMEFRAME:</strong> {start_date} to {end_date}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# PAGE 3: Component Audit
elif page == "3. COMPONENT AUDIT":
    st.title("UI COMPONENT DEEP DIVE")
    if st.session_state.consolidated is not None:
        st.dataframe(st.session_state.consolidated)
    else:
        st.warning("Please sync API data or upload a CSV on Page 1 first.")

# PAGE 4: CRO Recommendations
elif page == "4. CRO RECOMMENDATIONS":
    st.title("STRATEGIC CRO RECOMMENDATIONS")
    st.write("Dynamic CRO insights based on synchronized site journey metrics.")
