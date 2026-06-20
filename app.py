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

    ax.bar(
        data[x_col],
        data[y_col],
        width=0.8
    )

    # Tính giới hạn trục Y
    min_revenue = data[y_col].min()
    max_revenue = data[y_col].max()

    padding = (max_revenue - min_revenue) * 0.2

    ax.set_ylim(
        min_revenue - padding,
        max_revenue + padding
    )

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

    # # =========================
    # # STORE REVENUE BY REGION PIE CHARTS
    # # =========================

    # st.subheader("Store Revenue Share by Region")

    # store_region_revenue = (
    #     df.groupby(["Year", "Region", "Store ID"])["Estimated Revenue"]
    #     .sum()
    #     .reset_index()
    # )

    # regions = sorted(df["Region"].dropna().unique().tolist())

    # st.markdown("### Store Revenue Share by Region - 2022")

    # region_cols_2022 = st.columns(4)

    # for idx, region in enumerate(regions):
    #     with region_cols_2022[idx % 4]:
    #         data_region_2022 = store_region_revenue[
    #             (store_region_revenue["Year"] == 2022) &
    #             (store_region_revenue["Region"] == region)
    #         ]

    #         draw_pie_chart(
    #             data_region_2022,
    #             "Store ID",
    #             "Estimated Revenue",
    #             f"{region} - 2022"
    #         )

    # st.markdown("### Store Revenue Share by Region - 2023")

    # region_cols_2023 = st.columns(4)

    # for idx, region in enumerate(regions):
    #     with region_cols_2023[idx % 4]:
    #         data_region_2023 = store_region_revenue[
    #             (store_region_revenue["Year"] == 2023) &
    #             (store_region_revenue["Region"] == region)
    #         ]

    #         draw_pie_chart(
    #             data_region_2023,
    #             "Store ID",
    #             "Estimated Revenue",
    #             f"{region} - 2023"
    #         )

    #     st.divider()
    
    # # =========================
    # # STORE REVENUE TREND BY REGION - LINE CHARTS
    # # =========================

    # st.subheader("Store Revenue Trend by Region")

    # line_df = df[df["Year"].isin([2022, 2023])].copy()

    # monthly_store_region_revenue = (
    #     line_df.groupby(["Year", "Month", "Month Name", "Region", "Store ID"])["Estimated Revenue"]
    #     .sum()
    #     .reset_index()
    #     .sort_values(["Year", "Month", "Region", "Store ID"])
    # )

    # for year in [2022, 2023]:
    #     st.markdown(f"### Monthly Store Revenue Trend by Region - {year}")

    #     year_data = monthly_store_region_revenue[
    #         monthly_store_region_revenue["Year"] == year
    #     ]

    #     fig, axes = plt.subplots(1, 4, figsize=(22, 5), sharey=False)

    #     legend_handles = []
    #     legend_labels = []

    #     for idx, region in enumerate(regions):
    #         ax = axes[idx]

    #         region_data = year_data[year_data["Region"] == region]

    #         for store_id in sorted(region_data["Store ID"].unique()):
    #             store_data = region_data[region_data["Store ID"] == store_id]

    #             line, = ax.plot(
    #                 store_data["Month Name"],
    #                 store_data["Estimated Revenue"],
    #                 marker="o",
    #                 label=store_id
    #             )

    #             if store_id not in legend_labels:
    #                 legend_handles.append(line)
    #                 legend_labels.append(store_id)

    #         ax.set_title(f"{region} - {year}")
    #         ax.set_xlabel("Month")
    #         ax.set_ylabel("Revenue ($)")
    #         ax.tick_params(axis="x", rotation=45)

    #     fig.legend(
    #         legend_handles,
    #         legend_labels,
    #         title="Store ID",
    #         loc="lower center",
    #         ncol=len(legend_labels),
    #         bbox_to_anchor=(0.5, -0.08)
    #     )

    #     fig.tight_layout(rect=[0, 0.12, 1, 1])

    #     st.pyplot(fig)
        
    # st.divider()
    
    # =========================
    # REGION REVENUE TREND
    # =========================

    st.subheader("Region Revenue Trend Overview")

    region_trend_df = df[df["Year"].isin([2022, 2023])].copy()

    monthly_region_revenue = (
        region_trend_df
        .groupby(["Year", "Month", "Month Name", "Region"])["Estimated Revenue"]
        .sum()
        .reset_index()
        .sort_values(["Year", "Month", "Region"])
    )

    for year in [2022, 2023]:
        st.markdown(f"### Monthly Revenue Trend by Region - {year}")

        year_region_data = monthly_region_revenue[
            monthly_region_revenue["Year"] == year
        ]

        fig, ax = plt.subplots(figsize=(12, 5))

        for region in sorted(year_region_data["Region"].unique()):
            region_data = year_region_data[
                year_region_data["Region"] == region
            ]

            ax.plot(
                region_data["Month Name"],
                region_data["Estimated Revenue"],
                marker="o",
                linewidth=2.5,
                label=region
            )

        ax.set_title(f"Revenue Trend by Region - {year}")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue ($)")

        ticks = ax.get_yticks()
        ax.set_yticklabels([f"{t/1e6:.1f}M" for t in ticks])

        ax.legend(
            title="Region",
            loc="lower center",
            bbox_to_anchor=(0.5, -0.3),
            ncol=4
        )

        fig.tight_layout()

        st.pyplot(fig)

    # =========================
    # OVERSTOCKED PRODUCTS ANALYSIS BY YEAR
    # =========================

    st.subheader("Overstocked Products Analysis")

    overstock_df = df[df["Year"].isin([2022, 2023])].copy()

    product_inventory_yearly = (
        overstock_df
        .groupby(["Year", "Category", "Product ID"])
        .agg(
            avg_inventory=("Inventory Level", "mean"),
            avg_demand_forecast=("Demand Forecast", "mean")
        )
        .reset_index()
    )

    product_inventory_yearly["overstock_gap"] = (
        product_inventory_yearly["avg_inventory"]
        - product_inventory_yearly["avg_demand_forecast"]
    )

    product_inventory_yearly["overstock_rate"] = (
        product_inventory_yearly["overstock_gap"]
        / product_inventory_yearly["avg_demand_forecast"]
        * 100
    )

    product_inventory_yearly = product_inventory_yearly[
        product_inventory_yearly["overstock_rate"] > 0
    ]

    product_inventory_yearly["product_category"] = (
        product_inventory_yearly["Product ID"]
        + " - "
        + product_inventory_yearly["Category"]
    )

    categories = sorted(product_inventory_yearly["Category"].unique())

    for year in [2022, 2023]:
        st.markdown(f"### Overstock Rate by Product and Category - {year}")

        year_overstock = product_inventory_yearly[
            product_inventory_yearly["Year"] == year
        ]

        # ===== 5 CATEGORY BAR CHARTS =====
        for i in range(0, len(categories), 2):
            cols = st.columns(2)

            for j, category in enumerate(categories[i:i + 2]):
                with cols[j]:
                    category_data = (
                        year_overstock[
                            year_overstock["Category"] == category
                        ]
                        .sort_values("Product ID")
                    )

                    fig, ax = plt.subplots(figsize=(8, 4))

                    ax.bar(
                        category_data["Product ID"],
                        category_data["overstock_rate"]
                    )

                    min_val = category_data["overstock_rate"].min()
                    max_val = category_data["overstock_rate"].max()
                    padding = (max_val - min_val) * 0.25

                    if padding == 0:
                        padding = max_val * 0.1

                    ax.set_ylim(
                        max(0, min_val - padding),
                        max_val + padding
                    )

                    ax.set_title(f"{category} - {year}")
                    ax.set_xlabel("Product ID")
                    ax.set_ylabel("Overstock Rate (%)")
                    ax.tick_params(axis="x", rotation=45)

                    st.pyplot(fig)

        # ===== TOP 10 OVERSTOCKED PRODUCTS IN SAME YEAR =====
        st.markdown(f"### Top 10 Products with Highest Overstock Rate - {year}")

        top10_overstock = (
            year_overstock
            .sort_values("overstock_rate", ascending=False)
            .head(10)
        )

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.bar(
            top10_overstock["product_category"],
            top10_overstock["overstock_rate"]
        )

        min_val = top10_overstock["overstock_rate"].min()
        max_val = top10_overstock["overstock_rate"].max()
        padding = (max_val - min_val) * 0.25

        if padding == 0:
            padding = max_val * 0.1

        ax.set_ylim(
            max(0, min_val - padding),
            max_val + padding
        )

        ax.set_title(f"Top 10 Products with Highest Overstock Rate - {year}")
        ax.set_xlabel("Product ID - Category")
        ax.set_ylabel("Overstock Rate (%)")
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)

        st.caption(
            "Overstock Rate (%) = "
            "(Average Inventory Level - Average Demand Forecast) / "
            "Average Demand Forecast × 100"
        )

        st.divider()

        # =========================
    # INVENTORY TURNOVER BY PRODUCT + CATEGORY BY YEAR
    # =========================

    st.subheader("Inventory Turnover by Product")

    turnover_df = df[df["Year"].isin([2022, 2023])].copy()

    product_turnover_yearly = (
        turnover_df
        .groupby(["Year", "Category", "Product ID"])
        .agg(
            total_units_sold=("Units Sold", "sum"),
            avg_inventory=("Inventory Level", "mean")
        )
        .reset_index()
    )

    product_turnover_yearly["inventory_turnover"] = (
        product_turnover_yearly["total_units_sold"]
        / product_turnover_yearly["avg_inventory"]
    )

    product_turnover_yearly = product_turnover_yearly[
        product_turnover_yearly["avg_inventory"] > 0
    ]

    product_turnover_yearly["product_category"] = (
        product_turnover_yearly["Product ID"]
        + " - "
        + product_turnover_yearly["Category"]
    )

    categories_turnover = sorted(product_turnover_yearly["Category"].unique())

    for year in [2022, 2023]:
        st.markdown(f"### Inventory Turnover by Product and Category - {year}")

        year_turnover = product_turnover_yearly[
            product_turnover_yearly["Year"] == year
        ]

        # ===== 5 CATEGORY BAR CHARTS =====
        for i in range(0, len(categories_turnover), 2):
            cols = st.columns(2)

            for j, category in enumerate(categories_turnover[i:i + 2]):
                with cols[j]:
                    category_data = (
                        year_turnover[
                            year_turnover["Category"] == category
                        ]
                        .sort_values("Product ID")
                    )

                    fig, ax = plt.subplots(figsize=(8, 4))

                    ax.bar(
                        category_data["Product ID"],
                        category_data["inventory_turnover"]
                    )

                    min_val = category_data["inventory_turnover"].min()
                    max_val = category_data["inventory_turnover"].max()
                    padding = (max_val - min_val) * 0.25

                    if padding == 0:
                        padding = max_val * 0.1

                    ax.set_ylim(
                        max(0, min_val - padding),
                        max_val + padding
                    )

                    ax.set_title(f"{category} - {year}")
                    ax.set_xlabel("Product ID")
                    ax.set_ylabel("Inventory Turnover")
                    ax.tick_params(axis="x", rotation=45)

                    st.pyplot(fig)

        # ===== TOP 10 INVENTORY TURNOVER IN SAME YEAR =====
        st.markdown(f"### Top 10 Products with Highest Inventory Turnover - {year}")

        top10_turnover = (
            year_turnover
            .sort_values("inventory_turnover", ascending=False)
            .head(10)
        )

        fig, ax = plt.subplots(figsize=(12, 5))

        ax.bar(
            top10_turnover["product_category"],
            top10_turnover["inventory_turnover"]
        )

        min_val = top10_turnover["inventory_turnover"].min()
        max_val = top10_turnover["inventory_turnover"].max()
        padding = (max_val - min_val) * 0.25

        if padding == 0:
            padding = max_val * 0.1

        ax.set_ylim(
            max(0, min_val - padding),
            max_val + padding
        )

        ax.set_title(f"Top 10 Products with Highest Inventory Turnover - {year}")
        ax.set_xlabel("Product ID - Category")
        ax.set_ylabel("Inventory Turnover")
        ax.tick_params(axis="x", rotation=45)

        st.pyplot(fig)

        st.caption(
            "Inventory Turnover = Total Units Sold / Average Inventory Level. "
            "A higher value means the product sells faster relative to its average inventory."
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