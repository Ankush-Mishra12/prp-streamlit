import streamlit as st
import pandas as pd
import pyodbc

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="PRP E-Commerce Analytics",
    page_icon="📊",
    layout="wide"
)
# ---------------------------------------------------------
# LOGIN
# ---------------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:

    st.title("🔐 PRP Analytics Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username == "Ankush" and password == "ankush@999":
            st.session_state.authenticated = True
            st.rerun()

        else:
            st.error("Invalid username or password")

    st.stop()
# ---------------------------------------------------------
# Sql server connection
# ---------------------------------------------------------
@st.cache_resource
def get_connection():

    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=prp_project;"
        "Trusted_Connection=yes;"
    )

    return conn
@st.cache_data
def load_data():

    conn = get_connection()

    website_pageviews = pd.read_sql(
        "SELECT * FROM website_pageviews",
        conn
    )

    website_sessions = pd.read_sql(
        "SELECT * FROM website_sessions",
        conn
    )

    orders = pd.read_sql(
        "SELECT * FROM orders",
        conn
    )

    order_items = pd.read_sql(
        "SELECT * FROM order_items",
        conn
    )

    order_item_refunds = pd.read_sql(
        "SELECT * FROM order_item_refunds",
        conn
    )

    products = pd.read_sql(
        "SELECT * FROM products",
        conn
    )

    return (
        website_pageviews,
        website_sessions,
        orders,
        order_items,
        order_item_refunds,
        products
    )
website_pageviews, website_sessions, orders, order_items, order_item_refunds, products = load_data()
# ---------------------------------------------------------
# KPI CALCULATIONS
# ---------------------------------------------------------

def calculate_kpis(orders, website_sessions):

    total_revenue = orders["price_usd"].sum()

    total_orders = orders["order_id"].nunique()

    total_sessions = website_sessions["website_session_id"].nunique()

    conversion_rate = (
        total_orders / total_sessions * 100
        if total_sessions > 0 else 0
    )

    aov = (
        total_revenue / total_orders
        if total_orders > 0 else 0
    )

    return (
        total_revenue,
        total_orders,
        total_sessions,
        conversion_rate,
        aov
    )


(
    total_revenue,
    total_orders,
    total_sessions,
    conversion_rate,
    aov
) = calculate_kpis(orders, website_sessions)


# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------

st.sidebar.title("📊 PRP Analytics")
st.sidebar.write("E-Commerce Analytics Application")

page = st.sidebar.radio(
    "Navigate",
    [
        "🏠 Overview",
        "📈 Descriptive Analysis",
        "🔍 Diagnostic Analysis",
        "🤖 Predictive Analysis"
    ]
)

# ---------------------------------------------------------
# OVERVIEW
# ---------------------------------------------------------

if page == "🏠 Overview":

    st.title("📊 PRP E-Commerce Analytics")

    st.markdown(
        """
        ### Business Analytics Dashboard

        This application provides:

        - Descriptive Analysis
        - Diagnostic Analysis
        - Predictive Analysis

        The analysis is based on e-commerce website
        sessions, pageviews, orders, products and refunds.
        """
    )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Revenue",
            f"${total_revenue:,.2f}"
        )

    with col2:
        st.metric(
            "Total Orders",
            f"{total_orders:,}"
        )

    with col3:
        st.metric(
            "Total Sessions",
            f"{total_sessions:,}"
        )

    with col4:
        st.metric(
            "Conversion Rate",
            f"{conversion_rate:.2f}%"
        )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Average Order Value",
            f"${aov:.2f}"
        )

    with col2:
        st.metric(
            "Analysis Coverage",
            "Descriptive • Diagnostic • Predictive"
        )

    st.info(
        "Use the navigation menu on the left to explore the analysis."
    )



# ---------------------------------------------------------
# DESCRIPTIVE ANALYSIS
# ---------------------------------------------------------

