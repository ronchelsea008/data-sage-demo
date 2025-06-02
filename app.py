import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# --- App config and custom branding ---
st.set_page_config(page_title="🧙 Data Sage - Insight Wizard", layout="wide")

st.markdown("""
    <div style='background-color: #4A90E2; padding: 10px; border-radius: 10px; text-align: center; color: white;'>
        <h2>🔮 Data Sage: Insight Wizard</h2>
        <p>Powered by your brand</p>
    </div>
""", unsafe_allow_html=True)

st.write("👋 **Welcome!** Upload your data file below and let the magic begin:")

# --- File uploader ---
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # --- Read data ---
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    # --- Column classifications ---
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    # Remove typical unique ID columns
    cat_cols_cleaned = [c for c in cat_cols if not c.lower() in ['id', 'unique_id']]

    # --- Summary Statistics ---
    st.subheader("🔍 Summary Statistics")
    st.dataframe(df.describe(include='all').T)

    # --- Frequency charts ---
    st.subheader("🔢 Frequency Charts")
    freq_cols = st.multiselect("Select categorical columns to visualize", cat_cols_cleaned, default=cat_cols_cleaned[:2])
    col1, col2 = st.columns(2)
    for idx, col in enumerate(freq_cols):
        fig = px.histogram(df, x=col, color=col, title=f"Frequency of {col}")
        if idx % 2 == 0:
            col1.plotly_chart(fig, use_container_width=True)
        else:
            col2.plotly_chart(fig, use_container_width=True)

    # --- Date-based trends ---
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    if date_cols:
        st.subheader("📈 Trend Analysis Over Time")
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df_sorted = df.sort_values(by=date_col)

        num_trend_col = st.selectbox("Select a numeric column for trend plot", numeric_cols)
        fig_trend = px.line(df_sorted, x=date_col, y=num_trend_col, title=f"{num_trend_col} over time")
        st.plotly_chart(fig_trend, use_container_width=True)
        st.info(f"💡 **Insight**: Notice any peaks or patterns for `{num_trend_col}` over time?")

    # --- Correlation heatmap ---
    st.subheader("💡 Correlation Heatmap")
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='RdBu_r', title="Numeric Feature Correlations")
        st.plotly_chart(fig_corr, use_container_width=True)

    # --- Cross-tab Analysis ---
    st.subheader("🔗 Cross-Tab Analysis")
    if len(cat_cols_cleaned) >= 2:
        cross1 = st.selectbox("Select first categorical column", cat_cols_cleaned, key="cross1")
        cross2 = st.selectbox("Select second categorical column", cat_cols_cleaned, key="cross2")
        pivot = pd.crosstab(df[cross1], df[cross2], margins=True)
        st.dataframe(pivot)

        # Optional third dimension
        if len(cat_cols_cleaned) >= 3:
            cross3 = st.selectbox("Optional: Select third categorical column", cat_cols_cleaned, key="cross3")
            pivot_3d = pd.crosstab([df[cross1], df[cross3]], df[cross2], margins=True)
            pivot_3d_reset = pivot_3d.reset_index()
            pivot_3d_reset = pivot_3d_reset.loc[:, ~pivot_3d_reset.columns.duplicated()]
            st.dataframe(pivot_3d_reset)

    # --- Auto-generated insights ---
    st.subheader("✨ Key Insights Summary")
    insights = []
    if not df.empty:
        insights.append(f"- **Total rows**: {len(df)}")
        insights.append(f"- **Most common `{freq_cols[0]}`**: {df[freq_cols[0]].mode()[0]}")
        if date_cols:
            insights.append(f"- **Date range**: {df[date_col].min().date()} to {df[date_col].max().date()}")
        if len(numeric_cols) >= 2:
            top_corr = corr.abs().unstack().sort_values(ascending=False)
            top_corr = top_corr[top_corr < 1].reset_index().iloc[0]
            insights.append(f"- **Highest numeric correlation**: `{top_corr['level_0']}` vs `{top_corr['level_1']}` ({top_corr[0]:.2f})")
    for insight in insights:
        st.write(insight)

    st.success("🚀 Analysis complete! Let us know how we can customize further insights for your business.")

else:
    st.info("👆 Upload your data to explore insights and trends.")

# --- Footer ---
st.markdown("""
    <hr>
    <p style='text-align: center; font-size: small; color: gray;'>
        🚀 Made uniquely for your project by Data Sage
    </p>
""", unsafe_allow_html=True)
