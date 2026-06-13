import sqlite3
from datetime import datetime
from pathlib import Path

import streamlit as st

from services.reminder_service import send_reminder

DB_DIR = Path(__file__).resolve().parents[1] / "database"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "tasks.db"

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task TEXT NOT NULL,
        due_at TEXT NOT NULL DEFAULT '',
        reminder_contact TEXT NOT NULL DEFAULT '',
        reminder_type TEXT NOT NULL DEFAULT 'email',
        reminder_sent INTEGER NOT NULL DEFAULT 0
    )
    """
)
conn.commit()

cursor.execute("PRAGMA table_info(tasks)")
columns = {row[1] for row in cursor.fetchall()}
if not {"due_at", "reminder_contact", "reminder_type", "reminder_sent"}.issubset(columns):
    existing_tasks = [row[0] for row in cursor.execute("SELECT task FROM tasks").fetchall()]
    cursor.execute("DROP TABLE tasks")
    cursor.execute(
        """
        CREATE TABLE tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            due_at TEXT NOT NULL DEFAULT '',
            reminder_contact TEXT NOT NULL DEFAULT '',
            reminder_type TEXT NOT NULL DEFAULT 'email',
            reminder_sent INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    for task_text in existing_tasks:
        cursor.execute(
            "INSERT INTO tasks(task, due_at, reminder_contact, reminder_type, reminder_sent) VALUES(?, '', '', 'email', 0)",
            (task_text,),
        )
    conn.commit()

st.markdown(
    """
    <style>
    .planner-shell { padding: 0.6rem 0 1rem; }
    .planner-card {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: #ffffff;
        border: 1px solid #e5e7eb;
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.05);
        margin-bottom: 0.8rem;
    }
    .planner-badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 999px;
        background: #eff6ff;
        color: #1d4ed8;
        font-size: 0.82rem;
        font-weight: 600;
        margin-top: 0.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="planner-shell">', unsafe_allow_html=True)
st.title("📅 Daily Planner")
st.caption("Plan your day, set a deadline, and receive reminders at the right time.")

left_col, right_col = st.columns([2, 1])

with left_col:
    st.subheader("Add a Task")
    with st.form("planner_form"):
        task = st.text_input("Task", placeholder="What do you need to do?")
        deadline_date = st.date_input("Deadline date")
        deadline_time = st.time_input("Deadline time")
        reminder_contact = st.text_input("Reminder email or phone", placeholder="Enter your email or phone number")
        reminder_type = st.selectbox("Reminder type", ["email", "phone"])
        submitted = st.form_submit_button("Add Task")

        if submitted:
            if not task.strip():
                st.warning("Please enter a task.")
            elif not reminder_contact.strip():
                st.warning("Please enter an email or phone number for reminders.")
            else:
                due_at = datetime.combine(deadline_date, deadline_time).strftime("%Y-%m-%d %H:%M")
                cursor.execute(
                    "INSERT INTO tasks(task, due_at, reminder_contact, reminder_type, reminder_sent) VALUES(?,?,?,?,0)",
                    (task.strip(), due_at, reminder_contact.strip(), reminder_type),
                )
                conn.commit()
                st.success("Task added")
                st.rerun()

with right_col:
    st.subheader("Planning Tips")
    st.markdown(
        """
        <div class="planner-card">
            <b>Stay on track</b><br>
            Add clear deadlines, include a contact for reminders, and review overdue tasks quickly.
        </div>
        """,
        unsafe_allow_html=True,
    )

cursor.execute("SELECT id, task, due_at, reminder_contact, reminder_type, reminder_sent FROM tasks ORDER BY due_at ASC")
tasks = cursor.fetchall()

st.subheader("Your Tasks")
if not tasks:
    st.info("No tasks yet. Add one above to get started.")
else:
    for task_id, task_text, due_at, reminder_contact, reminder_type, reminder_sent in tasks:
        now = datetime.now()
        try:
            due_dt = datetime.strptime(due_at, "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            due_dt = None

        status = "Pending"
        if reminder_sent:
            status = "Reminder sent"
        elif due_dt and due_dt <= now:
            status = "Overdue"
        elif due_dt:
            status = "Scheduled"

        if due_dt and due_dt <= now and not reminder_sent:
            reminder_result = send_reminder(task_text, due_at, reminder_contact, reminder_type)
            if reminder_result.get("sent"):
                cursor.execute("UPDATE tasks SET reminder_sent = 1 WHERE id = ?", (task_id,))
                conn.commit()
                st.toast(f"Reminder sent to {reminder_contact}")
            else:
                cursor.execute("UPDATE tasks SET reminder_sent = 1 WHERE id = ?", (task_id,))
                conn.commit()
                st.info(f"Reminder queued for {reminder_contact}")

        st.markdown(
            f"""
            <div class="planner-card">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; gap:0.8rem;">
                    <div>
                        <b>{task_text}</b><br>
                        <span style="color:#6b7280;">Due: {due_at or 'No deadline'} · Contact: {reminder_contact or 'Not provided'} ({reminder_type})</span>
                    </div>
                    <span class="planner-badge">{status}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col1, col2 = st.columns([6, 1])
        with col2:
            if st.button("Remove", key=f"delete-{task_id}"):
                cursor.execute("DELETE FROM tasks WHERE id=?", (task_id,))
                conn.commit()
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)