import streamlit as st

st.title("Data Sage Demo")
st.write("Upload your CSV file to generate AI-powered insights!")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    st.write("Data preview:", df.head())
    st.write("Basic statistics:", df.describe())
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Data Sage Enhanced", layout="wide")
st.title("📊 Data Sage Enhanced Demo")
st.write("Upload your CSV file for AI-powered insights and visualizations.")

uploaded_file = st.file_uploader("Upload your CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Data Preview")
    st.dataframe(df.head())

    st.subheader("🧮 Basic Statistics")
    st.dataframe(df.describe())

    st.subheader("📈 Column-wise Analysis")
    col_option = st.selectbox("Choose a column to analyze:", df.columns)

    if df[col_option].dtype in ['int64', 'float64']:
        st.write(f"### Histogram of {col_option}")
        fig, ax = plt.subplots()
        sns.histplot(df[col_option].dropna(), kde=True, ax=ax)
        st.pyplot(fig)
    else:
        st.write(f"### Countplot of {col_option}")
        fig, ax = plt.subplots()
        sns.countplot(y=col_option, data=df, order=df[col_option].value_counts().index, ax=ax)
        st.pyplot(fig)

    st.subheader("💡 Quick AI-Powered Insights")
    st.write("- Top 5 most frequent values in each column:")
    for col in df.columns:
        st.write(f"**{col}**: {df[col].value_counts().head(5).to_dict()}")

    st.write("🔍 *More advanced AI insights can be added!*")

else:
    st.write("⬆️ Upload a CSV to begin!")
