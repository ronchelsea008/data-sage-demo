import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# App config
st.set_page_config(page_title="Data Sage Enhanced", layout="wide")
st.title("🧙 Data Sage: Data Analysis Assistant")

# Upload
uploaded_file = st.file_uploader("Upload your Excel or CSV file", type=["csv", "xlsx"])
if uploaded_file is not None:
    # Read file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.subheader("📄 Raw Data Preview")
    st.dataframe(df.head())

    # Identify numeric & categorical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()

    # Remove typical unique ID columns from categorical analysis
    cat_cols_cleaned = [c for c in cat_cols if not c.lower() in ['id', 'unique_id']]

    # Basic stats
    st.subheader("📊 Basic Summary Statistics")
    st.write(df.describe(include='all').T)

    # Frequency charts for categorical columns
    st.subheader("🔎 Frequency Charts for Categorical Columns")
    for col in cat_cols_cleaned:
        fig, ax = plt.subplots()
        df[col].value_counts().plot(kind='bar', ax=ax, color='skyblue')
        ax.set_title(f"Frequency of {col}")
        ax.set_ylabel("Count")
        st.pyplot(fig)
        st.write(f"💡 **Insight**: Most common value in `{col}` is `{df[col].mode()[0]}`")

    # Trends for numeric columns over date if date column exists
    date_cols = [c for c in df.columns if 'date' in c.lower()]
    if date_cols:
        st.subheader("📈 Trends Over Time")
        date_col = date_cols[0]  # pick first date column
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df = df.dropna(subset=[date_col])
        df_sorted = df.sort_values(by=date_col)

        for col in numeric_cols:
            fig, ax = plt.subplots()
            ax.plot(df_sorted[date_col], df_sorted[col], marker='o', linestyle='-', color='teal')
            ax.set_title(f"{col} over time ({date_col})")
            ax.set_ylabel(col)
            ax.set_xlabel(date_col)
            st.pyplot(fig)
            st.write(f"💡 **Insight**: Trend analysis for `{col}` can highlight seasonality or growth patterns.")

    # Cross-tab analysis
    st.subheader("🔗 Cross-Tab Analysis")
    if len(cat_cols_cleaned) >= 2:
        col1 = st.selectbox("Select first categorical column", cat_cols_cleaned, key="cross1")
        col2 = st.selectbox("Select second categorical column", cat_cols_cleaned, key="cross2")
        pivot = pd.crosstab(df[col1], df[col2], margins=True)
        st.dataframe(pivot)
        st.write("💡 **Insight**: Explore relationships between categories.")

        # 3D Cross-Tab (no duplicate columns error!)
        if len(cat_cols_cleaned) >= 3:
            col3 = st.selectbox("Optional: Select a third column to add to cross tab", cat_cols_cleaned, key="cross3")
            pivot_3d = pd.crosstab([df[col1], df[col3]], df[col2], margins=True)
            pivot_3d_reset = pivot_3d.reset_index()
            pivot_3d_reset = pivot_3d_reset.loc[:, ~pivot_3d_reset.columns.duplicated()]  # remove duplicate columns
            st.dataframe(pivot_3d_reset)
            st.write("💡 **Insight**: Adding a third column reveals more nuanced subgroup patterns.")

    # Correlation heatmap
    st.subheader("🔥 Correlation Heatmap for Numeric Columns")
    if len(numeric_cols) >= 2:
        corr = df[numeric_cols].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
        ax.set_title("Correlation Heatmap")
        st.pyplot(fig)
        st.write("💡 **Insight**: Correlations help detect dependencies among numeric features.")

    st.success("✅ Analysis complete! Explore the insights above.")

else:
    st.info("👆 Upload a file to get started.")
