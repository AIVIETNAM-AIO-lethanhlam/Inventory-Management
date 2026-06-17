import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Retail Store Inventory Management",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown(
    """
    <style>
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: 1px solid #2563EB !important;
        border-radius: 8px !important;
        box-shadow: none !important;
    }

    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border: 1px solid #22C55E !important;
        box-shadow: 0 0 0 1px #22C55E !important;
    }

    div[data-testid="stTextInput"] input {
        caret-color: #22C55E !important;
        cursor: text !important;
    }

    div[data-testid="stSelectbox"],
    div[data-testid="stSelectbox"] * {
        cursor: pointer !important;
    }

    div[data-testid="stDataFrame"],
    div[data-testid="stDataFrame"] * {
        opacity: 1 !important;
        filter: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

DATA_FILE = "retail_store_inventory.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_FILE)
    df["Date"] = pd.to_datetime(df["Date"])

    base_search_columns = [
        "Store ID",
        "Product ID",
        "Category",
        "Region",
        "Weather Condition",
        "Seasonality"
    ]

    df["base_search_text"] = (
        df[base_search_columns]
        .astype(str)
        .agg(" ".join, axis=1)
        .str.lower()
    )

    return df


df = load_data()

# =========================
# FEATURE ENGINEERING
# =========================

df["Estimated Revenue"] = (
    df["Units Sold"] *
    df["Price"] *
    (1 - df["Discount"] / 100)
)

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Month Name"] = df["Date"].dt.strftime("%b")
df["search_text"] = df["base_search_text"]

month_order = [
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug",
    "Sep", "Oct", "Nov", "Dec"
]

# =========================
# SESSION STATE
# =========================

if "active_search" not in st.session_state:
    st.session_state["active_search"] = ""

if "search_input" not in st.session_state:
    st.session_state["search_input"] = ""

# =========================
# SIDEBAR
# =========================

st.sidebar.title("Menu")

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Filter & Search Data"]
)

# =========================
# HEADER
# =========================

st.markdown(
    """
    <div style="
        background-color:#111827;
        padding:18px 25px;
        border-radius:10px;
        margin-bottom:25px;
        border:1px solid #374151;
    ">
        <h2 style="color:white; margin:0;">
            Retail Store Inventory Management
        </h2>
        <p style="color:#9CA3AF; margin:5px 0 0 0;">
            Inventory monitoring, reorder alert and retail analytics dashboard
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# =========================
# HELPER FUNCTIONS
# =========================

def draw_bar_chart(data, x_col, y_col, title):
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(data[x_col], data[y_col])
    ax.set_title(title)
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue ($)")
    ax.tick_params(axis="x", rotation=0)
    st.pyplot(fig)


def draw_pie_chart(data, label_col, value_col, title):
    fig, ax = plt.subplots(figsize=(5, 5))

    if data.empty or data[value_col].sum() == 0:
        ax.text(0.5, 0.5, "No data", ha="center", va="center")
        ax.axis("off")
    else:
        ax.pie(
            data[value_col],
            labels=data[label_col],
            autopct="%1.1f%%",
            startangle=90
        )
        ax.set_title(title)
        ax.axis("equal")

    st.pyplot(fig)


# =========================
# PAGE 1: DASHBOARD
# =========================

