import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(page_title="Data Sage Enhanced Dashboard", layout="wide")

st.title("🦉 Data Sage: Enhanced Dashboard")
st.write(
    "Upload your CSV or Excel file to generate automatic, interactive insights and KPIs."
)

uploaded_file = st.file_uploader(
    "Upload a CSV or Excel file", type=["csv", "xlsx"]
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # Clean & preprocess
    df = df.dropna(axis=1, how="all")  # drop completely empty columns

    # Attempt to parse any date columns
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass

    st.success("✅ File successfully loaded and preprocessed!")
    st.subheader("📝 Data Preview")
    st.dataframe(df)

    # Dynamic KPIs (example: total rows, unique columns, etc.)
    st.subheader("📊 Key Performance Indicators (KPIs)")
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Total Rows", df.shape[0])
    kpi2.metric("Total Columns", df.shape[1])
    kpi3.metric(
        "Missing Values (%)",
        f"{(df.isnull().sum().sum() / df.size * 100):.2f}%"
    )

    # Additional numeric KPIs if numeric columns exist
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    if numeric_cols:
        kpi4, kpi5 = st.columns(2)
        kpi4.metric("Total Sum", f"{df[numeric_cols].sum().sum():,.2f}")
        kpi5.metric("Mean Value", f"{df[numeric_cols].mean().mean():,.2f}")

    # Trend analysis (by date column if available)
    date_cols = df.select_dtypes(include=["datetime64", "datetime64[ns]"]).columns.tolist()
    if date_cols:
        date_col = st.selectbox("Select date column for time trends", date_cols)
        numeric_col = st.selectbox("Select numeric column to trend", numeric_cols)

        if date_col and numeric_col:
            df_grouped = df.groupby(date_col)[numeric_col].sum().reset_index()
            fig_trend = px.line(
                df_grouped,
                x=date_col,
                y=numeric_col,
                title=f"Trend of {numeric_col} over time",
                markers=True
            )
            st.plotly_chart(fig_trend, use_container_width=True)

    # Dynamic Bar Chart: User-selected categorical vs numeric
    categorical_cols = df.select_dtypes(include="object").columns.tolist()
    if categorical_cols and numeric_cols:
        st.subheader("📊 Interactive Bar Chart")
        cat_col = st.selectbox("Select categorical column", categorical_cols)
        num_col = st.selectbox("Select numeric column for bar chart", numeric_cols)

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

    # Pie chart (optional)
    if categorical_cols:
        st.subheader("🥧 Pie Chart for a Categorical Column")
        pie_col = st.selectbox("Select categorical column for pie chart", categorical_cols)
        pie_data = df[pie_col].value_counts().reset_index()
        pie_data.columns = [pie_col, "count"]
        fig_pie = px.pie(
            pie_data,
            names=pie_col,
            values="count",
            title=f"Distribution of {pie_col}",
            hole=0.4
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.success("✨ Dashboard generated with automatic insights!")
    st.caption(
        "This enhanced analysis avoids static tables and focuses on interactive exploration. "
        "Feel free to export or customize further!"
    )
else:
    st.warning("⚠️ Please upload a file to start your analysis.")
