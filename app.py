import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="CELINE CRM Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- LOAD DATA (FIXED) ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("online_retail_II.csv", encoding="ISO-8859-1")

    # Clean column names
    df.columns = df.columns.str.strip()

    # Handle different dataset formats
    if "CustomerID" in df.columns:
        df.rename(columns={"CustomerID": "Customer ID"}, inplace=True)

    if "UnitPrice" in df.columns:
        df.rename(columns={"UnitPrice": "Price"}, inplace=True)

    if "InvoiceNo" in df.columns:
        df.rename(columns={"InvoiceNo": "Invoice"}, inplace=True)

    # Clean data
    df = df.dropna(subset=["Customer ID"])
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]

    # Feature engineering
    df["TotalSpend"] = df["Quantity"] * df["Price"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    return df

df = load_data()

# ---------------- RFM ----------------
@st.cache_data
def build_rfm(df):
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("Customer ID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        Frequency=("Invoice", "nunique"),
        Monetary=("TotalSpend", "sum")
    ).reset_index()

    rfm["R"] = pd.qcut(rfm["Recency"], 4, labels=[4,3,2,1]).astype(int)
    rfm["F"] = pd.qcut(rfm["Frequency"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)
    rfm["M"] = pd.qcut(rfm["Monetary"].rank(method="first"), 4, labels=[1,2,3,4]).astype(int)

    def segment(row):
        if row["R"] >= 3 and row["F"] >= 3 and row["M"] >= 3:
            return "Champion"
        elif row["R"] >= 3 and row["F"] >= 2:
            return "Loyal"
        elif row["R"] >= 3:
            return "New Client"
        elif row["R"] == 2:
            return "At Risk"
        else:
            return "Lost"

    rfm["Segment"] = rfm.apply(segment, axis=1)

    return rfm

rfm = build_rfm(df)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## CELINE CRM")
    search_id = st.text_input("Search Customer ID")
    selected_segment = st.selectbox("Segment", ["All"] + sorted(rfm["Segment"].unique()))

# ---------------- FILTERS ----------------
df_f = df.copy()
rfm_f = rfm.copy()

if selected_segment != "All":
    rfm_f = rfm[rfm["Segment"] == selected_segment]

# ---------------- HEADER ----------------
st.title("CELINE CRM Intelligence Dashboard")

# ---------------- KPIs ----------------
k1, k2, k3, k4 = st.columns(4)

k1.metric("Revenue", f"£{df['TotalSpend'].sum():,.0f}")
k2.metric("Clients", df["Customer ID"].nunique())
k3.metric("Orders", df["Invoice"].nunique())
k4.metric("AOV", f"£{df.groupby('Invoice')['TotalSpend'].sum().mean():,.2f}")

# ---------------- SEGMENT CHART ----------------
st.subheader("Customer Segmentation")

seg = rfm_f["Segment"].value_counts().reset_index()
seg.columns = ["Segment", "Count"]

fig1 = px.pie(seg, names="Segment", values="Count", hole=0.4)
st.plotly_chart(fig1, use_container_width=True)

# ---------------- REVENUE TREND ----------------
st.subheader("Revenue Trend")

monthly = df.groupby("Month")["TotalSpend"].sum().reset_index()
fig2 = px.line(monthly, x="Month", y="TotalSpend", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- TOP PRODUCTS ----------------
st.subheader("Top Products")

products = df.groupby("Description")["TotalSpend"].sum().reset_index()\
    .sort_values("TotalSpend", ascending=False).head(15)

fig3 = px.bar(products, x="TotalSpend", y="Description", orientation="h")
st.plotly_chart(fig3, use_container_width=True)

# ---------------- CLIENT VIEW ----------------
if search_id:
    try:
        cid = float(search_id)
        user = rfm[rfm["Customer ID"] == cid]

        if not user.empty:
            st.subheader("Client Profile")
            row = user.iloc[0]

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Segment", row["Segment"])
            c2.metric("Recency", row["Recency"])
            c3.metric("Orders", row["Frequency"])
            c4.metric("Spend", f"£{row['Monetary']:,.2f}")

    except:
        st.warning("Enter valid Customer ID")
