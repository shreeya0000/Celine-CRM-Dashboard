import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(
    page_title="CELINE CRM Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600&family=Jost:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Jost', sans-serif;
}

.stApp {
    background-color: #FAFAF8;
}

[data-testid="stSidebar"] {
    background-color: #1C1C1C;
}
[data-testid="stSidebar"] * {
    color: #D4C9B8 !important;
    font-family: 'Jost', sans-serif !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stTextInput label,
[data-testid="stSidebar"] .stDateInput label {
    font-size: 11px !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #8A7F72 !important;
}

.brand-header {
    text-align: center;
    padding: 48px 0 32px 0;
    border-bottom: 1px solid #E2DDD6;
    margin-bottom: 40px;
}
.brand-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: 52px;
    font-weight: 300;
    letter-spacing: 0.35em;
    color: #1C1C1C;
    margin: 0;
    line-height: 1;
}
.brand-subtitle {
    font-family: 'Jost', sans-serif;
    font-size: 11px;
    font-weight: 400;
    letter-spacing: 0.25em;
    color: #8A7F72;
    margin-top: 10px;
    text-transform: uppercase;
}

.section-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px;
    font-weight: 400;
    color: #1C1C1C;
    letter-spacing: 0.05em;
    margin-bottom: 4px;
}
.section-sub {
    font-size: 12px;
    color: #8A7F72;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 20px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #E2DDD6;
    border-top: 2px solid #B8A898;
    border-radius: 2px;
    padding: 20px 16px;
}
[data-testid="stMetricLabel"] {
    font-size: 10px !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    color: #8A7F72 !important;
    font-family: 'Jost', sans-serif !important;
}
[data-testid="stMetricValue"] {
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 32px !important;
    font-weight: 400 !important;
    color: #1C1C1C !important;
}

.narrative-block {
    background: white;
    border: 1px solid #E2DDD6;
    border-left: 3px solid #B8A898;
    padding: 20px 24px;
    margin: 16px 0 28px 0;
    font-size: 14px;
    line-height: 1.8;
    color: #3C3C3C;
    border-radius: 0 2px 2px 0;
}
.narrative-block strong {
    color: #1C1C1C;
    font-weight: 500;
}

