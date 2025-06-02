import streamlit as st

st.title("Data Sage Demo")
st.write("Upload your CSV file to generate AI-powered insights!")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    import pandas as pd
    df = pd.read_csv(uploaded_file)
    st.write("Data preview:", df.head())
    st.write("Basic statistics:", df.describe())
