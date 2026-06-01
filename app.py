import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="CELINE CRM Intelligence",
    layout="wide"
)

# ---------- LOAD DATA (UPDATED) ----------
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/plotly/datasets/master/online_retail.csv"
    df = pd.read_csv(url, encoding="ISO-8859-1")

    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["CustomerID"])
    df = df[df["Quantity"] > 0]
    df = df[df["UnitPrice"] > 0]

    df["TotalSpend"] = df["Quantity"] * df["UnitPrice"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    df.rename(columns={
        "CustomerID": "Customer ID",
        "UnitPrice": "Price"
    }, inplace=True)

    return df

df = load_data()

# ---------- RFM ----------
@st.cache_data
def build_rfm(df):
    snapshot = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    rfm = df.groupby("Customer ID").agg(
        Recency=("InvoiceDate", lambda x: (snapshot - x.max()).days),
        Frequency=("InvoiceNo", "nunique"),
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

# ---------- UI ----------
st.title("CELINE CRM Intelligence Dashboard")

# KPIs
col1, col2, col3 = st.columns(3)

col1.metric("Total Revenue", f"£{df['TotalSpend'].sum():,.0f}")
col2.metric("Customers", f"{df['Customer ID'].nunique():,}")
col3.metric("Orders", f"{df['InvoiceNo'].nunique():,}")

# Segmentation chart
st.subheader("Customer Segments")

seg = rfm["Segment"].value_counts().reset_index()
seg.columns = ["Segment", "Count"]

fig1 = px.pie(seg, names="Segment", values="Count", hole=0.4)
st.plotly_chart(fig1, use_container_width=True)

# Revenue trend
st.subheader("Revenue Trend")

monthly = df.groupby("Month")["TotalSpend"].sum().reset_index()
fig2 = px.line(monthly, x="Month", y="TotalSpend", markers=True)
st.plotly_chart(fig2, use_container_width=True)

# Top products
st.subheader("Top Products")

products = df.groupby("Description")["TotalSpend"].sum().reset_index()\
    .sort_values("TotalSpend", ascending=False).head(10)

fig3 = px.bar(products, x="TotalSpend", y="Description", orientation="h")
st.plotly_chart(fig3, use_container_width=True)