.insight-tag {
    display: inline-block;
    font-size: 10px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 2px;
    margin-bottom: 12px;
    font-family: 'Jost', sans-serif;
}
.tag-neutral { background: #F0EDE8; color: #6B6259; }
.tag-warning { background: #F5EDE8; color: #8B5E4A; }
.tag-positive { background: #EAF0EC; color: #4A7A5A; }

.rec-card {
    background: white;
    border: 1px solid #E2DDD6;
    border-radius: 2px;
    padding: 24px;
    height: 100%;
}
.rec-card-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 18px;
    font-weight: 500;
    color: #1C1C1C;
    margin-bottom: 14px;
    letter-spacing: 0.03em;
}
.rec-card ul {
    margin: 0;
    padding-left: 16px;
    color: #3C3C3C;
    font-size: 13px;
    line-height: 2;
}
.rec-card li {
    margin-bottom: 2px;
}

.thin-divider {
    border: none;
    border-top: 1px solid #E2DDD6;
    margin: 36px 0;
}

.stDataFrame {
    border: 1px solid #E2DDD6 !important;
    border-radius: 2px !important;
}

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

PASTEL_PALETTE = [
    "#A8C5D8",
    "#C5A8C8",
    "#A8C5B5",
    "#D8C5A8",
    "#D8A8B5",
]

SEGMENT_COLORS = {
    "Champion":   "#A8C5D8",
    "Loyal":      "#A8C5B5",
    "New Client": "#C5A8C8",
    "At Risk":    "#D8C5A8",
    "Lost":       "#D8A8B5",
}

@st.cache_data
def load_data():
    df = pd.read_excel("online_retail_II.xlsx", engine="openpyxl")
    df.columns = df.columns.str.strip()
    df = df.dropna(subset=["Customer ID"])
    df = df[df["Quantity"] > 0]
    df = df[df["Price"] > 0]
    df["TotalSpend"] = df["Quantity"] * df["Price"]
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)
    return df

df = load_data()

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
        elif row["R"] >= 3 and row["F"] <= 2:
            return "New Client"
        elif row["R"] == 2:
            return "At Risk"
        else:
            return "Lost"
    rfm["Segment"] = rfm.apply(segment, axis=1)
    return rfm

rfm = build_rfm(df)

with st.sidebar:
    st.markdown("<div style='padding: 24px 0 8px; font-family: Cormorant Garamond, serif; font-size: 22px; letter-spacing: 0.2em; color: #D4C9B8;'>CELINE</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase; color: #8A7F72; padding-bottom: 20px;'>CRM Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: #333; margin-bottom: 20px;'>", unsafe_allow_html=True)

    st.markdown("<p style='font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#8A7F72;margin-bottom:4px;'>Client Search</p>", unsafe_allow_html=True)
    search_id = st.text_input("", placeholder="Enter Customer ID", label_visibility="collapsed")

    st.markdown("<p style='font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#8A7F72;margin:16px 0 4px;'>Segment Filter</p>", unsafe_allow_html=True)
    segments = ["All"] + sorted(rfm["Segment"].unique().tolist())
    selected_segment = st.selectbox("", segments, label_visibility="collapsed")

    st.markdown("<p style='font-size:10px;letter-spacing:.15em;text-transform:uppercase;color:#8A7F72;margin:16px 0 4px;'>Date Range</p>", unsafe_allow_html=True)
    min_d, max_d = df["InvoiceDate"].min().date(), df["InvoiceDate"].max().date()
    date_range = st.date_input("", value=(min_d, max_d), min_value=min_d, max_value=max_d, label_visibility="collapsed")

    st.markdown("<hr style='border-color: #333; margin: 20px 0;'>", unsafe_allow_html=True)
    csv = rfm.to_csv(index=False).encode("utf-8")
    st.download_button("Download RFM Data", csv, "celine_rfm.csv", "text/csv", use_container_width=True)
    st.markdown("<hr style='border-color: #333; margin: 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:10px;color:#555;letter-spacing:.08em;'>CRM Analyst Portfolio<br>Built with Python and Streamlit</p>", unsafe_allow_html=True)

if len(date_range) == 2:
    df_f = df[(df["InvoiceDate"].dt.date >= date_range[0]) & (df["InvoiceDate"].dt.date <= date_range[1])]
else:
    df_f = df.copy()

rfm_f = rfm[rfm["Segment"] == selected_segment] if selected_segment != "All" else rfm.copy()

st.markdown("""
<div class='brand-header'>
    <div class='brand-name'>CELINE</div>
    <div class='brand-subtitle'>CRM &amp; Client Intelligence</div>
</div>
""", unsafe_allow_html=True)

total_clients    = rfm["Customer ID"].nunique()
champion_pct     = round(len(rfm[rfm["Segment"] == "Champion"]) / total_clients * 100, 1)
at_risk_pct      = round(len(rfm[rfm["Segment"] == "At Risk"]) / total_clients * 100, 1)
lost_pct         = round(len(rfm[rfm["Segment"] == "Lost"]) / total_clients * 100, 1)
loyal_count      = len(rfm[rfm["Segment"] == "Loyal"])
at_risk_count    = len(rfm[rfm["Segment"] == "At Risk"])
lost_count       = len(rfm[rfm["Segment"] == "Lost"])
champion_rev     = rfm[rfm["Segment"] == "Champion"]["Monetary"].sum()
total_rev        = rfm["Monetary"].sum()
champion_rev_pct = round(champion_rev / total_rev * 100, 1)
peak_month       = df_f.groupby("Month")["TotalSpend"].sum().idxmax()
peak_val         = df_f.groupby("Month")["TotalSpend"].sum().max()

if search_id:
    try:
        cid = float(search_id)
        c_rfm = rfm[rfm["Customer ID"] == cid]
        c_tx  = df[df["Customer ID"] == cid]
        if c_rfm.empty:
            st.warning("No client found with that ID.")
        else:
            row = c_rfm.iloc[0]
            st.markdown("<div class='section-title'>Client Profile</div><div class='section-sub'>Individual client view</div>", unsafe_allow_html=True)
            cc1, cc2, cc3, cc4 = st.columns(4)
            cc1.metric("Segment",        row["Segment"])
            cc2.metric("Days Since Purchase", int(row["Recency"]))
            cc3.metric("Total Orders",   int(row["Frequency"]))
            cc4.metric("Lifetime Spend", f"£{row['Monetary']:,.2f}")
            st.dataframe(c_tx[["InvoiceDate","Invoice","Description","Quantity","Price","TotalSpend"]].sort_values("InvoiceDate", ascending=False), use_container_width=True)
            st.markdown("<hr class='thin-divider'>", unsafe_allow_html=True)
    except:
        st.warning("Please enter a valid numeric Customer ID.")

st.markdown("<div class='section-title'>Executive Summary</div><div class='section-sub'>Period overview</div>", unsafe_allow_html=True)
st.markdown(f"""
<div class='narrative-block'>
    <strong>{total_clients:,} unique clients</strong> have been analysed across the full transaction history.
    RFM scoring identifies <strong>{champion_pct}% as Champions</strong>, collectively responsible for
    <strong>{champion_rev_pct}% of total revenue</strong> — a concentration that underscores the critical
    importance of protecting this segment. Concurrently, <strong>{at_risk_pct}% of clients are classified
    as At Risk</strong> and <strong>{lost_pct}% as Lost</strong>, representing a material re-engagement
    opportunity. The strategic priorities are clear: deepen Champion relationships through white-glove
    clienteling, and activate a structured win-back programme to recover declining segments before
    attrition becomes permanent.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Key Performance Indicators</div><div class='section-sub'>Filtered by selected date range</div>", unsafe_allow_html=True)
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Revenue",   f"£{df_f['TotalSpend'].sum():,.0f}")
k2.metric("Unique Clients",  f"{df_f['Customer ID'].nunique():,}")
k3.metric("Total Orders",    f"{df_f['Invoice'].nunique():,}")
k4.metric("Avg Order Value", f"£{df_f.groupby('Invoice')['TotalSpend'].sum().mean():,.2f}")

st.markdown("<hr class='thin-divider'>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Client Segmentation</div><div class='section-sub'>RFM analysis — recency, frequency, monetary scoring</div>", unsafe_allow_html=True)

ca, cb = st.columns(2)
with ca:
    seg_c = rfm_f["Segment"].value_counts().reset_index()
    seg_c.columns = ["Segment", "Count"]
    fig1 = px.pie(seg_c, names="Segment", values="Count",
                  title="Client Base by Segment",
                  color="Segment",
                  color_discrete_map=SEGMENT_COLORS,
                  hole=0.45)
    fig1.update_traces(textfont_size=12, textfont_family="Jost")
    fig1.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Jost", color="#3C3C3C", size=12),
        title=dict(font=dict(family="Cormorant Garamond", size=18, color="#1C1C1C")),
        legend=dict(font=dict(family="Jost", size=11)),
        margin=dict(t=50, b=20)
    )
    st.plotly_chart(fig1, use_container_width=True)

with cb:
    seg_v = rfm_f.groupby("Segment")["Monetary"].sum().reset_index().sort_values("Monetary")
    fig2 = px.bar(seg_v, x="Monetary", y="Segment", orientation="h",
                  title="Revenue by Segment",
                  color="Segment",
                  color_discrete_map=SEGMENT_COLORS)
    fig2.update_layout(
        paper_bgcolor="white", plot_bgcolor="white",
        font=dict(family="Jost", color="#3C3C3C", size=12),
        title=dict(font=dict(family="Cormorant Garamond", size=18, color="#1C1C1C")),
        showlegend=False,
        xaxis=dict(title="Total Revenue (£)", gridcolor="#F0EDE8"),
        yaxis=dict(title=""),
        margin=dict(t=50, b=20)
    )
    st.plotly_chart(fig2, use_container_width=True)

st.markdown(f"""
<div class='narrative-block'>
    <span class='insight-tag tag-warning'>At Risk Alert</span><br>
    <strong>{at_risk_count:,} clients ({at_risk_pct}% of the base)</strong> are showing signs of disengagement.
    Purchase recency has declined significantly within this cohort. Immediate action is recommended:
    a personalised re-engagement sequence deployed within 30 days, anchored around exclusive access
    or a curated product recommendation aligned to their purchase history.
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Client RFM Profiles</div><div class='section-sub'>Individual scoring — sorted by lifetime value</div>", unsafe_allow_html=True)
display_rfm = rfm_f[["Customer ID","Recency","Frequency","Monetary","Segment"]]\
    .sort_values("Monetary", ascending=False)\
    .rename(columns={
        "Recency":   "Days Since Last Purchase",
        "Frequency": "Total Orders",
        "Monetary":  "Lifetime Value (£)"
    })
st.dataframe(display_rfm, use_container_width=True, height=280)

st.markdown("<hr class='thin-divider'>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Revenue Trend</div><div class='section-sub'>Monthly performance across the full period</div>", unsafe_allow_html=True)
monthly = df_f.groupby("Month")["TotalSpend"].sum().reset_index()
fig3 = px.line(monthly, x="Month", y="TotalSpend",
               title="Monthly Revenue Performance",
               markers=True,
               color_discrete_sequence=["#A8C5D8"])
fig3.update_traces(line=dict(width=2), marker=dict(size=6, color="#8AAFC0"))
fig3.update_layout(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Jost", color="#3C3C3C", size=12),
    title=dict(font=dict(family="Cormorant Garamond", size=18, color="#1C1C1C")),
    xaxis=dict(tickangle=-45, gridcolor="#F0EDE8", title=""),
    yaxis=dict(gridcolor="#F0EDE8", title="Revenue (£)"),
    margin=dict(t=50, b=60)
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown(f"""
<div class='narrative-block'>
    <span class='insight-tag tag-neutral'>Trend Insight</span><br>
    Revenue peaked in <strong>{peak_month}</strong> at <strong>£{peak_val:,.0f}</strong>.
    Seasonal spikes correlate with gifting periods and collection launches.
    Recommendation: align the CRM campaign calendar to the 4 to 6 weeks preceding
    peak windows to maximise client activation during high-intent purchase periods.
</div>
""", unsafe_allow_html=True)

st.markdown("<hr class='thin-divider'>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Top Products</div><div class='section-sub'>Ranked by total revenue contribution</div>", unsafe_allow_html=True)
products = df_f.groupby("Description")["TotalSpend"].sum().reset_index()\
    .sort_values("TotalSpend", ascending=False).head(20)
fig4 = px.bar(products, x="TotalSpend", y="Description", orientation="h",
              title="Top 20 Products by Revenue",
              color="TotalSpend",
              color_continuous_scale=["#E8E0F0", "#C5A8C8", "#8A6A9A"])
fig4.update_layout(
    paper_bgcolor="white", plot_bgcolor="white",
    font=dict(family="Jost", color="#3C3C3C", size=11),
    title=dict(font=dict(family="Cormorant Garamond", size=18, color="#1C1C1C")),
    yaxis=dict(autorange="reversed", title=""),
    xaxis=dict(gridcolor="#F0EDE8", title="Revenue (£)"),
    coloraxis_showscale=False,
    height=580,
    margin=dict(t=50, b=20)
)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("<hr class='thin-divider'>", unsafe_allow_html=True)

st.markdown("<div class='section-title'>Strategic Recommendations</div><div class='section-sub'>Actionable priorities derived from RFM analysis</div>", unsafe_allow_html=True)

r1, r2, r3 = st.columns(3)

with r1:
    st.markdown(f"""
    <div class='rec-card'>
        <div class='insight-tag tag-neutral'>Champions</div>
        <div class='rec-card-title'>Retain &amp; Reward</div>
        <ul>
            <li>Assign dedicated stylist outreach to top 100 clients by lifetime value</li>
            <li>Offer first access to new collection previews and private events</li>
            <li>Introduce a tiered recognition programme with tangible milestones</li>
            <li>Track NPS quarterly within this segment to detect early churn signals</li>
            <li>Champions represent {champion_rev_pct}% of revenue — zero tolerance for attrition</li>
        </ul>
    </div>""", unsafe_allow_html=True)

with r2:
    st.markdown(f"""
    <div class='rec-card'>
        <div class='insight-tag tag-warning'>At Risk</div>
        <div class='rec-card-title'>Re-engage Now</div>
        <ul>
            <li>Launch a 30-day win-back sequence for all {at_risk_count:,} At Risk clients</li>
            <li>Personalise outreach based on previous category purchases</li>
            <li>Offer exclusive early access or a curated edit aligned to their profile</li>
            <li>Set a 60-day re-engagement deadline — after which reclassify as Lost</li>
            <li>A/B test subject lines and offer types to optimise conversion rate</li>
        </ul>
    </div>""", unsafe_allow_html=True)

with r3:
    st.markdown(f"""
    <div class='rec-card'>
        <div class='insight-tag tag-positive'>Loyal</div>
        <div class='rec-card-title'>Elevate to Champion</div>
        <ul>
            <li>{loyal_count:,} Loyal clients sit one tier below Champion status</li>
            <li>Introduce a clear threshold — spend or frequency — to unlock Champion benefits</li>
            <li>Communicate progress toward the threshold in CRM touchpoints</li>
            <li>Bundle cross-category recommendations to increase basket size</li>
            <li>Small uplift in this segment has an outsized revenue impact at scale</li>
        </ul>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;font-size:11px;color:#8A7F72;letter-spacing:0.12em;padding:20px 0;border-top:1px solid #E2DDD6;'>CELINE CRM Intelligence &nbsp;|&nbsp; CRM Analyst Portfolio &nbsp;|&nbsp; Python · Streamlit · Plotly</p>", unsafe_allow_html=True)