elif page == "📈 Descriptive Analysis":

    st.title("📈 Descriptive Analysis")

    st.write(
        "Historical business performance across sessions, "
        "orders, revenue and conversion."
    )

    # -----------------------------------------------------
    # DATE PREPARATION
    # -----------------------------------------------------

    orders["created_at"] = pd.to_datetime(
        orders["created_at"],
        errors="coerce"
    )

    website_sessions["created_at"] = pd.to_datetime(
        website_sessions["created_at"],
        errors="coerce"
    )

    # -----------------------------------------------------
    # OVERALL KPIs
    # -----------------------------------------------------

    total_revenue_desc = orders["price_usd"].sum()

    total_orders_desc = orders["order_id"].nunique()

    total_sessions_desc = website_sessions[
        "website_session_id"
    ].nunique()

    conversion_rate_desc = (
        total_orders_desc / total_sessions_desc * 100
        if total_sessions_desc > 0 else 0
    )

    revenue_per_order = (
        total_revenue_desc / total_orders_desc
        if total_orders_desc > 0 else 0
    )

    revenue_per_session = (
        total_revenue_desc / total_sessions_desc
        if total_sessions_desc > 0 else 0
    )

    # -----------------------------------------------------
    # KPI CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Revenue",
            f"${total_revenue_desc:,.2f}"
        )

    with col2:
        st.metric(
            "Total Orders",
            f"{total_orders_desc:,}"
        )

    with col3:
        st.metric(
            "Total Sessions",
            f"{total_sessions_desc:,}"
        )

    with col4:
        st.metric(
            "Conversion Rate",
            f"{conversion_rate_desc:.2f}%"
        )

    st.divider()

    # -----------------------------------------------------
    # EFFICIENCY KPIs
    # -----------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Revenue per Order",
            f"${revenue_per_order:.2f}"
        )

    with col2:
        st.metric(
            "Revenue per Session",
            f"${revenue_per_session:.2f}"
        )

    st.divider()

    # -----------------------------------------------------
    # QUARTERLY SESSION & ORDER VOLUME
    # -----------------------------------------------------

    orders_quarterly = (
        orders
        .dropna(subset=["created_at"])
        .assign(
            Quarter=orders["created_at"].dt.to_period("Q").astype(str)
        )
        .groupby("Quarter")
        .agg(
            Orders=("order_id", "nunique")
        )
        .reset_index()
    )

    sessions_quarterly = (
        website_sessions
        .dropna(subset=["created_at"])
        .assign(
            Quarter=website_sessions["created_at"]
            .dt.to_period("Q")
            .astype(str)
        )
        .groupby("Quarter")
        .agg(
            Sessions=("website_session_id", "nunique")
        )
        .reset_index()
    )

    quarterly_volume = pd.merge(
        sessions_quarterly,
        orders_quarterly,
        on="Quarter",
        how="outer"
    ).fillna(0)

    quarterly_volume = quarterly_volume.sort_values("Quarter")

    st.subheader("Quarterly Session & Order Volume")

    st.line_chart(
        quarterly_volume.set_index("Quarter")[
            ["Sessions", "Orders"]
        ]
    )

    st.caption(
        "Quarterly trend of website sessions and completed orders."
    )

    # -----------------------------------------------------
    # QUARTERLY REVENUE
    # -----------------------------------------------------

    quarterly_revenue = (
        orders
        .dropna(subset=["created_at"])
        .assign(
            Quarter=orders["created_at"]
            .dt.to_period("Q")
            .astype(str)
        )
        .groupby("Quarter")
        .agg(
            Revenue=("price_usd", "sum")
        )
        .reset_index()
    )

    quarterly_revenue = quarterly_revenue.sort_values("Quarter")

    st.subheader("Quarterly Revenue Trend")

    st.line_chart(
        quarterly_revenue.set_index("Quarter")[
            ["Revenue"]
        ]
    )

    st.caption(
        "Quarterly revenue trend across the business."
    )

    # -----------------------------------------------------
    # QUARTERLY CONVERSION & REVENUE EFFICIENCY
    # -----------------------------------------------------

    quarterly_efficiency = pd.merge(
        quarterly_volume,
        quarterly_revenue,
        on="Quarter",
        how="left"
    )

    quarterly_efficiency["Conversion Rate"] = (
        quarterly_efficiency["Orders"]
        / quarterly_efficiency["Sessions"]
        * 100
    )

    quarterly_efficiency["Revenue per Order"] = (
        quarterly_efficiency["Revenue"]
        / quarterly_efficiency["Orders"]
    )

    quarterly_efficiency["Revenue per Session"] = (
        quarterly_efficiency["Revenue"]
        / quarterly_efficiency["Sessions"]
    )

    st.subheader("Quarterly Conversion Rate")

    st.line_chart(
        quarterly_efficiency.set_index("Quarter")[
            ["Conversion Rate"]
        ]
    )

    st.subheader("Quarterly Revenue per Order")

    st.line_chart(
        quarterly_efficiency.set_index("Quarter")[
            ["Revenue per Order"]
        ]
    )

    st.subheader("Quarterly Revenue per Session")

    st.line_chart(
        quarterly_efficiency.set_index("Quarter")[
            ["Revenue per Session"]
        ]
    )

