import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Data Sage Dashboard", layout="wide")

st.title("🦉 Data Sage: Interactive Dashboard")
st.write(
    "Upload your CSV or Excel file to generate dynamic, multi-dimensional charts and KPIs!"
)

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Basic cleaning
    df = df.dropna(axis=1, how="all")
    
    # Attempt to parse date columns
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    st.success("✅ File loaded!")

    # KPIs
    st.subheader("📊 Key Metrics")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Rows", df.shape[0])
    kpi2.metric("Total Columns", df.shape[1])
    missing_pct = (df.isnull().sum().sum() / df.size) * 100
    kpi3.metric("Missing Values (%)", f"{missing_pct:.2f}%")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    date_cols = df.select_dtypes(include="datetime").columns.tolist()

    # Trend analysis
    if date_cols and numeric_cols:
        st.subheader("📈 Trends Over Time")
        date_col = st.selectbox("Select date column", date_cols)
        num_col = st.selectbox("Select numeric column to trend", numeric_cols)

        trend_df = df.groupby(date_col)[num_col].sum().reset_index()
        fig_trend = px.line(
            trend_df,
            x=date_col,
            y=num_col,
            title=f"Trend of {num_col} over {date_col}",
            markers=True,
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # Grouped bar chart
    if categorical_cols and numeric_cols:
        st.subheader("📊 Grouped Bar Chart")
        cat_col = st.selectbox("Select categorical column", categorical_cols)
        num_col = st.selectbox("Select numeric column", numeric_cols, key="bar")

        bar_df = (
            df.groupby(cat_col)[num_col]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        fig_bar = px.bar(
            bar_df,
            x=cat_col,
            y=num_col,
            color=cat_col,
            title=f"{num_col} by {cat_col}",
            text_auto=True,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Scatter plot for numeric vs numeric
    if len(numeric_cols) >= 2:
        st.subheader("⚡ Scatter Plot: Compare Metrics")
        num_x = st.selectbox("X-axis numeric column", numeric_cols, key="xscatter")
        num_y = st.selectbox("Y-axis numeric column", numeric_cols, key="yscatter")
        fig_scatter = px.scatter(
            df,
            x=num_x,
            y=num_y,
            color=categorical_cols[0] if categorical_cols else None,
            title=f"{num_y} vs {num_x}",
            trendline="ols",
            size_max=10
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Optional: Heatmap (correlations)
    if len(numeric_cols) >= 2:
        st.subheader("🔥 Heatmap of Numeric Correlations")
        corr = df[numeric_cols].corr()
        fig_heatmap = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Heatmap",
            color_continuous_scale="RdBu_r"
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)

    st.caption(
        "All visualizations are dynamic and multi-dimensional for a true dashboard experience. Enjoy exploring!"
    )

else:
    st.warning("⚠️ Please upload a file to start your analysis.")