if page == "Dashboard":

    st.title("Retail Store Inventory Management Dashboard")

    total_products = df["Product ID"].nunique()
    total_stores = df["Store ID"].nunique()
    total_inventory = int(df["Inventory Level"].sum())
    total_revenue = df["Estimated Revenue"].sum()

    revenue_2022_total = df[df["Year"] == 2022]["Estimated Revenue"].sum()
    revenue_2023_total = df[df["Year"] == 2023]["Estimated Revenue"].sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Products", total_products)
    col2.metric("Total Stores", total_stores)
    col3.metric("Total Inventory", f"{total_inventory:,}")
    col4.metric("Total Revenue", f"${total_revenue:,.0f}")

    col5, col6 = st.columns(2)

    col5.metric("Total Revenue 2022", f"${revenue_2022_total:,.0f}")
    col6.metric("Total Revenue 2023", f"${revenue_2023_total:,.0f}")

    st.divider()

    st.subheader("Inventory Data Overview")

    st.dataframe(
        df[
            [
                "Date",
                "Store ID",
                "Product ID",
                "Category",
                "Region",
                "Inventory Level",
                "Units Sold",
                "Units Ordered",
                "Demand Forecast",
                "Price",
                "Discount",
                "Weather Condition",
                "Holiday/Promotion",
                "Competitor Pricing",
                "Seasonality"
            ]
        ],
        use_container_width=True
    )

    st.divider()

    # =========================
    # MONTHLY REVENUE BAR CHARTS
    # =========================

    st.subheader("Monthly Revenue Comparison")

    monthly_revenue = (
        df.groupby(["Year", "Month", "Month Name"])["Estimated Revenue"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Month"])
    )

    revenue_2022 = monthly_revenue[monthly_revenue["Year"] == 2022]
    revenue_2023 = monthly_revenue[monthly_revenue["Year"] == 2023]

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        draw_bar_chart(
            revenue_2022,
            "Month Name",
            "Estimated Revenue",
            "Revenue by Month - 2022"
        )

    with chart_col2:
        draw_bar_chart(
            revenue_2023,
            "Month Name",
            "Estimated Revenue",
            "Revenue by Month - 2023"
        )

    st.divider()

    # =========================
    # CATEGORY REVENUE PIE CHARTS
    # =========================

    st.subheader("Revenue Contribution by Category")

    category_revenue = (
        df.groupby(["Year", "Category"])["Estimated Revenue"]
        .sum()
        .reset_index()
    )

    category_2022 = category_revenue[category_revenue["Year"] == 2022]
    category_2023 = category_revenue[category_revenue["Year"] == 2023]

    pie_col1, pie_col2 = st.columns(2)

    with pie_col1:
        draw_pie_chart(
            category_2022,
            "Category",
            "Estimated Revenue",
            "Category Revenue Share - 2022"
        )

    with pie_col2:
        draw_pie_chart(
            category_2023,
            "Category",
            "Estimated Revenue",
            "Category Revenue Share - 2023"
        )

    st.divider()

    # =========================
    # STORE REVENUE BY REGION PIE CHARTS
    # =========================

    st.subheader("Store Revenue Share by Region")

    store_region_revenue = (
        df.groupby(["Year", "Region", "Store ID"])["Estimated Revenue"]
        .sum()
        .reset_index()
    )

    regions = sorted(df["Region"].dropna().unique().tolist())

    st.markdown("### Store Revenue Share by Region - 2022")

    region_cols_2022 = st.columns(4)

    for idx, region in enumerate(regions):
        with region_cols_2022[idx % 4]:
            data_region_2022 = store_region_revenue[
                (store_region_revenue["Year"] == 2022) &
                (store_region_revenue["Region"] == region)
            ]

            draw_pie_chart(
                data_region_2022,
                "Store ID",
                "Estimated Revenue",
                f"{region} - 2022"
            )

    st.markdown("### Store Revenue Share by Region - 2023")

    region_cols_2023 = st.columns(4)

    for idx, region in enumerate(regions):
        with region_cols_2023[idx % 4]:
            data_region_2023 = store_region_revenue[
                (store_region_revenue["Year"] == 2023) &
                (store_region_revenue["Region"] == region)
            ]

            draw_pie_chart(
                data_region_2023,
                "Store ID",
                "Estimated Revenue",
                f"{region} - 2023"
            )

        st.divider()

    # =========================
    # OVERSTOCKED PRODUCTS BY PRODUCT + CATEGORY
    # =========================

    st.subheader("Overstocked Products Analysis")

    product_inventory = (
        df.groupby(["Product ID", "Category"])
        .agg(
            avg_inventory=("Inventory Level", "mean"),
            avg_demand_forecast=("Demand Forecast", "mean"),
            total_units_sold=("Units Sold", "sum")
        )
        .reset_index()
    )

    product_inventory["overstock_gap"] = (
        product_inventory["avg_inventory"] -
        product_inventory["avg_demand_forecast"]
    )

    overstock_products = (
        product_inventory[product_inventory["overstock_gap"] > 0]
        .sort_values("overstock_gap", ascending=False)
        .head(10)
    )

    overstock_products["product_category"] = (
        overstock_products["Product ID"] + " - " + overstock_products["Category"]
    )

    st.markdown("### Top 10 Overstocked Products by Product and Category")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(
        overstock_products["product_category"],
        overstock_products["overstock_gap"]
    )
    ax.set_xlabel("Product ID - Category")
    ax.set_ylabel("Overstock Gap")
    ax.set_title("Top 10 Products with Highest Overstock Gap")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

    st.caption(
        "Overstock Gap = Average Inventory Level - Average Demand Forecast. "
        "This chart shows which specific products and categories have too much inventory."
    )

    st.divider()

    # =========================
    # INVENTORY TURNOVER BY PRODUCT + CATEGORY
    # =========================

    st.subheader("Inventory Turnover by Product")

    product_turnover = (
        df.groupby(["Product ID", "Category"])
        .agg(
            total_units_sold=("Units Sold", "sum"),
            avg_inventory=("Inventory Level", "mean")
        )
        .reset_index()
    )

    product_turnover["inventory_turnover"] = (
        product_turnover["total_units_sold"] /
        product_turnover["avg_inventory"]
    )

    top_product_turnover = (
        product_turnover
        .sort_values("inventory_turnover", ascending=False)
        .head(10)
    )

    top_product_turnover["product_category"] = (
        top_product_turnover["Product ID"] + " - " + top_product_turnover["Category"]
    )

    st.markdown("### Top 10 Products with Highest Inventory Turnover")

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(
        top_product_turnover["product_category"],
        top_product_turnover["inventory_turnover"]
    )
    ax.set_xlabel("Product ID - Category")
    ax.set_ylabel("Inventory Turnover")
    ax.set_title("Top 10 Products with Highest Inventory Turnover")
    ax.tick_params(axis="x", rotation=45)
    st.pyplot(fig)

    st.caption(
        "Inventory Turnover = Total Units Sold / Average Inventory Level. "
        "A higher value means the product sells faster relative to its inventory."
    )

    st.divider()

    # =========================
    # SEPARATE DEMAND TREND LINE CHARTS BY CATEGORY
    # =========================

    st.subheader("Category Demand Trend Over Time")

    # Chỉ lấy dữ liệu trong 2 năm chính: 2022 và 2023
    demand_df = df[df["Year"].isin([2022, 2023])].copy()

    monthly_category_demand = (
        demand_df.groupby(["Year", "Month", "Category"])["Demand Forecast"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Month"])
    )

    monthly_category_demand["Month Year"] = (
        monthly_category_demand["Year"].astype(str)
        + "-"
        + monthly_category_demand["Month"].astype(str).str.zfill(2)
    )

    categories = sorted(demand_df["Category"].unique().tolist())

    st.markdown("### Demand Forecast Trend by Each Category")

    for i in range(0, len(categories), 2):
        cols = st.columns(2)

        for j, category in enumerate(categories[i:i + 2]):
            with cols[j]:
                category_data = monthly_category_demand[
                    monthly_category_demand["Category"] == category
                ]

                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(
                    category_data["Month Year"],
                    category_data["Demand Forecast"],
                    marker="o"
                )

                ax.set_title(f"Demand Forecast Trend - {category}")
                ax.set_xlabel("Month")
                ax.set_ylabel("Total Demand Forecast")
                ax.tick_params(axis="x", rotation=45)

                st.pyplot(fig)

    st.caption(
        "Each line chart shows how demand forecast changes over time for one category. "
        "Only data from 2022 and 2023 is included."
    )

# =========================
# PAGE 2: FILTER & SEARCH
# =========================

elif page == "Filter & Search Data":

    st.title("Filter & Search Inventory Data")

    summary_container = st.container()

    st.divider()

    st.subheader("Filter Data")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        store_filter = st.selectbox(
            "Store ID",
            ["All"] + sorted(df["Store ID"].unique().tolist())
        )

    with col2:
        category_filter = st.selectbox(
            "Category",
            ["All"] + sorted(df["Category"].unique().tolist())
        )

    with col3:
        region_filter = st.selectbox(
            "Region",
            ["All"] + sorted(df["Region"].unique().tolist())
        )

    search_col1, search_col2, search_col3 = st.columns([5, 1, 1])

    with search_col1:
        search_text = st.text_input(
            "Search any data",
            placeholder="Search Store ID, Product ID, Category, Region, Weather, Seasonality...",
            key="search_input"
        )

    with search_col2:
        st.write("")
        st.write("")
        search_button = st.button("Search", use_container_width=True)

    with search_col3:
        st.write("")
        st.write("")
        clear_button = st.button("Clear", use_container_width=True)

    current_input = st.session_state["search_input"].strip().lower()

    if search_button or current_input != st.session_state.get("active_search", ""):
        st.session_state["active_search"] = current_input

    if clear_button:
        st.session_state["active_search"] = ""
        st.session_state["search_input"] = ""
        st.rerun()

    keyword = st.session_state.get("active_search", "")

    mask = pd.Series(True, index=df.index)

    if store_filter != "All":
        mask &= df["Store ID"].eq(store_filter)

    if category_filter != "All":
        mask &= df["Category"].eq(category_filter)

    if region_filter != "All":
        mask &= df["Region"].eq(region_filter)

    filtered_df = df[mask]

    if keyword:
        filtered_df = filtered_df[
            filtered_df["search_text"].str.contains(keyword, na=False, regex=False)
        ]

    with summary_container:
        st.subheader("Filtered Data Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Records", len(filtered_df))
        col2.metric("Total Units Sold", int(filtered_df["Units Sold"].sum()))
        col3.metric("Total Revenue", f"${filtered_df['Estimated Revenue'].sum():,.0f}")

        avg_price = round(filtered_df["Price"].mean(), 2)
        col4.metric("Average Price", avg_price)

        if keyword:
            st.caption(f"Active search keyword: `{keyword}`")

    st.divider()

    st.subheader("Search Result")

    st.write(f"Found **{len(filtered_df)}** records.")

    display_df = filtered_df.head(500)

    st.caption("Showing first 500 records for better performance.")

    st.dataframe(
        display_df[
            [
                "Date",
                "Store ID",
                "Product ID",
                "Category",
                "Region",
                "Inventory Level",
                "Units Sold",
                "Units Ordered",
                "Demand Forecast",
                "Price",
                "Discount",
                "Weather Condition",
                "Holiday/Promotion",
                "Competitor Pricing",
                "Seasonality",
            ]
        ],
        use_container_width=True
    )

    st.divider()

    st.subheader("Download Filtered Data")

    csv = (
        filtered_df
        .drop(
            columns=[
                "search_text",
                "base_search_text",
                "Year",
                "Month",
                "Month Name"
            ],
            errors="ignore"
        )
        .to_csv(index=False)
        .encode("utf-8")
    )

    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="filtered_inventory_data.csv",
        mime="text/csv"
    )