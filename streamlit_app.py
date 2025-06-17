import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# Set Streamlit page configuration
st.set_page_config(page_title="Universal Data Cleaning & Exploration App", layout="wide")

# Title
st.title("Universal Data Cleaning & Exploration App")
st.write("""
This interactive application allows you to:
- Upload any CSV dataset.
- Explore raw data.
- Apply flexible data cleaning operations.
- Visualize cleaned data.
- Export cleaned dataset.
""")

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("Raw Data Preview")
    st.dataframe(df.head())
    
    # Data Cleaning Section
    st.header("Data Cleaning")
    
    # Handling missing values
    st.subheader("Handle Missing Values")
    missing_option = st.selectbox("Choose method for handling missing values:", 
                                  ["None", "Drop rows with missing values", "Fill with mean (numerical only)", "Fill with mode"])
    
    if missing_option == "Drop rows with missing values":
        df = df.dropna()
    elif missing_option == "Fill with mean (numerical only)":
        df = df.fillna(df.mean(numeric_only=True))
    elif missing_option == "Fill with mode":
        for col in df.columns:
            df[col].fillna(df[col].mode()[0], inplace=True)

    # Handle duplicate rows
    st.subheader("Handle Duplicates")
    if st.checkbox("Remove duplicate rows"):
        df = df.drop_duplicates()
    
    # Convert data types
    st.subheader("Convert Columns")
    columns_to_convert = st.multiselect("Select columns to convert to numeric (if applicable):", df.columns)
    for col in columns_to_convert:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Show cleaned data
    st.subheader("Cleaned Data Preview")
    st.dataframe(df.head())

    # Export cleaned data
    cleaned_csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Cleaned Data", cleaned_csv, "cleaned_data.csv", "text/csv")

    # Data Exploration Section
    st.header("Data Exploration")
    st.write("You can explore descriptive statistics below:")
    st.dataframe(df.describe(include='all'))

    # Data Visualization Section
    st.header("Data Visualization")

    # Select plot type
    plot_type = st.selectbox("Choose plot type", ["Histogram", "Scatter Plot", "Boxplot", "Correlation Heatmap"])

    if plot_type == "Histogram":
        column = st.selectbox("Select column for histogram", df.select_dtypes(include=np.number).columns)
        plt.figure(figsize=(8, 4))
        sns.histplot(df[column], kde=True)
        st.pyplot(plt)

    elif plot_type == "Scatter Plot":
        columns = df.select_dtypes(include=np.number).columns
        x_axis = st.selectbox("Select X-axis", columns)
        y_axis = st.selectbox("Select Y-axis", columns)
        plt.figure(figsize=(8, 4))
        sns.scatterplot(x=df[x_axis], y=df[y_axis])
        st.pyplot(plt)

    elif plot_type == "Boxplot":
        column = st.selectbox("Select column for boxplot", df.select_dtypes(include=np.number).columns)
        plt.figure(figsize=(8, 4))
        sns.boxplot(x=df[column])
        st.pyplot(plt)

    elif plot_type == "Correlation Heatmap":
        plt.figure(figsize=(10, 8))
        sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm')
        st.pyplot(plt)

else:
    st.warning("Please upload a CSV file to get started.")
