import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import date
from openai import OpenAI
import os

# --------------------
# PAGE SETUP
# --------------------
st.set_page_config(page_title="🌱 Habit Tracker", layout="wide")
st.title("🌱 My Habit Tracker")

TODAY = str(date.today())
DATA_FILE = "habits.csv"

# --------------------
# LOAD / CREATE DATA
# --------------------
if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Habit", "Date"])
    df.to_csv(DATA_FILE, index=False)

# --------------------
# AI QUESTION FUNCTION
# --------------------
def ai_question():
    api_key = st.secrets.get("OPENAI_API_KEY")

    if not api_key:
        return "⚠️ Add your OpenAI API key in Streamlit Secrets"

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Ask one short, friendly daily self-improvement question."
            }
        ]
    )

    return response.choices[0].message.content

# --------------------
# SIDEBAR (AI)
# --------------------
st.sidebar.title("🤖 Daily AI Question")

if st.sidebar.button("Ask AI"):
    st.sidebar.success(ai_question())

# --------------------
# ADD HABIT
# --------------------
st.subheader("➕ Add a Habit")

new_habit = st.text_input("Habit name (example: Gym, Read)")

if st.button("Add Habit"):
    if new_habit.strip() == "":
        st.error("Please type a habit name")
    else:
        st.success(f"Habit '{new_habit}' added!")

# --------------------
# TODAY'S HABITS
# --------------------
st.subheader("✅ Mark Habit as Done Today")

habits = df["Habit"].unique()

if len(habits) == 0:
    st.info("No habits yet. Add one above ☝️")

for habit in habits:
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(habit)

    with col2:
        if st.button("Done", key=f"done_{habit}"):
            new_row = {"Habit": habit, "Date": TODAY}
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.rerun()

# --------------------
# DELETE HABIT
# --------------------
st.subheader("❌ Delete a Habit")

if len(habits) > 0:
    delete_habit = st.selectbox("Choose a habit to delete", habits)

    if st.button("Delete Habit"):
        df = df[df["Habit"] != delete_habit]
        df.to_csv(DATA_FILE, index=False)
        st.warning(f"Habit '{delete_habit}' deleted")
        st.rerun()

# --------------------
# PROGRESS CHART
# --------------------
st.subheader("📊 Progress Chart")

if not df.empty:
    chart_df = df.groupby("Habit").count().reset_index()
    fig = px.bar(
        chart_df,
        x="Habit",
        y="Date",
        title="Habit Completions"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No progress yet!")
