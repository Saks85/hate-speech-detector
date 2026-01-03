import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt


API_BASE = "http://127.0.0.1:8000/api/v1/dashboard"


st.set_page_config(page_title="Hate Speech Moderation Dashboard")

st.title("🛡 Hate Speech Detection – Moderator Dashboard")


@st.cache_data
def fetch_stats():
    r = requests.get(f"{API_BASE}/stats")
    return r.json()


@st.cache_data
def fetch_feedback():
    r = requests.get(f"{API_BASE}/list")
    return pd.DataFrame(r.json())


stats = fetch_stats()


st.subheader("📊 System Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Total Feedback Items", stats["total_feedback"])
col2.metric("Model Errors", stats["model_errors"])
col3.metric("Overrides Applied", stats["overrides"])



st.subheader("📝 Recent Feedback")

df = fetch_feedback()

st.dataframe(df, use_container_width=True)


st.subheader("📈 Label Review Chart")

label_counts = df["correct_label"].value_counts()

fig, ax = plt.subplots()
ax.bar(label_counts.index, label_counts.values)
st.pyplot(fig)
