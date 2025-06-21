# Refactored streamlit_app.py with modular classes

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# System Entities (Classes)
# -------------------------------

class SalesData:
    def __init__(self, file):
        self.df = pd.read_csv(file)

    def preview_raw(self):
        return self.df.head()

    def convert_columns(self, columns):
        for col in columns:
            self.df[col] = pd.to_numeric(self.df[col], errors='coerce')


class DataCleaner:
    def __init__(self, df):
        self.df = df

    def handle_missing(self, method):
        if method == "Drop rows with missing values":
            return self.df.dropna()
        elif method == "Fill with mean (numerical only)":
            return self.df.fillna(self.df.mean(numeric_only=True))
        elif method == "Fill with mode":
            for col in self.df.columns:
                self.df[col].fillna(self.df[col].mode()[0], inplace=True)
            return self.df
        return self.df

    def remove_duplicates(self):
        return self.df.drop_duplicates()


class Analyzer:
    @staticmethod
    def generate_summary(df):
        return df.describe(include='all')


class Visualizer:
    @staticmethod
    def plot(df, plot_type, x=None, y=None):
        plt.figure(figsize=(8, 4))
        if plot_type == "Histogram":
            sns.histplot(df[x], kde=True)
        elif plot_type == "Scatter Plot":
            sns.scatterplot(x=df[x], y=df[y])
        elif plot_type == "Boxplot":
            sns.boxplot(x=df[x])
        elif plot_type == "Correlation Heatmap":
            plt.figure(figsize=(10, 8))
            sns.heatmap(df.corr(numeric_only=True), annot=True, cmap='coolwarm')
        st.pyplot(plt)


class Exporter:
    @staticmethod
    def export_file(df):
        return df.to_csv(index=False).encode('utf-8')


# -------------------------------
# Streamlit Interface
# -------------------------------

st.set_page_config(page_title="Universal Data Cleaning & Exploration App", layout="wide")
st.title("Universal Data Cleaning & Exploration App")
st.write("""
This interactive application allows you to:
- Upload any CSV dataset.
- Explore raw data.
- Apply flexible data cleaning operations.
- Visualize cleaned data.
- Export cleaned dataset.
""")

uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

if uploaded_file:
    data = SalesData(uploaded_file)
    st.subheader("Raw Data Preview")
    st.dataframe(data.preview_raw())

    st.header("Data Cleaning")
    cleaner = DataCleaner(data.df)

    missing_option = st.selectbox("Choose method for handling missing values:",
                                   ["None", "Drop rows with missing values", "Fill with mean (numerical only)", "Fill with mode"])
    data.df = cleaner.handle_missing(missing_option)

    if st.checkbox("Remove duplicate rows"):
        data.df = cleaner.remove_duplicates()

    columns_to_convert = st.multiselect("Select columns to convert to numeric (if applicable):", data.df.columns)
    data.convert_columns(columns_to_convert)

    st.subheader("Cleaned Data Preview")
    st.dataframe(data.df.head())

    cleaned_csv = Exporter.export_file(data.df)
    st.download_button("Download Cleaned Data", cleaned_csv, "cleaned_data.csv", "text/csv")

    st.header("Data Exploration")
    st.dataframe(Analyzer.generate_summary(data.df))

    st.header("Data Visualization")
    plot_type = st.selectbox("Choose plot type", ["Histogram", "Scatter Plot", "Boxplot", "Correlation Heatmap"])

    numeric_columns = data.df.select_dtypes(include=np.number).columns
    x = y = None

    if plot_type in ["Histogram", "Boxplot"]:
        x = st.selectbox("Select column", numeric_columns)
    elif plot_type == "Scatter Plot":
        x = st.selectbox("X-axis", numeric_columns)
        y = st.selectbox("Y-axis", numeric_columns)

    Visualizer.plot(data.df, plot_type, x, y)

else:
    st.warning("Please upload a CSV file to get started.")