# ---------------------------------------------------------
# DIAGNOSTIC ANALYSIS
# ---------------------------------------------------------

elif page == "🔍 Diagnostic Analysis":

    st.title("🔍 Diagnostic Analysis")

    st.write(
        "This section investigates the factors and patterns "
        "behind business performance."
    )

    tab1, tab2, tab3 = st.tabs(
        [
            "Channel Analysis",
            "Customer & Device",
            "Product Analysis"
        ]
    )

# =====================================================
# CHANNEL ANALYSIS
# =====================================================

    with tab1:
        
        st.subheader("Marketing Channel Performance")

        channel_data = (
            website_sessions
            .groupby("utm_source")
            .agg(
                Sessions=("website_session_id", "nunique")
            )
            .reset_index()
        )

        channel_data["utm_source"] = (
            channel_data["utm_source"].fillna("Unknown")
        )

        st.dataframe(
            channel_data,
            use_container_width=True
        )

        channel_orders = (
            website_sessions[
                ["website_session_id", "utm_source"]
            ]
            .merge(
                orders[
                    ["order_id", "website_session_id", "price_usd"]
                ],
                on="website_session_id",
                how="left"
            )
        )

        channel_orders["utm_source"] = (
            channel_orders["utm_source"].fillna("Unknown")
        )

        channel_performance = (
            channel_orders
            .groupby("utm_source")
            .agg(
                Sessions=("website_session_id", "nunique"),
                Orders=("order_id", "nunique"),
                Revenue=("price_usd", "sum")
            )
            .reset_index()
        )

        channel_performance["Conversion Rate"] = (
            channel_performance["Orders"]
            / channel_performance["Sessions"]
            * 100
        )

        total_sessions_channel = channel_performance["Sessions"].sum()

        channel_performance["Session Share"] = (
            channel_performance["Sessions"]
            / total_sessions_channel
            * 100
        )

        channel_performance = channel_performance.sort_values("Sessions", ascending=False)

        st.subheader("Sessions by Marketing Channel")

        st.bar_chart(
            channel_performance.set_index("utm_source")[["Sessions"]]
        )

        st.subheader("Conversion Rate by Marketing Channel")

        st.bar_chart(
            channel_performance
            .sort_values("Conversion Rate", ascending=False)
            .set_index("utm_source")[["Conversion Rate"]]
        )


    with tab2:
        st.subheader("Device-wise Conversion Rate")

        device_orders = (
            website_sessions[["website_session_id", "device_type"]]
            .merge(
                orders[["order_id", "website_session_id"]],
                on="website_session_id",
                how="left"
            )
        )

        device_performance = (
            device_orders
            .groupby("device_type")
            .agg(
                Sessions=("website_session_id", "nunique"),
                Orders=("order_id", "nunique")
            )
            .reset_index()
        )

        device_performance["Conversion Rate"] = (
            device_performance["Orders"]
            / device_performance["Sessions"]
            * 100
        )

        st.dataframe(device_performance, use_container_width=True)

        st.bar_chart(
            device_performance.set_index("device_type")[["Conversion Rate"]]
        )

        st.caption(
            "Desktop sessions convert at a notably higher rate than mobile sessions."
        )

        st.divider()

        st.subheader("Cart Abandonment Rate by Device")

        pv_device = (
            website_pageviews[["website_session_id", "pageview_url"]]
            .merge(
                website_sessions[["website_session_id", "device_type"]],
                on="website_session_id",
                how="left"
            )
        )

        cart_sessions = (
            pv_device[pv_device["pageview_url"] == "/cart"]
            .groupby("device_type")["website_session_id"]
            .nunique()
            .reset_index(name="Cart Sessions")
        )

        purchase_sessions = (
            pv_device[pv_device["pageview_url"] == "/thank-you-for-your-order"]
            .groupby("device_type")["website_session_id"]
            .nunique()
            .reset_index(name="Purchase Sessions")
        )

        abandonment = pd.merge(cart_sessions, purchase_sessions, on="device_type", how="left")
        abandonment["Purchase Sessions"] = abandonment["Purchase Sessions"].fillna(0)

        abandonment["Cart Abandonment Rate"] = (
            (abandonment["Cart Sessions"] - abandonment["Purchase Sessions"])
            / abandonment["Cart Sessions"]
            * 100
        )

        st.dataframe(abandonment, use_container_width=True)

        st.bar_chart(
            abandonment.set_index("device_type")[["Cart Abandonment Rate"]]
        )

        st.caption(
            "Mobile sessions show a higher cart abandonment rate compared to desktop, "
            "suggesting checkout friction on smaller screens."
        )

        st.divider()

        st.subheader("New vs Repeat Session Share")

        repeat_split = (
            website_sessions["is_repeat_session"]
            .value_counts(normalize=True)
            .mul(100)
            .rename(index={0: "New", 1: "Repeat"})
            .reset_index()
        )
        repeat_split.columns = ["Session Type", "Share (%)"]

        st.dataframe(repeat_split, use_container_width=True)

        st.bar_chart(
            repeat_split.set_index("Session Type")[["Share (%)"]]
        )
        st.write("Customer & Device")

    with tab3:
        st.subheader("Primary Product Revenue Contribution")

        product_orders = (
            orders
            .merge(
                products,
                left_on="primary_product_id",
                right_on="product_id",
                how="left"
            )
        )

        product_revenue = (
            product_orders
            .groupby("product_name")
            .agg(
                Revenue=("price_usd", "sum"),
                Orders=("order_id", "nunique")
            )
            .reset_index()
            .sort_values("Revenue", ascending=False)
        )

        st.dataframe(product_revenue, use_container_width=True)

        st.bar_chart(
            product_revenue.set_index("product_name")[["Revenue"]]
        )

        st.caption(
            "The Original Mr. Fuzzy consistently leads in revenue contribution "
            "as the primary product across years."
        )

        st.divider()

        st.subheader("Most Common Product Combinations")

        item_counts = order_items.groupby("order_id")["product_id"].transform("count")

        multi_item_orders = order_items[item_counts > 1]

        pairs = pd.merge(
            multi_item_orders[["order_id", "product_id"]],
            multi_item_orders[["order_id", "product_id"]],
            on="order_id",
            suffixes=("_A", "_B")
        )

        pairs = pairs[
            pairs["product_id_A"] < pairs["product_id_B"]
        ]

        product_a = products[
            ["product_id", "product_name"]
        ].rename(
            columns={
                "product_id": "product_id_A",
                "product_name": "Product A"
            }
        )

        pairs = pairs.merge(
            product_a,
            on="product_id_A",
            how="left"
        )

        product_b = products[
            ["product_id", "product_name"]
        ].rename(
            columns={
                "product_id": "product_id_B",
                "product_name": "Product B"
            }
        )

        pairs = pairs.merge(
            product_b,
            on="product_id_B",
            how="left"
        )

        combo_counts = (
            pairs
            .groupby(["Product A", "Product B"])
            .size()
            .reset_index(name="Times Bought Together")
            .sort_values(
                "Times Bought Together",
                ascending=False
            )
        )

        st.dataframe(
            combo_counts,
            use_container_width=True
        )

        st.caption(
            "Shows which products are most frequently purchased together "
            "in the same order — useful for cross-sell recommendations."
        )

        st.write("Product Analysis")
        st.subheader("Most Common Product Combinations")

        chart_data = combo_counts.head(10).copy()

        chart_data["Combination"] = (
            chart_data["Product A"]
            + " + "
            + chart_data["Product B"]
        )

        st.bar_chart(
            chart_data.set_index("Combination")[
                ["Times Bought Together"]
            ]
        )


        
