import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Data Sage Dashboard", layout="wide")
st.title("🦉 Data Sage: Interactive Dashboard")
st.write("Upload your CSV or Excel file to generate dynamic, multi-dimensional charts and KPIs!")

# --------- Header detection helper ---------
def detect_header_row(uploaded_file, file_type):
    if file_type == "csv":
        preview = pd.read_csv(uploaded_file, header=None, nrows=15)
    else:
        preview = pd.read_excel(uploaded_file, header=None, nrows=15)

    scores = []
    for i, row in preview.iterrows():
        filled = row.count()
        unique = row.nunique()
        score = filled + unique
        scores.append((i, score))

    best_row = max(scores, key=lambda x: x[1])[0]
    return best_row

# --------- File upload and preprocessing ---------
uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    file_type = "csv" if uploaded_file.name.endswith(".csv") else "excel"
    try:
        best_row = detect_header_row(uploaded_file, file_type)
        uploaded_file.seek(0)  # Reset pointer
        if file_type == "csv":
            df = pd.read_csv(uploaded_file, header=best_row)
        else:
            df = pd.read_excel(uploaded_file, header=best_row)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Clean up: remove empty rows and columns
    df.columns = df.columns.str.strip()
    df = df.dropna(axis=1, how="all")
    df = df.dropna(axis=0, how="all")

    # Try parsing dates
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    st.success("✅ File loaded and cleaned!")

    # ---------- KPIs ----------
    st.subheader("📊 Key Metrics")
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Rows", df.shape[0])
    k2.metric("Total Columns", df.shape[1])
    missing_pct = (df.isnull().sum().sum() / df.size) * 100
    k3.metric("Missing Values (%)", f"{missing_pct:.2f}%")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    date_cols = df.select_dtypes(include="datetime").columns.tolist()

    # ---------- Trend ----------
    if date_cols and numeric_cols:
        st.subheader("📈 Trends Over Time")
        date_col = st.selectbox("Select date column", date_cols)
        num_col = st.selectbox("Select numeric column to trend", numeric_cols)

        trend_df = df.groupby(date_col)[num_col].sum().reset_index()
        fig_trend = px.line(trend_df, x=date_col, y=num_col, title=f"Trend of {num_col} over {date_col}", markers=True)
        st.plotly_chart(fig_trend, use_container_width=True)

    # ---------- Bar Chart ----------
    if categorical_cols and numeric_cols:
        st.subheader("📊 Grouped Bar Chart")
        cat_col = st.selectbox("Select categorical column", categorical_cols)
        num_col = st.selectbox("Select numeric column", numeric_cols, key="bar")

        bar_df = df.groupby(cat_col)[num_col].sum().sort_values(ascending=False).reset_index()
        fig_bar = px.bar(bar_df, x=cat_col, y=num_col, color=cat_col, title=f"{num_col} by {cat_col}", text_auto=True)
        st.plotly_chart(fig_bar, use_container_width=True)

    # ---------- Scatter Plot ----------
    if len(numeric_cols) >= 2:
        st.subheader("⚡ Scatter Plot: Compare Metrics")
        x_col = st.selectbox("X-axis", numeric_cols, key="x")
        y_col = st.selectbox("Y-axis", numeric_cols, key="y")
        fig_scatter = px.scatter(df, x=x_col, y=y_col, color=categorical_cols[0] if categorical_cols else None,
                                 title=f"{y_col} vs {x_col}", trendline="ols", size_max=10)
        st.plotly_chart(fig_scatter, use_container_width=True)

    # ---------- Heatmap ----------
    if len(numeric_cols) >= 2:
        st.subheader("🔥 Heatmap of Numeric Correlations")
        corr = df[numeric_cols].corr()
        fig_heatmap = px.imshow(corr, text_auto=True, title="Correlation Heatmap", color_continuous_scale="RdBu_r")
        st.plotly_chart(fig_heatmap, use_container_width=True)

    # ---------- Aggregator ----------
    st.subheader("🧮 Column Aggregator with Group By")

    with st.expander("Aggregate data with group-by logic"):
        group_by_col = st.selectbox("Group by column (categorical)", categorical_cols, key="groupby")

        selected_num_cols = st.multiselect("Numeric columns to aggregate", numeric_cols, key="agg_num_cols")
        agg_func = st.selectbox("Aggregation function for numeric data", ["sum", "count"], key="agg_func")

        selected_cat_cols = st.multiselect("Categorical columns for value counts", categorical_cols, key="agg_cat_cols")

        if st.button("Run Aggregation", key="agg_btn"):
            st.markdown("### 📊 Aggregation Output")

            if group_by_col and selected_num_cols:
                agg_df = df.groupby(group_by_col)[selected_num_cols].agg(agg_func).reset_index()
                st.dataframe(agg_df)

            if selected_cat_cols:
                for col in selected_cat_cols:
                    st.markdown(f"**{col} - Value Counts**")
                    st.dataframe(df[col].value_counts().reset_index().rename(columns={"index": col, col: "Count"}))

    st.caption("All visualizations are dynamic and adapt to your dataset 🎯")

else:
    st.warning("⚠️ Please upload a file to start your analysis.")
