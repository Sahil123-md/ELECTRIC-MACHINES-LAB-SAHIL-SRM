import math

import numpy as np
import streamlit as st

st.set_page_config(page_title="Electric Machines Virtual Lab", page_icon="EM", layout="wide")

DEFAULT_USERS = {"student1": "eee123", "student2": "eee123"}

if "user_db" not in st.session_state:
    st.session_state.user_db = dict(DEFAULT_USERS)
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "completed" not in st.session_state:
    st.session_state.completed = []
if "quiz_scores" not in st.session_state:
    st.session_state.quiz_scores = []

st.markdown(
    """
<style>
    :root {
        --bg-1: #0b1220;
        --bg-2: #111a2d;
        --panel: #17233a;
        --panel-2: #1f2f4d;
        --text: #e7edf7;
        --muted: #a8b6cf;
        --accent: #4dc3ff;
        --accent-2: #4f8cff;
        --ok: #2dd4bf;
    }

    .stApp {
        background: radial-gradient(1200px 600px at 85% -15%, #1f3358 0%, var(--bg-1) 45%, #080d18 100%);
        color: var(--text);
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111b2f 0%, #0e1729 100%);
        border-right: 1px solid #253550;
    }

    .hero {
        border-radius: 18px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        border: 1px solid #2f4d74;
        background: linear-gradient(135deg, #15233c 0%, #1c3358 55%, #224670 100%);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.28);
    }

    .hero h1 {
        margin: 0;
        font-size: 2rem;
        color: #f5f9ff;
    }

    .hero p {
        margin: 0.45rem 0 0 0;
        color: var(--muted);
        font-size: 1rem;
    }

    [data-testid="stMetric"] {
        background: linear-gradient(160deg, var(--panel) 0%, var(--panel-2) 100%);
        border: 1px solid #314c73;
        border-radius: 14px;
        padding: 10px 12px;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
    }

    .stTabs [data-baseweb="tab"] {
        border: 1px solid #2d4468;
        border-radius: 10px;
        background: #13203a;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #1c3a63 0%, #26528c 100%) !important;
        color: #f7fbff !important;
        border-color: #4b7ebb !important;
    }

    .stButton > button {
        border-radius: 10px;
        border: 1px solid #3970a8;
        background: linear-gradient(135deg, var(--accent-2) 0%, #3f7fd1 100%);
        color: #ffffff;
        font-weight: 600;
    }

    .stButton > button:hover {
        border-color: #6cb4e8;
        background: linear-gradient(135deg, #5aa1e8 0%, #4f8cff 100%);
    }

    .stMarkdown p,
    .stCaption {
        color: var(--text);
    }

    .stAlert {
        border-radius: 12px;
    }
</style>
""",
    unsafe_allow_html=True,
)


def mark_complete(name: str) -> None:
    if name not in st.session_state.completed:
        st.session_state.completed.append(name)


def auth_panel(prefix: str) -> None:
    if prefix == "dashboard":
        if st.button("Login as Demo User"):
            st.session_state.current_user = "student1"
            st.rerun()

    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        with st.form(f"{prefix}_login"):
            u = st.text_input("Username", key=f"{prefix}_u")
            p = st.text_input("Password", type="password", key=f"{prefix}_p")
            submit = st.form_submit_button("Login")
        if submit:
            if u in st.session_state.user_db and st.session_state.user_db[u] == p:
                st.session_state.current_user = u
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with t2:
        with st.form(f"{prefix}_register"):
            u = st.text_input("New username", key=f"{prefix}_new_u")
            p = st.text_input("New password", type="password", key=f"{prefix}_new_p")
            submit = st.form_submit_button("Create Account")
        if submit:
            if not u.strip() or not p.strip():
                st.error("Username and password are required.")
            elif u in st.session_state.user_db:
                st.error("Username already exists.")
            else:
                st.session_state.user_db[u.strip()] = p.strip()
                st.success("Account created. Login now.")


