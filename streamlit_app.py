import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import requests

# Display welcome content from Markdown file
def show_welcome():
    try:
        with open("welcome_streamlit.md", "r", encoding="utf-8") as file:
            welcome_content = file.read()
        st.markdown(welcome_content)
    except FileNotFoundError:
        st.warning("Welcome file not found. Please ensure 'welcome_streamlit.md' is in the app directory.")

# Call the function to display welcome section
show_welcome()

st.set_page_config(page_title="Sales Performance Dashboard", layout="wide")
st.title("Sales Performance Dashboard - First Iteration")

# Sidebar for uploading and URL input
st.sidebar.header("Load Data")
uploaded_file = st.sidebar.file_uploader("Upload your CSV file", type=["csv"])
data_url = st.sidebar.text_input("...or enter a public CSV URL")

# Load dataset from file or URL
df = None
if uploaded_file:
    df = pd.read_csv(uploaded_file)
elif data_url:
    try:
        response = requests.get(data_url)
        if response.status_code == 200:
            df = pd.read_csv(io.StringIO(response.text))
        else:
            st.sidebar.error("Unable to fetch data from URL.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# If data is loaded, show exploration and preprocessing options
if df is not None:
    st.subheader("Data Preview")
    st.write(df.head())

    st.subheader("Data Exploration")
    st.write("Shape of data:", df.shape)
    st.write("Data types:")
    st.write(df.dtypes)
    st.write("Summary statistics:")
    st.write(df.describe())

    # Cleaning options
    st.sidebar.header("Data Cleaning Options")
    drop_missing = st.sidebar.checkbox("Drop rows with missing values")
    drop_negative = st.sidebar.checkbox("Remove rows with negative Quantity or UnitPrice")
    drop_canceled = st.sidebar.checkbox("Remove canceled orders (Invoice starts with 'C')")

    cleaned_df = df.copy()
    if drop_missing:
        cleaned_df = cleaned_df.dropna()
    if drop_negative and {'Quantity', 'UnitPrice'}.issubset(cleaned_df.columns):
        cleaned_df = cleaned_df[(cleaned_df['Quantity'] > 0) & (cleaned_df['UnitPrice'] > 0)]
    if drop_canceled and 'InvoiceNo' in cleaned_df.columns:
        cleaned_df = cleaned_df[~cleaned_df['InvoiceNo'].astype(str).str.startswith('C')]

    st.subheader("Cleaned Data Preview")
    st.write(cleaned_df.head())

    # Visualization
    st.subheader("Visualization")
    if {'Description', 'Quantity'}.issubset(cleaned_df.columns):
        top_products = cleaned_df.groupby('Description')['Quantity'].sum().sort_values(ascending=False).head(10)
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=top_products.values, y=top_products.index, ax=ax)
        ax.set_title("Top 10 Products by Quantity Sold")
        st.pyplot(fig)
else:
    st.info("Please upload a CSV file or provide a valid CSV URL to get started.")
