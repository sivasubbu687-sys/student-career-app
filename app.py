import streamlit as st
import sqlite3
import pandas as pd
import datetime
from PyPDF2 import PdfReader
import random
import plotly.graph_objects as go

# ================= GLOBAL STYLE =================

st.markdown("""
<style>
.stApp{
background: linear-gradient(-45deg,#0f172a,#1e293b,#334155,#0f172a);
background-size:400% 400%;
animation:bgmove 12s ease infinite;
color:white;
}

.card{
padding:25px;
border-radius:18px;
text-align:center;
color:white;
box-shadow:0 10px 25px rgba(0,0,0,0.4);
}

.card1{background:linear-gradient(135deg,#6366f1,#4f46e5);}
.card2{background:linear-gradient(135deg,#22c55e,#16a34a);}
.card3{background:linear-gradient(135deg,#f59e0b,#ea580c);}

.counter{
font-size:40px;
font-weight:bold;
}
</style>
""",unsafe_allow_html=True)

# ================= DATABASE =================

conn = sqlite3.connect("student.db",check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS attendance(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
date TEXT,
subject TEXT,
period INTEGER,
status INTEGER,
UNIQUE(user_id,date,subject,period)
)
""")

conn.commit()

# ================= SESSION =================

if "logged_in" not in st.session_state:
    st.session_state.logged_in=False

if "username" not in st.session_state:
    st.session_state.username=""

if "user_id" not in st.session_state:
    st.session_state.user_id=None

# ================= LOGIN =================

if not st.session_state.logged_in:

    st.title("🎓 Student Career Intelligence System")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        if password=="1234":

            cursor.execute(
            "INSERT OR IGNORE INTO users(username,password) VALUES(?,?)",
            (username,"1234"))

            conn.commit()

            cursor.execute(
            "SELECT id FROM users WHERE username=?",
            (username,))

            user=cursor.fetchone()

            st.session_state.logged_in=True
            st.session_state.username=username
            st.session_state.user_id=user[0]

            st.success("Login Successful")
            st.rerun()

        else:
            st.error("Password must be 1234")

    st.stop()

# ================= SIDEBAR =================

st.sidebar.title("📚 Menu")

menu = st.sidebar.selectbox(
"Menu",
[
"Dashboard",
"Attendance",
"Resume Analyzer",
"Skill Advisor",
"Career Roadmap",
"Placement Analyzer",
"Study Planner",
"Guidance"
]
)

if st.sidebar.button("Logout"):
    st.session_state.logged_in=False
    st.rerun()

# ================= DASHBOARD =================

if menu=="Dashboard":

    st.title(f"Welcome {st.session_state.username}")

    days = st.slider("Show attendance for last N days",1,90,10)

    df = pd.read_sql_query("""
    SELECT date,subject,status FROM attendance
    WHERE user_id=?
    AND date >= date('now',?)
    """,conn,params=(st.session_state.user_id,f'-{days} day'))

    if not df.empty:
        total=len(df)
        present=df["status"].sum()
        attendance=(present/total)*100
    else:
        total=0
        present=0
        attendance=0

    c1,c2,c3 = st.columns(3)

    c1.markdown(
    f"<div class='card card1'><h3>Total Classes</h3><div class='counter'>{total}</div></div>",
    unsafe_allow_html=True)

    c2.markdown(
    f"<div class='card card2'><h3>Present</h3><div class='counter'>{present}</div></div>",
    unsafe_allow_html=True)

    c3.markdown(
    f"<div class='card card3'><h3>Attendance %</h3><div class='counter'>{attendance:.2f}</div></div>",
    unsafe_allow_html=True)

    gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=attendance,
    title={'text':f"Attendance (Last {days} Days)"},
    gauge={'axis':{'range':[0,100]}}
    ))

    st.plotly_chart(gauge,width="stretch")

# ================= ATTENDANCE =================

if menu=="Attendance":

    st.header("📘 Period Wise Attendance")

    date = st.date_input("Date",datetime.date.today())
    subject = st.text_input("Subject")

    periods = st.number_input("Total Periods",1,6,1)

    for i in range(1,periods+1):

        status = st.selectbox(f"Period {i}",["Present","Absent"],key=f"p{i}")

        if st.button(f"Save {i}",key=f"s{i}"):

            value = 1 if status=="Present" else 0

            try:
                cursor.execute("""
                INSERT INTO attendance(user_id,date,subject,period,status)
                VALUES(?,?,?,?,?)
                """,(st.session_state.user_id,str(date),subject,i,value))

                conn.commit()
                st.success("Saved")

            except:
                st.warning("Already marked")

# ================= RESUME ANALYZER =================

if menu=="Resume Analyzer":

    st.header("📄 Resume Analyzer")

    file = st.file_uploader("Upload Resume",type=["pdf"])

    if file:

        reader = PdfReader(file)
        text=""

        for page in reader.pages:
            data = page.extract_text()
            if data:
                text += data.lower()

        score=0

        if "education" in text: score+=20
        if "skills" in text: score+=20
        if "project" in text: score+=20
        if "experience" in text: score+=20
        if "github" in text: score+=20

        st.progress(score)
        st.write("Resume Score:",score,"/100")

# ================= SKILL ADVISOR =================

if menu=="Skill Advisor":

    st.header("🎯 Skill Advisor")

    role = st.selectbox(
    "Target Role",
    ["Software Engineer","Data Scientist","Cyber Security"]
    )

    user_input = st.text_input("Enter Skills (comma separated)")

    if user_input:

        user=[s.strip().lower() for s in user_input.split(",")]

        req={
        "Software Engineer":["dsa","system design","sql","cloud","java","python"],
        "Data Scientist":["python","machine learning","statistics","pandas"],
        "Cyber Security":["linux","networking","security"]
        }

        need=req[role]

        st.subheader("Missing Skills")

        for s in need:
            if s not in user:
                st.warning(s)

# ================= CAREER ROADMAP =================

if menu=="Career Roadmap":

    st.header("🛣 Career Roadmap")

    role = st.selectbox(
    "Role",
    ["Software Engineer","Data Scientist","Cyber Security"]
    )

    if role=="Software Engineer":
        st.write("Learn Programming → DSA → Databases → Projects → System Design")

    elif role=="Data Scientist":
        st.write("Python → Statistics → Data Analysis → Machine Learning → Projects")

    elif role=="Cyber Security":
        st.write("Linux → Networking → Security Concepts → Ethical Hacking")

# ================= PLACEMENT ANALYZER =================

if menu=="Placement Analyzer":

    st.header("🏢 Placement Analyzer")

    cgpa = st.slider("CGPA",0.0,10.0,7.5)
    skills = st.slider("Skill Level",0,100,70)
    internships = st.slider("Internships",0,5,1)
    projects = st.slider("Projects",0,10,2)

    score = (cgpa/10*100*0.4)+(skills*0.3)+(internships*20*0.2)+(projects*10*0.1)

    st.progress(int(score))
    st.write("Placement Score:",round(score,2))

    st.subheader("Recommended Companies")

    if score >= 85:
        companies=["Google","Amazon","Microsoft","Adobe","Atlassian"]

    elif score >= 75:
        companies=["Oracle","Cisco","IBM","SAP"]

    elif score >= 65:
        companies=["Accenture","Capgemini","Infosys","TCS"]

    elif score >= 50:
        companies=["Tech Mahindra","HCL"]

    else:
        companies=["Improve skills to target better companies"]

    for c in companies:
        st.write("✔",c)

# ================= STUDY PLANNER =================

if menu=="Study Planner":

    st.header("📅 Weekly Study Planner")

    days=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

    for d in days:
        st.text_input(f"{d} Plan")

# ================= GUIDANCE =================

if menu=="Guidance":

    st.header("📚 Study Guidance")

    st.write("https://leetcode.com")
    st.write("https://codechef.com")
    st.write("https://hackerrank.com")

    tips=[
    "Solve 2 problems daily",
    "Build projects",
    "Revise fundamentals weekly"
    ]

    st.info(random.choice(tips))