import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
import openai
import os

# --------------------
# PAGE SETUP
# --------------------
st.set_page_config(page_title="🌱 Habit Tracker", layout="wide")
st.title("🌱 My Habit Tracker")

TODAY = str(date.today())
DATA_FILE = "habits.csv"

# --------------------
# LOAD DATA
# --------------------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Habit", "Date"])
    df.to_csv(DATA_FILE, index=False)

# --------------------
# SIDEBAR (AI)
# --------------------
st.sidebar.title("🤖 Daily Question")

openai.api_key = st.secrets.get("OPENAI_API_KEY", "")

def ai_question():
    if not openai.api_key:
        return "Add your OpenAI key to get AI questions!"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ask one short daily self-improvement question."}
        ]
    )
    return response.choices[0].message.content

if st.sidebar.button("Ask AI"):
    st.sidebar.success(ai_question())

# --------------------
# ADD HABIT
# --------------------
st.subheader("➕ Add a Habit")

new_habit = st.text_input("Habit name (ex: Gym, Read)")

if st.button("Add Habit"):
    if new_habit.strip() != "":
        st.success("Habit added!")
    else:
        st.error("Type something first")

# --------------------
# TODAY'S HABITS
# --------------------
st.subheader("✅ Today")

habits = df["Habit"].unique()

for habit in habits:
    col1, col2 = st.columns([3,1])

    with col1:
        st.write(habit)

    with col2:
        if st.button("Done", key=f"{habit}_done"):
            new_row = {"Habit": habit, "Date": TODAY}
            df = pd.concat([df, pd.DataFrame([new_row])])
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --------------------
# DELETE HABIT
# --------------------
st.subheader("❌ Delete a Habit")

delete_habit = st.selectbox("Choose habit", habits)

if st.button("Delete"):
    df = df[df["Habit"] != delete_habit]
    df.to_csv(DATA_FILE, index=False)
    st.warning("Habit deleted")
    st.rerun()

# --------------------
# CHART
# --------------------
st.subheader("📊 Progress")

if not df.empty:
    chart_df = df.groupby("Habit").count().reset_index()
    fig = px.bar(chart_df, x="Habit", y="Date", title="Habit Completions")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No data yet!")
