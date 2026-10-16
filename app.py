import base64
import io
import re
import pandas as pd
import plotly.express as px
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Weekday Assembly | Executive CRO Audit Engine",
    page_icon="⚡",
    layout="wide",
)

# Helper function to convert local images for CSS background use
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

card_base64 = get_base64_image("Card.png")

# Helper function to parse Clarity export file names dynamically
def parse_clarity_filename(filename):
    base = filename.rsplit(".", 1)[0] if "." in filename else filename
    if base.startswith("Clarity_"):
        base = base[8:]

    date_match = re.search(r"_(\d{2}-\d{2}-\d{4}.*)$", base)
    if date_match:
        date_str = date_match.group(1)
        main_part = base[: date_match.start()]
    else:
        date_str = ""
        main_part = base

    parts = main_part.split("_")
    parts = [p.strip() for p in parts if p.strip() and p.strip() != "-"]

    heatmap_type = "Tap"
    device_type = "Mobile"
    project_parts = []

    for p in parts:
        p_lower = p.lower()
        if p_lower in ["tap", "scroll", "click", "area", "conversion", "attention"]:
            heatmap_type = p.capitalize()
        elif p_lower in ["mobile", "desktop", "tablet", "pc"]:
            if p_lower == "pc":
                device_type = "Desktop PC"
            else:
                device_type = p.capitalize()
        else:
            project_parts.append(p)

    project_name = (
        " ".join(project_parts).upper() if project_parts else "CLARITY PROJECT"
    )
    date_formatted = date_str.split()[0] if date_str else ""

    display_title = (
        f"{project_name} — {heatmap_type.upper()} ({device_type.upper()})"
    )
    if date_formatted:
        display_title += f" [{date_formatted}]"

    clean_file_prefix = (
        f"{project_name.replace(' ', '_')}_{heatmap_type}_{device_type.replace(' ', '_')}"
    )
    if date_formatted:
        clean_file_prefix += f"_{date_formatted}"

    export_filename = f"{clean_file_prefix}_Cleaned_Report.csv"

    return display_title, export_filename, project_name

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

    h1, h2, h3 {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 700 !important;
        color: #564941 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.1em !important;
    }}

    h4, h5, h6, label {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
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
        letter-spacing: 0.1em !important;
        margin-bottom: 0.25rem;
    }}

    .brand-card-value {{
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 1.8rem !important;
        font-weight: 700 !important;
        color: #181916 !important;
        letter-spacing: 0.05em !important;
    }}

    .report-section {{
        background-color: #FFFEF0 !important;
        border: 1px solid #564941 !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
    }}

    .disclaimer-note {{
        background-color: #FFFEF0 !important;
        border-left: 3px solid #564941 !important;
        padding: 0.75rem 1rem !important;
        font-size: 0.75rem !important;
        color: #564941 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-top: 1rem;
        margin-bottom: 1rem;
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
        letter-spacing: 0.1em !important;
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

# Sidebar Navigation & Multi-Client Selector
st.sidebar.image("weekday assembly._NPGoat.png", width=200)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

st.sidebar.title("CLIENT WORKSPACE")
active_client = st.sidebar.selectbox(
    "SELECT CLIENT PROJECT",
    ["DU/ER UK", "PARKIT EU", "HUF Worldwide EU", "Jansport EU"]
)

st.sidebar.markdown("---")
st.sidebar.title("NAVIGATION")
page = st.sidebar.radio(
    "SELECT VIEW",
    [
        "1. DATA REFINEMENT & UPLOAD",
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

# Dynamic CRO Recommendation Generator
def generate_dynamic_cro_insights(consolidated_df, pct_col_name):
    quick_wins = []
    strategic_tests = []

    component_dict = dict(zip(consolidated_df['Clean Label'], consolidated_df[pct_col_name]))

    swatch_share = sum(val for key, val in component_dict.items() if "SWATCH" in key)
    if swatch_share > 5.0:
        quick_wins.append(
            f"Explicit Variant Labeling ({swatch_share:.1f}% Share): High colour swatch engagement indicates strong variant consideration. Add explicit selected variant text (e.g., 'Colour: Olive') directly adjacent to swatches to reduce cognitive load."
        )
        strategic_tests.append(
            f"Variant Stock Status Teasers: Test displaying real-time stock availability indicators (e.g., 'Low Stock') directly when hovering or tapping colour swatches."
        )

    size_share = sum(val for key, val in component_dict.items() if "SIZE" in key)
    if size_share > 5.0:
        quick_wins.append(
            f"Size Chart Proximity ({size_share:.1f}% Share): Sizing represents a primary friction point. Pin the Size Guide directly adjacent to the size selector buttons."
        )
        strategic_tests.append(
            f"Interactive Fit Recommender: Test integrating an interactive fit calculator or auto-selecting default active sizes."
        )

    gallery_share = sum(val for key, val in component_dict.items() if "GALLERY" in key)
    if gallery_share < 5.0:
        quick_wins.append(
            f"Gallery Visual Teasers ({gallery_share:.1f}% Share): Low explicit image tapping suggests passive swiping. Add visible thumbnail tracks or numbered pill badges (e.g., '1 of 6') to prompt visual discovery."
        )
        strategic_tests.append(
            f"Short-Form Video as Slide 2: Test introducing a short product-in-motion video loop as the second slide in the main gallery slider."
        )

    accordion_share = sum(val for key, val in component_dict.items() if "ACCORDION" in key)
    if accordion_share > 8.0:
        quick_wins.append(
            f"Above-the-Fold Spec Elevation ({accordion_share:.1f}% Share): High accordion engagement shows users searching for detailed specs (Fabric/Fit). Surface key bullet points directly under the main title."
        )

    atc_share = sum(val for key, val in component_dict.items() if "ADD TO CART" in key)
    if atc_share < 5.0:
        quick_wins.append(
            f"CTA Contrast & Sticky Bar ({atc_share:.1f}% Share): Add-to-cart clicks represent under 5% of overall engagement. Increase CTA contrast using high-contrast brand styling (`#564941`) and implement a persistent sticky ATC bar on scroll."
        )

    return quick_wins, strategic_tests

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

# PAGE 1: Data Refinement & Upload
if page == "1. DATA REFINEMENT & UPLOAD":
    st.title("Clarity Heatmap Refinement Tool")
    st.write("Internal tool for consolidating duplicate HTML DOM selectors into human-legible CRO components.")

    uploaded_file = st.file_uploader("UPLOAD RAW CLARITY CSV EXPORT", type=["csv"])

    exclude_cookies = st.checkbox("EXCLUDE COOKIE CONSENT BANNER CLICKS FROM CRO ANALYSIS", value=True)

    if uploaded_file is not None:
        try:
            report_title, dynamic_export_filename, project_name = parse_clarity_filename(uploaded_file.name)
            st.session_state.report_title = report_title
            st.session_state.project_name = project_name if project_name else active_client

            content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
            raw_lines = content.splitlines()
            header_idx = next((i for i, line in enumerate(raw_lines) if '"Rank","Button"' in line), None)

            if header_idx is None:
                st.error("Invalid Clarity CSV format: Unable to locate data table header ('Rank','Button').")
            else:
                data_str = "\n".join(raw_lines[header_idx:])
                df = pd.read_csv(io.StringIO(data_str))

                if df.empty:
                    st.warning("⚠️ The uploaded Clarity CSV export contains 0 recorded clicks/taps for this page view and device segment.")
                else:
                    count_col = 'Clicks' if 'Clicks' in df.columns else 'Taps' if 'Taps' in df.columns else df.columns[2]
                    df[count_col] = df[count_col].astype(str).str.replace(",", "").astype(int)
                    df["Clean Label"] = df["Button"].apply(categorise_selector)

                    if exclude_cookies:
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

                    st.markdown("---")
                    m1, m2, m3 = st.columns(3)
                    with m1:
                        st.markdown(f'<div class="brand-card"><div class="brand-card-label">RAW CSV ROWS</div><div class="brand-card-value">{len(df):,}</div></div>', unsafe_allow_html=True)
                    with m2:
                        st.markdown(f'<div class="brand-card"><div class="brand-card-label">UI COMPONENTS</div><div class="brand-card-value">{len(consolidated):,}</div></div>', unsafe_allow_html=True)
                    with m3:
                        st.markdown(f'<div class="brand-card"><div class="brand-card-label">ANALYSED {count_col.upper()}</div><div class="brand-card-value">{total_clicks:,}</div></div>', unsafe_allow_html=True)

                    st.markdown("<br>", unsafe_allow_html=True)
                    st.subheader(f"CLICK DISTRIBUTION BREAKDOWN — {report_title}")

                    tab1, tab2 = st.tabs(["VISUAL BREAKDOWN", "DATA TABLE"])
                    with tab1:
                        fig_bar = px.bar(
                            consolidated.head(12), x="Clicks", y="Clean Label", orientation="h",
                            text=pct_col_name, labels={"Clicks": f"TOTAL {count_col.upper()}", "Clean Label": "COMPONENT"},
                            color_discrete_sequence=["#564941"]
                        )
                        fig_bar.update_layout(font_family="IBM Plex Mono", font_color="#181916", yaxis={"categoryorder": "total ascending"}, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=480, margin=dict(l=20, r=20, t=30, b=20))
                        fig_bar.update_traces(texttemplate="%{text:.2f}%", textposition="outside", marker_line_color="#181916", marker_line_width=1)
                        st.plotly_chart(fig_bar, use_container_width=True)

                        st.markdown(
                            f"""
                            <div class="disclaimer-note">
                                <strong>NOTE:</strong> UI components accounting for less than 1.00% of total {count_col.lower()} are consolidated into micro-click fallback categories to optimise executive reporting readability.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    with tab2:
                        st.dataframe(consolidated.style.format({"Clicks": "{:,}", pct_col_name: "{:.2f}%"}), use_container_width=True)

                        st.markdown(
                            f"""
                            <div class="disclaimer-note">
                                <strong>NOTE:</strong> UI components accounting for less than 1.00% of total {count_col.lower()} are consolidated into micro-click fallback categories to optimise executive reporting readability.
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    csv_buffer = consolidated.to_csv(index=False).encode("utf-8")
                    st.download_button("📥 DOWNLOAD BRANDED REPORT (.CSV)", data=csv_buffer, file_name=dynamic_export_filename, mime="text/csv")
        except Exception as e:
            st.error(f"Error processing file: {e}")

# PAGE 2: Executive Summary
elif page == "2. EXECUTIVE SUMMARY":
    st.title("EXECUTIVE CRO AUDIT SUMMARY")
    if st.session_state.consolidated is not None:
        c_df = st.session_state.consolidated
        top_component = c_df.iloc[0]["Clean Label"]
        top_pct = c_df.iloc[0][st.session_state.pct_col_name]

        st.markdown(
            f"""
            <div class="report-section">
                <h3>CLIENT: {active_client}</h3>
                <p><strong>REPORT TIMEFRAME:</strong> {st.session_state.report_title}</p>
                <p>This audit consolidates heatmaps and user touch points into clear CRO priorities. The single highest interacted UI component is <strong>{top_component}</strong>, capturing <strong>{top_pct}%</strong> of all non-cookie interactions.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.subheader("PRIMARY FINDINGS")
        st.markdown(
            f"""
            * **Dominant Interaction:** `{top_component}` drives the majority of engagement ({top_pct}% of total non-cookie clicks).
            * **Friction Identification:** Lower secondary component engagement indicates potential cognitive overload or hidden navigation elements.
            * **Mobile Gesture Insight:** Mobile swipe interactions are best paired with explicit visual cues (like carousel arrows or pagination counter links).
            """
        )
    else:
        st.warning("Please upload a Clarity CSV export on Page 1 first.")

# PAGE 3: Component Audit
elif page == "3. COMPONENT AUDIT":
    st.title("UI COMPONENT DEEP DIVE")
    if st.session_state.consolidated is not None:
        c_df = st.session_state.consolidated
        for idx, row in c_df.head(6).iterrows():
            st.markdown(
                f"""
                <div class="report-section">
                    <h4>COMPONENT #{idx+1}: {row['Clean Label']}</h4>
                    <p><strong>TOTAL INTERACTIONS:</strong> {row['Clicks']:,} ({row[st.session_state.pct_col_name]}%)</p>
                    <p><strong>CRO OBSERVATION:</strong> High volume on this element highlights a crucial step in the user decision path. Ensure clear feedback states and optimal tap targets.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.warning("Please upload a Clarity CSV export on Page 1 first.")

# PAGE 4: CRO Recommendations
elif page == "4. CRO RECOMMENDATIONS":
    st.title("STRATEGIC CRO RECOMMENDATIONS")
    if st.session_state.consolidated is not None:
        qw, st_tests = generate_dynamic_cro_insights(
            st.session_state.consolidated,
            st.session_state.pct_col_name
        )

        st.subheader("1. QUICK WINS (LOW EFFORT / HIGH IMPACT)")
        quick_wins_text = st.text_area(
            "EDITABLE QUICK WINS",
            value="\n\n".join(f"• {item}" for item in qw) if qw else "• Enlarge primary CTA tap targets on mobile viewports.",
            height=200
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("2. STRATEGIC AB TESTS (HIGH IMPACT)")
        strategic_tests_text = st.text_area(
            "EDITABLE STRATEGIC TESTS",
            value="\n\n".join(f"• {item}" for item in st_tests) if st_tests else "• Test sticky Add to Cart bar vs. static inline CTA button on mobile scroll.",
            height=200
        )
    else:
        st.warning("Please upload a Clarity CSV export on Page 1 first.")