# ---------------------------------------------------------
# PREDICTIVE ANALYSIS
# ---------------------------------------------------------

elif page == "🤖 Predictive Analysis":

    st.title("🤖 Predictive Analysis")

    st.subheader("Repeat Visitor Prediction")

    st.write(
        """
        This model predicts whether a session belongs to a repeat visitor
        or a first-time visitor, using:

        - Device Type
        - Marketing Source (utm_source)
        - Marketing Campaign (utm_campaign)
        """
    )

    st.divider()

    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import OneHotEncoder
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score

    @st.cache_resource
    def train_model():
        features = ["device_type", "utm_source", "utm_campaign"]
        target = "is_repeat_session"

        df = website_sessions[features + [target]].copy()
        df["utm_source"] = df["utm_source"].fillna("direct")
        df["utm_campaign"] = df["utm_campaign"].fillna("direct")

        X = df[features]
        y = df[target]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        encoder = OneHotEncoder(handle_unknown="ignore")
        encoder.fit(X_train)
        X_train_encoded = encoder.transform(X_train)
        X_test_encoded = encoder.transform(X_test)

        model = LogisticRegression(class_weight="balanced", random_state=42)
        model.fit(X_train_encoded, y_train)

        y_pred = model.predict(X_test_encoded)
        y_pred_proba = model.predict_proba(X_test_encoded)[:, 1]

        report = classification_report(y_test, y_pred, output_dict=True)
        auc = roc_auc_score(y_test, y_pred_proba)

        return model, encoder, report, auc

    model, encoder, report, auc = train_model()

    st.subheader("Model Performance")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Accuracy", f"{report['accuracy']*100:.2f}%")
    with col2:
        st.metric("Recall (Repeat class)", f"{report['1']['recall']*100:.2f}%")
    with col3:
        st.metric("ROC-AUC", f"{auc:.3f}")

    st.divider()

    st.subheader("Try a Prediction")

    col1, col2, col3 = st.columns(3)

    with col1:
        device_input = st.selectbox(
            "Device Type", website_sessions["device_type"].dropna().unique()
        )
    with col2:
        source_input = st.selectbox(
            "Marketing Source", website_sessions["utm_source"].fillna("direct").unique()
        )
    with col3:
        campaign_input = st.selectbox(
            "Marketing Campaign", website_sessions["utm_campaign"].fillna("direct").unique()
        )

    if st.button("Predict"):
        input_df = pd.DataFrame({
            "device_type": [device_input],
            "utm_source": [source_input],
            "utm_campaign": [campaign_input]
        })

        input_encoded = encoder.transform(input_df)
        prediction = model.predict(input_encoded)[0]
        probability = model.predict_proba(input_encoded)[0][1]

        if prediction == 1:
            st.success(f"Predicted: Repeat Visitor (Confidence: {probability*100:.1f}%)")
        else:
            st.warning(f"Predicted: First-time Visitor (Confidence: {(1-probability)*100:.1f}%)")
    