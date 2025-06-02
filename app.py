import streamlit as st
import pandas as pd
import plotly.express as px

# App configuration
st.set_page_config(page_title="Data Sage Enhanced", layout="wide")
st.title("🚀 Data Sage Enhanced: Interactive Dashboard & Insights")

uploaded_file = st.file_uploader("📁 Upload your CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Load data
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Error reading the file: {e}")
        st.stop()

    st.write("✅ Data preview:")
    st.dataframe(df.head())

    # Identify columns
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    cat_cols = df.select_dtypes(include='object').columns.tolist()
    date_cols = df.select_dtypes(include='datetime').columns.tolist()

    # Fallback for date columns (try to parse manually)
    if not date_cols:
        for col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors='raise')
                date_cols.append(col)
                break
            except:
                continue

    # --- KPIs ---
    st.subheader("📊 Key Performance Indicators (KPIs)")
    if numeric_cols:
        kpi1, kpi2, kpi3 = st.columns(3)
        kpi1.metric(
            label=f"🔢 Total `{numeric_cols[0]}`",
            value=f"{df[numeric_cols[0]].sum():,.0f}"
        )
        kpi2.metric(
            label=f"📈 Average `{numeric_cols[0]}`",
            value=f"{df[numeric_cols[0]].mean():,.2f}"
        )
        kpi3.metric(
            label=f"🚀 Max `{numeric_cols[0]}`",
            value=f"{df[numeric_cols[0]].max():,.0f}"
        )

    if date_cols and numeric_cols:
        date_col = date_cols[0]
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df['Month'] = df[date_col].dt.to_period('M')
        month_summary = df.groupby('Month')[numeric_cols[0]].sum().reset_index()
        top_month = month_summary.iloc[month_summary[numeric_cols[0]].idxmax()]
        st.info(f"🌟 **Best Month:** {top_month['Month']} with total {numeric_cols[0]} of {top_month[numeric_cols[0]]:,.0f}")

    if cat_cols:
        top_cat = df[cat_cols[0]].mode()[0]
        count_top_cat = df[cat_cols[0]].value_counts().iloc[0]
        st.success(f"🏆 **Top Category in `{cat_cols[0]}`:** {top_cat} ({count_top_cat} occurrences)")

    # --- Interactive Charts ---
    st.header("📈 Interactive Data Visualizations")

    # Trend over time
    if date_cols and numeric_cols:
        st.subheader("📅 Trend Over Time")
        trend_chart = px.line(df, x=date_cols[0], y=numeric_cols[0], title=f"{numeric_cols[0]} Over Time")
        st.plotly_chart(trend_chart, use_container_width=True)

    # Category breakdown
    if cat_cols and numeric_cols:
        st.subheader("📊 Category Breakdown")
        cat_chart = px.bar(df, x=cat_cols[0], y=numeric_cols[0], color=cat_cols[0],
                           title=f"{numeric_cols[0]} by {cat_cols[0]}", height=500)
        st.plotly_chart(cat_chart, use_container_width=True)

    # Correlation heatmap
    if len(numeric_cols) > 1:
        st.subheader("🔗 Correlation Heatmap")
        corr = df[numeric_cols].corr()
        corr_chart = px.imshow(corr, text_auto=True, aspect="auto", color_continuous_scale="Viridis")
        st.plotly_chart(corr_chart, use_container_width=True)

    # Pie chart for category distribution
    if cat_cols:
        st.subheader("🥧 Category Distribution")
        pie_chart = px.pie(df, names=cat_cols[0], title=f"Distribution of {cat_cols[0]}")
        st.plotly_chart(pie_chart, use_container_width=True)

    st.write("✅ Analysis complete. Explore the insights interactively above!")

else:
    st.info("⬆️ Upload a file to start the analysis.")