LABS = {
    "DC Shunt Motor Speed Control": {
        "aim": "Study armature-voltage and field-flux effect on speed.",
        "components": [
            {"Component": "DC shunt motor", "Spec": "220 V", "Qty": 1},
            {"Component": "DC supply", "Spec": "0-240 V", "Qty": 1},
            {"Component": "Field rheostat", "Spec": "Variable", "Qty": 1},
            {"Component": "Ammeter/voltmeter", "Spec": "DC", "Qty": 2},
            {"Component": "Tachometer", "Spec": "Digital", "Qty": 1},
        ],
        "wiring": [
            "Connect armature through starter to DC source.",
            "Connect shunt field with rheostat in series.",
            "Measure V, Ia, and speed at each load point.",
        ],
    },
    "Transformer OC and SC Test": {
        "aim": "Estimate losses and efficiency using OC/SC tests.",
        "components": [
            {"Component": "Single-phase transformer", "Spec": "1-5 kVA", "Qty": 1},
            {"Component": "Variac", "Spec": "0-270 V", "Qty": 1},
            {"Component": "Wattmeter", "Spec": "AC", "Qty": 2},
            {"Component": "Ammeter/voltmeter", "Spec": "AC", "Qty": 2},
            {"Component": "Shorting link", "Spec": "LV side", "Qty": 1},
        ],
        "wiring": [
            "OC test: keep HV open and energize LV.",
            "SC test: short LV and energize HV at reduced voltage.",
            "Record P_oc and P_cu values.",
        ],
    },
    "Induction Motor Slip-Torque": {
        "aim": "Relate rotor speed, slip, and torque behavior.",
        "components": [
            {"Component": "3-phase induction motor", "Spec": "415 V", "Qty": 1},
            {"Component": "3-phase source", "Spec": "Lab supply", "Qty": 1},
            {"Component": "Tachometer", "Spec": "RPM", "Qty": 1},
            {"Component": "Clamp meter", "Spec": "AC current", "Qty": 1},
            {"Component": "Brake load", "Spec": "Dynamometer", "Qty": 1},
        ],
        "wiring": [
            "Connect motor to 3-phase source with protection.",
            "Set brake load and measure speed per load step.",
            "Compute slip from synchronous speed.",
        ],
    },
}

