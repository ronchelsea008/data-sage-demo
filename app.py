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

    # 🧹 CLEANING
    df.columns = df.columns.str.strip()  # remove whitespace from column names
    df = df.dropna(axis=1, how="all")    # remove all-blank columns
    df = df.dropna(axis=0, how="all")    # remove all-blank rows

    # 🔍 Skip metadata/overview rows at the top
    threshold = len(df.columns) * 0.5
    first_valid_row = df.apply(lambda row: row.count(), axis=1).gt(threshold).idxmax()
    df = df.loc[first_valid_row:].reset_index(drop=True)

    # Retry cleaning just in case
    df = df.dropna(axis=0, how="all")
    df.columns = df.columns.str.strip()

    # Attempt to parse date columns
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    st.success("✅ File loaded and cleaned!")

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

    # Column Aggregator with Group By
    st.subheader("🧮 Column Aggregator with Group By")

    with st.expander("Aggregate numerical and categorical columns by group"):
        group_by_col = st.selectbox(
            "Select a column to group by (usually categorical)",
            categorical_cols,
            key="groupby_col"
        )

        st.markdown("### ➕ Numeric Columns to Aggregate")
        selected_num_cols = st.multiselect(
            "Choose numeric columns",
            numeric_cols,
            key="agg_numeric"
        )

        num_agg_func = st.selectbox(
            "Select aggregation function for numeric columns",
            ["sum", "count"],
            key="agg_func_numeric"
        )

        st.markdown("### 🔤 Categorical Columns for Frequency Count")
        selected_cat_cols = st.multiselect(
            "Choose categorical columns to count values (not grouped)",
            categorical_cols,
            key="agg_categorical"
        )

        if st.button("Run Aggregation with Group By", key="run_agg"):
            agg_results = {}

            # Grouped numeric aggregation
            if group_by_col and selected_num_cols:
                grouped_df = (
                    df.groupby(group_by_col)[selected_num_cols]
                    .agg(num_agg_func)
                    .reset_index()
                )
                agg_results["Grouped Numeric Aggregation"] = grouped_df

            # Categorical frequency counts (independent of group-by)
            if selected_cat_cols:
                cat_counts = {}
                for col in selected_cat_cols:
                    cat_counts[col] = df[col].value_counts().to_frame(name="Count")
                agg_results["Categorical Counts"] = cat_counts

            # Show Results
            st.markdown("### 📊 Aggregation Results")
            for label, result in agg_results.items():
                st.write(f"**{label}**")
                if isinstance(result, dict):
                    for col_name, freq_df in result.items():
                        st.write(f"**{col_name}**")
                        st.dataframe(freq_df)
                else:
                    st.dataframe(result)

    st.caption(
        "All visualizations are dynamic and multi-dimensional for a true dashboard experience. Enjoy exploring!"
    )

else:
    st.warning("⚠️ Please upload a file to start your analysis.")
