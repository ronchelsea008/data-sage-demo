import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Data Sage Pro+", layout="wide")
st.title("📊 Data Sage Pro+")
st.write("Upload your CSV for clean analytics, charts, and insights!")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head())

    # Exclude unique ID-like columns from analysis
    nunique_threshold = 0.9 * len(df)
    non_id_columns = [col for col in df.columns if df[col].nunique() < nunique_threshold]

    st.subheader("🧮 Basic Statistics (excluding unique IDs)")
    st.dataframe(df[non_id_columns].describe(include='all'))

    st.subheader("📊 Correlation Heatmap (Numerical Columns)")
    num_cols = df[non_id_columns].select_dtypes(include=['float64', 'int64']).columns
    if len(num_cols) > 1:
        corr = df[num_cols].corr()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
        st.pyplot(fig)
        st.write("💡 **Insight**: Strong correlations (>|0.7|) may indicate potential linear relationships or multicollinearity.")
    else:
        st.write("Not enough numerical columns for correlation heatmap.")

    st.subheader("📊 Frequency Chart")
    cat_cols = [col for col in non_id_columns if df[col].dtype == 'object']
    if cat_cols:
        cat_col = st.selectbox("Select a categorical column for frequency chart:", cat_cols)
        top_n = st.slider("Top N categories", 1, 20, 10)
        freq = df[cat_col].value_counts().head(top_n)
        fig, ax = plt.subplots()
        sns.barplot(x=freq.index, y=freq.values, ax=ax)
        ax.set_title(f"Top {top_n} most frequent {cat_col} values")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
        st.write(f"💡 **Insight**: The most common `{cat_col}` is **{freq.index[0]}** with **{freq.values[0]}** occurrences.")
    else:
        st.write("No categorical columns found for frequency chart.")

    st.subheader("📈 Cross Table / Pivot Analysis")
    if len(cat_cols) >= 2:
        col1 = st.selectbox("Select row column for cross table", cat_cols, key="cross1")
        col2 = st.selectbox("Select column column for cross table", cat_cols, key="cross2")
        pivot_table = pd.crosstab(df[col1], df[col2], margins=True)
        st.dataframe(pivot_table.reset_index())  # fix pyarrow serialization
        st.write("💡 **Insight**: The cross table helps identify joint distributions between the two categorical columns.")

    st.subheader("🧪 Grouped Statistics")
    if cat_cols:
        group_col = st.selectbox("Select a column to group by:", cat_cols, key="group_col")
        numeric_cols = df[non_id_columns].select_dtypes(include=['float64', 'int64']).columns.tolist()
        if numeric_cols:
            group_stats = df.groupby(group_col)[numeric_cols].mean()
            st.dataframe(group_stats)
            st.write(f"💡 **Insight**: Group-level means highlight how `{group_col}` affects numerical columns.")
        else:
            st.write("No numeric columns for grouped statistics.")
    else:
        st.write("No categorical columns for grouped statistics.")

    st.subheader("📊 Additional Cross-Tab Analysis")
    if len(cat_cols) >= 3:
        col3 = st.selectbox("Optional: Select a third column to add to cross tab", cat_cols, key="cross3")
        pivot_3d = pd.crosstab([df[col1], df[col3]], df[col2], margins=True)
        pivot_3d_reset = pivot_3d.reset_index()  # fix pyarrow serialization
        st.dataframe(pivot_3d_reset)
        st.write("💡 **Insight**: Adding a third column reveals more nuanced subgroup patterns.")

    st.subheader("📈 Scatter Plot for Numeric Analysis")
    if len(num_cols) >= 2:
        x_col = st.selectbox("X-axis column", num_cols, key="scatter_x")
        y_col = st.selectbox("Y-axis column", num_cols, key="scatter_y")
        fig, ax = plt.subplots()
        sns.scatterplot(x=x_col, y=y_col, data=df, ax=ax)
        st.pyplot(fig)
        corr_value = df[[x_col, y_col]].corr().iloc[0, 1]
        st.write(f"💡 **Insight**: Correlation between `{x_col}` and `{y_col}`: **{corr_value:.2f}**")

    st.subheader("💡 AI-Powered Summary Insights")
    st.write(f"- Rows: **{df.shape[0]}**, Columns: **{df.shape[1]}**")
    st.write(f"- Most common categorical column: **{df[cat_cols].nunique().idxmin()}**")
    st.write(f"- Missing values (Top 3): {df.isnull().sum().sort_values(ascending=False).head(3).to_dict()}")
    st.write("🔍 *Want even deeper AI-generated summaries? Let me know!*")

else:
    st.write("⬆️ Upload a CSV to begin!")
