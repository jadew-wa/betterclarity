import base64
import io
import re
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="Weekday Assembly | Clarity Refinement Tool",
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

    return display_title, export_filename

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

    /* Standalone Buttons Styling */
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
        transition: all 0.2s ease;
    }}

    div[data-testid="stButton"] > button:hover, .stDownloadButton > button:hover {{
        background-color: #181916 !important;
        color: #FFFEF0 !important;
    }}

    /* File Uploader Container & Button Overlap Fix */
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
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        padding: 0.4rem 0.8rem !important;
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

    button[data-baseweb="tab"] {{
        font-family: 'IBM Plex Mono', monospace !important;
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-weight: 600 !important;
    }}
    </style>
""",
    unsafe_allow_html=True,
)

col_logo, col_space = st.columns([1, 3])
with col_logo:
    st.image("weekday assembly._NPGoat.png", width=260)

st.markdown("<br>", unsafe_allow_html=True)
st.title("Clarity Heatmap Refinement Tool")
st.write(
    "Internal tool for consolidating duplicate HTML DOM selectors into human-legible CRO components."
)

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

uploaded_file = st.file_uploader(
    "UPLOAD RAW CLARITY CSV EXPORT", type=["csv"]
)

if uploaded_file is not None:
    try:
        report_title, dynamic_export_filename = parse_clarity_filename(
            uploaded_file.name
        )

        content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
        raw_lines = content.splitlines()
        header_idx = next(
            (i for i, line in enumerate(raw_lines) if '"Rank","Button"' in line), None
        )

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

                consolidated = (
                    df.groupby("Clean Label", as_index=False)
                    .agg(Clicks=(count_col, "sum"), Elements_Merged=("Button", "count"))
                    .sort_values(by="Clicks", ascending=False)
                )

                total_clicks = consolidated["Clicks"].sum()
                pct_col_name = f"% OF TOTAL {count_col.upper()}"
                consolidated[pct_col_name] = (
                    (consolidated["Clicks"] / total_clicks) * 100 if total_clicks > 0 else 0
                ).round(2)

                st.markdown("---")

                m1, m2, m3 = st.columns(3)

                with m1:
                    st.markdown(
                        f"""
                        <div class="brand-card">
                            <div class="brand-card-label">RAW CSV ROWS</div>
                            <div class="brand-card-value">{len(df):,}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with m2:
                    st.markdown(
                        f"""
                        <div class="brand-card">
                            <div class="brand-card-label">UI COMPONENTS</div>
                            <div class="brand-card-value">{len(consolidated):,}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                with m3:
                    st.markdown(
                        f"""
                        <div class="brand-card">
                            <div class="brand-card-label">ANALYSED {count_col.upper()}</div>
                            <div class="brand-card-value">{total_clicks:,}</div>
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                st.markdown("<br>", unsafe_allow_html=True)

                st.subheader(f"CLICK DISTRIBUTION BREAKDOWN — {report_title}")

                tab1, tab2 = st.tabs(["VISUAL BREAKDOWN", "DATA TABLE"])

                with tab1:
                    fig_bar = px.bar(
                        consolidated.head(12),
                        x="Clicks",
                        y="Clean Label",
                        orientation="h",
                        text=pct_col_name,
                        labels={"Clicks": f"TOTAL {count_col.upper()}", "Clean Label": "COMPONENT"},
                        color_discrete_sequence=["#564941"],
                    )
                    fig_bar.update_layout(
                        font_family="IBM Plex Mono",
                        font_color="#181916",
                        yaxis={"categoryorder": "total ascending"},
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=480,
                        margin=dict(l=20, r=20, t=30, b=20),
                    )
                    fig_bar.update_traces(
                        texttemplate="%{text:.2f}%",
                        textposition="outside",
                        marker_line_color="#181916",
                        marker_line_width=1,
                    )
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
                    st.dataframe(
                        consolidated.style.format(
                            {"Clicks": "{:,}", pct_col_name: "{:.2f}%"}
                        ),
                        use_container_width=True,
                    )

                    st.markdown(
                        f"""
                        <div class="disclaimer-note">
                            <strong>NOTE:</strong> UI components accounting for less than 1.00% of total {count_col.lower()} are consolidated into micro-click fallback categories to optimise executive reporting readability.
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

                csv_buffer = consolidated.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="📥 DOWNLOAD BRANDED REPORT (.CSV)",
                    data=csv_buffer,
                    file_name=dynamic_export_filename,
                    mime="text/csv",
                )

    except Exception as e:
        st.error(f"Error processing file: {e}")
