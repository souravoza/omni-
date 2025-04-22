
import streamlit as st
import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

# Page setup
st.set_page_config(page_title="OmniVillage Enhanced Dashboard", layout="wide")
st.title("📊 OmniVillage Full Data Visual Dashboard")

# Load JSON
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return pd.DataFrame(json.load(f))

# Clean column names
def clean_dataframe(df):
    df.columns = [str(col).strip().replace("\n", "").replace("\r", "").replace("_", " ").title() for col in df.columns]
    return df

# Export buttons
def download_buttons(df, name):
    csv = df.to_csv(index=False).encode("utf-8")
    excel = BytesIO()
    with pd.ExcelWriter(excel, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    st.download_button("📥 Download CSV", csv, f"{name}.csv", "text/csv")
    st.download_button("📥 Download Excel", excel.getvalue(), f"{name}.xlsx",
                       "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# Metrics display
def show_stats(df):
    st.markdown("### 📌 Dataset Stats")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Rows", df.shape[0])
    col2.metric("Total Columns", df.shape[1])
    col3.metric("Missing Values", df.isnull().sum().sum())

# Plot categorical columns
def plot_categorical(df):
    st.markdown("### 📊 Categorical Column Visuals")
    cat_cols = [col for col in df.columns if df[col].apply(lambda x: isinstance(x, (str, int, float, bool, type(None)))).all() and df[col].nunique() <= 25]
    if not cat_cols:
        st.info("No categorical columns suitable for bar chart.")
        return
    for col in cat_cols:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.countplot(data=df, x=col, order=df[col].value_counts().index, palette='pastel', ax=ax)
        ax.set_title(f"Distribution of '{col}'", fontsize=14)
        ax.set_xlabel(col, fontsize=12)
        ax.set_ylabel("Count", fontsize=12)
        ax.tick_params(axis='x', rotation=45)
        for container in ax.containers:
            ax.bar_label(container, fontsize=9, padding=2)
        st.pyplot(fig)

# Plot numeric columns
def plot_numeric(df):
    st.markdown("### 📈 Numeric Column Visuals")
    num_cols = df.select_dtypes(include=["int64", "float64"]).columns
    if len(num_cols) == 0:
        st.info("No numeric columns available for histogram.")
        return
    for col in num_cols:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.histplot(df[col].dropna(), kde=True, color='skyblue', ax=ax)
        ax.set_title(f"Histogram of '{col}'", fontsize=14)
        ax.set_xlabel(col, fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        st.pyplot(fig)

# Set up file reading
data_dir = os.path.dirname(os.path.abspath(__file__))
json_files = sorted([f for f in os.listdir(data_dir) if f.endswith(".json")])

selected_file = st.sidebar.selectbox("📁 Select Dataset", json_files)
file_path = os.path.join(data_dir, selected_file)

# Load and clean
df = load_json(file_path)
df = clean_dataframe(df)

# Show stats
show_stats(df)

# Data preview
st.subheader("📋 Data Preview")
st.dataframe(df.head(100), use_container_width=True)
download_buttons(df, selected_file.replace(".json", ""))

# Visualizations
plot_categorical(df)
plot_numeric(df)