st.markdown(
    """
<div class="hero">
    <h1>Electric Machines Virtual Lab</h1>
    <p>Practical EEE environment for DC machines, transformers, and induction motor studies.</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Student Access")
    if st.session_state.current_user:
        st.success(f"Logged in as: {st.session_state.current_user}")
        if st.button("Logout"):
            st.session_state.current_user = None
            st.rerun()
    else:
        st.caption("Demo login: student1 / eee123")
        auth_panel("sidebar")

    st.markdown("---")
    section = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Aim and Theory",
            "Virtual Labs",
            "Calculators",
            "Instruments",
            "Quiz",
            "Feedback",
        ],
    )

if section == "Dashboard":
    st.subheader("Student Dashboard")
    if not st.session_state.current_user:
        st.warning("Login to track progress.")
        auth_panel("dashboard")
    else:
        avg = (
            sum(st.session_state.quiz_scores) / len(st.session_state.quiz_scores)
            if st.session_state.quiz_scores
            else 0.0
        )
        c1, c2, c3 = st.columns(3)
        c1.metric("Completed modules", len(st.session_state.completed))
        c2.metric("Quiz attempts", len(st.session_state.quiz_scores))
        c3.metric("Average quiz score", f"{avg:.2f}/3")
        for item in st.session_state.completed:
            st.write(f"- {item}")

if section == "Aim and Theory":
    st.subheader("Aim")
    st.write("Understand operation and testing of electric machines using guided practical workflows.")
    st.subheader("Core Equations")
    c1, c2 = st.columns(2)
    with c1:
        st.latex(r"N_s=\frac{120f}{P}")
        st.latex(r"s=\frac{N_s-N_r}{N_s}")
    with c2:
        st.latex(r"E_b=V-I_aR_a")
        st.latex(r"\eta=\frac{P_{out}}{P_{out}+P_{loss}}\times100")

if section == "Virtual Labs":
    st.subheader("Proper Virtual Labs with Components")
    lab_name = st.selectbox("Select lab", list(LABS.keys()))
    lab = LABS[lab_name]
    t1, t2, t3, t4 = st.tabs(["Overview", "Components", "Wiring", "Observation"])
    with t1:
        st.write(lab["aim"])
    with t2:
        st.table(lab["components"])
    with t3:
        for i, step in enumerate(lab["wiring"], start=1):
            st.write(f"{i}. {step}")
    with t4:
        key = f"obs_{lab_name}"
        if key not in st.session_state:
            st.session_state[key] = [
                {"Trial": 1, "Reading 1": "", "Reading 2": "", "Remark": ""},
                {"Trial": 2, "Reading 1": "", "Reading 2": "", "Remark": ""},
            ]
        st.session_state[key] = st.data_editor(
            st.session_state[key], num_rows="dynamic", use_container_width=True
        )
        if st.button("Mark Lab Complete"):
            mark_complete(f"Virtual Lab - {lab_name}")
            st.success("Marked complete.")

if section == "Calculators":
    st.subheader("Machine Calculators")
    mode = st.selectbox(
        "Choose calculator",
        [
            "Synchronous Speed and Slip",
            "Transformer Efficiency",
            "DC Motor Speed Estimate",
        ],
    )
    if mode == "Synchronous Speed and Slip":
        f = st.number_input("Frequency (Hz)", min_value=1.0, value=50.0)
        poles = st.selectbox("Poles", [2, 4, 6, 8], index=1)
        nr = st.number_input("Rotor speed (rpm)", min_value=1.0, value=1440.0)
        ns = 120 * f / poles
        slip = (ns - nr) / ns if ns > 0 else 0
        st.metric("Ns", f"{ns:.2f} rpm")
        st.metric("Slip", f"{max(slip,0):.5f}")
    if mode == "Transformer Efficiency":
        pout = st.number_input("Output power (W)", min_value=1.0, value=5000.0)
        pcore = st.number_input("Core loss (W)", min_value=0.0, value=180.0)
        pcu = st.number_input("Copper loss (W)", min_value=0.0, value=320.0)
        eff = 100 * pout / (pout + pcore + pcu)
        st.metric("Efficiency", f"{eff:.3f} %")
    if mode == "DC Motor Speed Estimate":
        v = st.number_input("V (V)", min_value=1.0, value=220.0)
        ia = st.number_input("Ia (A)", min_value=0.0, value=8.0)
        ra = st.number_input("Ra (ohm)", min_value=0.01, value=1.2)
        base_speed = st.number_input("Base speed (rpm)", min_value=100.0, value=1500.0)
        flux_ratio = st.slider("Flux ratio", min_value=0.5, max_value=1.2, value=1.0)
        eb = v - ia * ra
        speed = base_speed * (eb / v) / flux_ratio if v > 0 else 0
        st.metric("Back EMF", f"{eb:.2f} V")
        st.metric("Estimated speed", f"{speed:.1f} rpm")
    if st.button("Mark Calculator Complete"):
        mark_complete(mode)
        st.success("Saved.")

if section == "Instruments":
    st.subheader("Virtual Instruments")
    inst = st.selectbox("Instrument", ["Tachometer", "Insulation Tester", "Power Analyzer"])
    if inst == "Tachometer":
        true_speed = st.number_input("True speed (rpm)", min_value=0.0, value=1450.0)
        tol = st.slider("Tolerance (%)", 0.0, 5.0, 1.0)
        if st.button("Take Reading"):
            measured = true_speed * (1 + np.random.normal(0, tol / 100))
            st.metric("Measured speed", f"{measured:.1f} rpm")
    if inst == "Insulation Tester":
        r = st.number_input("Insulation resistance true (MOhm)", min_value=0.01, value=25.0)
        if st.button("Test"):
            measured = max(r * (1 + np.random.normal(0, 0.05)), 0.01)
            st.metric("Insulation resistance", f"{measured:.2f} MOhm")
    if inst == "Power Analyzer":
        v = st.number_input("Line voltage (V)", min_value=1.0, value=415.0)
        i = st.number_input("Line current (A)", min_value=0.1, value=12.0)
        pf = st.slider("PF", min_value=0.1, max_value=1.0, value=0.85)
        p = math.sqrt(3) * v * i * pf / 1000
        st.metric("Real Power", f"{p:.3f} kW")
    if st.button("Mark Instrument Complete"):
        mark_complete(inst)
        st.success("Saved.")

if section == "Quiz":
    st.subheader("Quiz")
    q1 = st.radio("Synchronous speed formula?", ["Ns=120f/P", "Ns=f/120P", "Ns=60P/f"], index=None)
    q2 = st.radio("Back EMF in DC motor?", ["Eb=V-IaRa", "Eb=Ia/V", "Eb=V+IaRa"], index=None)
    q3 = st.radio("OC test gives mainly?", ["Core loss", "Copper loss", "Starting torque"], index=None)
    if st.button("Submit Quiz"):
        score = 0
        if q1 == "Ns=120f/P":
            score += 1
        if q2 == "Eb=V-IaRa":
            score += 1
        if q3 == "Core loss":
            score += 1
        st.session_state.quiz_scores.append(score)
        mark_complete("Quiz")
        st.success(f"Score: {score}/3")

if section == "Feedback":
    st.subheader("Feedback")
    with st.form("fb_form"):
        rating = st.slider("Rate this lab", 1, 5, 4)
        comments = st.text_area("Suggestions")
        submit = st.form_submit_button("Submit")
    if submit:
        st.success(f"Thanks. Rating received: {rating}/5")
        if comments.strip():
            st.write("Comment:", comments.strip())
