# app.py — PLAIN / FAST VERSION (SQLite only) + 2 PASSWORDS
# 1) App Access Password
# 2) Admin Password (Admin Dashboard + Admin Editor)

import sqlite3
import base64
import html
import numbers
import os
import time
from pathlib import Path
import altair as alt
import pandas as pd
import streamlit as st
from datetime import date, datetime

from auth_session import clear_authentication, expire_inactive_session, require_admin
from export_safety import safe_csv_bytes
from report import build_excel_report, REPORT_FILENAME
from finance_rules import nonnegative_amount, positive_amount, redeemed_total
from security import integer_setting, required_password_hash, verify_password

# =========================
# CONFIG
# =========================
PROJECT_DIR = Path(__file__).resolve().parent
_configured_db_path = os.environ.get("SJMCC_DB_PATH", "sjmcc_harvest_sqlite/sjmcc_2026_harvest.db")
DB_PATH = str(Path(_configured_db_path) if Path(_configured_db_path).is_absolute() else PROJECT_DIR / _configured_db_path)

HARVEST_ACTIVITIES = [
    "Theme Selection",
    "Unveiling of Banner",
    "Seed Sowing",
    "Jesus’ Family",
    "Mary’s Family",
    "Joseph’s Family",
    "King and Queen Selection",
    "Children and Youths Harvest",
    "Societal Seed Sowing",
    "CMO/CWO Harvest",
    "Geopolitical Zones Harvest",
    "Sponsorship of Brochure Pictures",
    "Brochure Launch",
    "Harvest Proper",
]

SEED_SOWING_LEVELS = ["", "Diamond", "Platinum", "Gold", "Silver", "Bronze"]
PAYMENT_MODES = ["Cash", "Transfer", "Pledge"]
COMPULSORY_CATEGORIES = ["Man", "Woman", "Youth", "Children"]
ASSETS_DIR = str(PROJECT_DIR / "assets")


def _auth_configuration():
    return {
        "app": required_password_hash("SJMCC_APP_PASSWORD_HASH"),
        "admin": required_password_hash("SJMCC_ADMIN_PASSWORD_HASH"),
        "max_attempts": integer_setting("SJMCC_AUTH_MAX_ATTEMPTS", 5, minimum=3, maximum=20),
        "lockout_seconds": integer_setting("SJMCC_AUTH_LOCKOUT_SECONDS", 300, minimum=30, maximum=3600),
        "session_timeout_seconds": integer_setting(
            "SJMCC_SESSION_TIMEOUT_SECONDS", 1800, minimum=300, maximum=86400
        ),
    }


def _password_attempt(scope: str, password: str, expected_hash: str, max_attempts: int, lockout_seconds: int) -> bool:
    """Verify a password and apply a per-session brute-force lockout."""
    attempts_key = f"{scope}_failed_attempts"
    lock_key = f"{scope}_locked_until"
    now = time.monotonic()
    locked_until = float(st.session_state.get(lock_key, 0.0))
    if now < locked_until:
        remaining = max(1, int(locked_until - now))
        st.error(f"Too many failed attempts. Try again in {remaining} seconds.")
        return False
    if verify_password(password, expected_hash):
        st.session_state[attempts_key] = 0
        st.session_state[lock_key] = 0.0
        return True
    attempts = int(st.session_state.get(attempts_key, 0)) + 1
    st.session_state[attempts_key] = attempts
    if attempts >= max_attempts:
        st.session_state[attempts_key] = 0
        st.session_state[lock_key] = now + lockout_seconds
        st.error(f"Too many failed attempts. Access is locked for {lockout_seconds} seconds.")
    else:
        st.error("Wrong password.")
    return False


def _asset_data_uri(filename):
    path = os.path.join(ASSETS_DIR, filename)
    if not os.path.exists(path):
        return ""
    ext = os.path.splitext(filename)[1].lstrip(".").lower() or "png"
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(path, "rb") as asset:
        return f"data:image/{mime};base64,{base64.b64encode(asset.read()).decode()}"


# =========================
# LOGIN GATES
# =========================
def require_app_login():
    config = _auth_configuration()
    if "app_ok" not in st.session_state:
        st.session_state["app_ok"] = False

    if st.session_state["app_ok"]:
        if expire_inactive_session(st.session_state, time.monotonic(), config["session_timeout_seconds"]):
            st.warning("Your session expired due to inactivity. Please sign in again.")
        else:
            return True

    brand, auth = st.columns([1.15, 0.85], gap="large")
    logo = _asset_data_uri("left.png")
    logo_html = f'<img class="login-logo" src="{logo}" alt="">' if logo else ""
    patron = _asset_data_uri("right.png")
    patron_html = f'<img class="login-patron" src="{patron}" alt="">' if patron else ""
    with brand:
        st.markdown(
            f"""
            <section class="login-brand">
              <div class="login-brand-top">{logo_html}<span>Financial Stewardship</span></div>
              <div class="login-art" aria-hidden="true">{patron_html}</div>
              <div class="login-brand-copy">
                <span class="login-cross">✝</span>
                <h1>St Joseph Military<br>Catholic Church, Lokoja</h1>
                <div class="login-gold-rule"></div>
                <p>2026 Harvest Financial Management</p>
              </div>
              <div class="login-brand-foot">Account Statement &amp; Records System</div>
            </section>
            """,
            unsafe_allow_html=True,
        )
    with auth:
        st.markdown('<div class="login-form-kicker">SECURE SYSTEM ACCESS</div>', unsafe_allow_html=True)
        st.title("Welcome")
        st.subheader("2026 Harvest Financial Management")
        st.warning("Password required to access this system.")
        pw = st.text_input("Enter Access Password", type="password", label_visibility="visible")
        if st.button("Login", use_container_width=True):
            if _password_attempt("app", pw, config["app"], config["max_attempts"], config["lockout_seconds"]):
                st.session_state["app_ok"] = True
                st.session_state["auth_last_activity"] = time.monotonic()
                st.success("Access granted ✅")
                st.rerun()
    return False


def require_admin_login():
    config = _auth_configuration()
    if "admin_ok" not in st.session_state:
        st.session_state["admin_ok"] = False

    if st.session_state["admin_ok"]:
        return True

    left, middle, right = st.columns([1, 1.25, 1])
    with middle:
        st.markdown('<div class="admin-lock">✦ &nbsp; RESTRICTED ADMINISTRATION</div>', unsafe_allow_html=True)
        st.warning("Admin password required.")
        pw = st.text_input("Enter Admin Password", type="password", label_visibility="visible")
        if st.button("Unlock Admin", use_container_width=True):
            if _password_attempt("admin", pw, config["admin"], config["max_attempts"], config["lockout_seconds"]):
                st.session_state["admin_ok"] = True
                st.success("Admin unlocked ✅")
                st.rerun()
    return False


# =========================
# DB HELPERS
# =========================
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table});")
    rows = cur.fetchall()
    return {r["name"] for r in rows}


def init_db_and_migrate():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON;")

    # harvest_records
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS harvest_records (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          phone_number TEXT,
          harvest_activity TEXT,
          seed_sowing_category TEXT,
          payment_mode TEXT,
          amount REAL NOT NULL DEFAULT 0,
          pledge_amount_paid REAL NOT NULL DEFAULT 0,
          created_date TEXT NOT NULL DEFAULT (date('now'))
        );
        """
    )

    # compulsory_contributions
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS compulsory_contributions (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          phone_number TEXT,
          category TEXT NOT NULL CHECK (category IN ('Man','Woman','Youth','Children')),
          amount REAL NOT NULL DEFAULT 0,
          created_date TEXT NOT NULL DEFAULT (date('now'))
        );
        """
    )

    # expenses
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          expense_date TEXT NOT NULL DEFAULT (date('now')),
          description TEXT NOT NULL,
          amount REAL NOT NULL DEFAULT 0,
          approved_by TEXT
        );
        """
    )

    # migrations
    cols_h = table_columns(conn, "harvest_records")
    if "created_date" not in cols_h:
        cur.execute("ALTER TABLE harvest_records ADD COLUMN created_date TEXT DEFAULT (date('now'));")

    cols_c = table_columns(conn, "compulsory_contributions")
    if "created_date" not in cols_c:
        cur.execute("ALTER TABLE compulsory_contributions ADD COLUMN created_date TEXT DEFAULT (date('now'));")

    cols_e = table_columns(conn, "expenses")
    if "expense_date" not in cols_e:
        cur.execute("ALTER TABLE expenses ADD COLUMN expense_date TEXT DEFAULT (date('now'));")
    if "approved_by" not in cols_e:
        cur.execute("ALTER TABLE expenses ADD COLUMN approved_by TEXT;")
    if "description" not in cols_e:
        cur.execute("ALTER TABLE expenses ADD COLUMN description TEXT;")
    if "amount" not in cols_e:
        cur.execute("ALTER TABLE expenses ADD COLUMN amount REAL DEFAULT 0;")

    conn.commit()
    conn.close()


# =========================
# INSERTS
# =========================
def insert_harvest_record(name, phone, activity, seed_cat, pay_mode, amount):
    """
    Rule:
      Cash/Transfer => Amount Paid = Amount (auto paid)
      Pledge => Amount Paid = 0 (unpaid until redeemed)
    """
    if not str(name).strip() or not str(phone).strip():
        raise ValueError("Name and phone number are required.")
    if activity not in HARVEST_ACTIVITIES:
        raise ValueError("Invalid harvest activity.")
    if seed_cat not in SEED_SOWING_LEVELS or (activity == "Seed Sowing" and not seed_cat):
        raise ValueError("Invalid seed-sowing category.")
    if pay_mode not in PAYMENT_MODES:
        raise ValueError("Invalid payment mode.")
    amt = _validated_positive_amount(amount)
    paid = amt if pay_mode in ("Cash", "Transfer") else 0.0

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO harvest_records
        (name, phone_number, harvest_activity, seed_sowing_category, payment_mode, amount, pledge_amount_paid)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (name.strip(), phone.strip(), activity, seed_cat or "", pay_mode, amt, paid),
    )
    conn.commit()
    conn.close()


def insert_compulsory(name, phone, category, amount):
    if not str(name).strip() or not str(phone).strip():
        raise ValueError("Name and phone number are required.")
    if category not in COMPULSORY_CATEGORIES:
        raise ValueError("Invalid compulsory levy category.")
    amount = _validated_positive_amount(amount)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO compulsory_contributions (name, phone_number, category, amount)
        VALUES (?, ?, ?, ?)
        """,
        (name.strip(), phone.strip(), category, amount),
    )
    conn.commit()
    conn.close()


def insert_expense(use_auto_date: bool, exp_date: date | None, description: str, amount: float, approved_by: str):
    if not str(description).strip() or not str(approved_by).strip():
        raise ValueError("Description and Approved By are required.")
    amount = _validated_positive_amount(amount)
    if not use_auto_date and exp_date is None:
        raise ValueError("Expense date is required.")
    conn = get_conn()
    cur = conn.cursor()

    if use_auto_date:
        cur.execute(
            "INSERT INTO expenses (description, amount, approved_by) VALUES (?, ?, ?)",
            (description.strip(), amount, approved_by.strip()),
        )
    else:
        cur.execute(
            "INSERT INTO expenses (expense_date, description, amount, approved_by) VALUES (?, ?, ?, ?)",
            (str(exp_date), description.strip(), amount, approved_by.strip()),
        )

    conn.commit()
    conn.close()


# =========================
# LISTS
# =========================
def list_harvest_records(limit=50000):
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT
          id,
          created_date AS "Date",
          name AS "Name",
          phone_number AS "Phone",
          harvest_activity AS "Activity",
          seed_sowing_category AS "Seed Category",
          payment_mode AS "Payment Mode",
          amount AS "Amount",
          pledge_amount_paid AS "Amount Paid",
          (amount - pledge_amount_paid) AS "Balance",
          CASE
            WHEN payment_mode IN ('Cash','Transfer') THEN 'Paid'
            WHEN (amount - pledge_amount_paid) <= 0 THEN 'Paid'
            ELSE 'Unpaid'
          END AS "Status"
        FROM harvest_records
        ORDER BY id DESC
        LIMIT ?
        """,
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df


def list_compulsory(limit=50000):
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT
          id,
          created_date AS "Date",
          name AS "Name",
          phone_number AS "Phone",
          category AS "Category",
          amount AS "Amount"
        FROM compulsory_contributions
        ORDER BY id DESC
        LIMIT ?
        """,
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df


def list_expenses(limit=50000):
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT
          id,
          expense_date AS "Date",
          description AS "Description",
          amount AS "Amount",
          approved_by AS "Approved By"
        FROM expenses
        ORDER BY Date DESC, id DESC
        LIMIT ?
        """,
        conn,
        params=(int(limit),),
    )
    conn.close()
    return df


# =========================
# UPDATES
# =========================
def update_amount_paid_add(record_id: int, add_now: float):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT amount, pledge_amount_paid, payment_mode FROM harvest_records WHERE id = ?",
        (int(record_id),),
    )
    row = cur.fetchone()
    if row is None:
        conn.close()
        raise ValueError("Record not found.")

    if row["payment_mode"] != "Pledge":
        conn.close()
        raise ValueError("Only pledge records can receive pledge-redemption payments.")

    try:
        new_paid = redeemed_total(row["amount"], row["pledge_amount_paid"], add_now, row["payment_mode"])
    except ValueError:
        conn.close()
        raise

    cur.execute("UPDATE harvest_records SET pledge_amount_paid = ? WHERE id = ?", (new_paid, int(record_id)))
    conn.commit()
    conn.close()
    return new_paid


# =========================
# ADMIN EDIT/DELETE
# =========================
def _require_admin_authorized():
    """Enforce admin authorization at the mutation boundary as well as in the UI."""
    require_admin(st.session_state)


def _validated_date(value, field_name="Date") -> str:
    text = str(value).strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date().isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must use YYYY-MM-DD format.") from exc


def _validated_amount(value, field_name="Amount") -> float:
    return nonnegative_amount(value, field_name)


def _validated_positive_amount(value, field_name="Amount") -> float:
    return positive_amount(value, field_name)


def admin_delete(table: str, rid: int):
    _require_admin_authorized()
    delete_statements = {
        "harvest_records": "DELETE FROM harvest_records WHERE id = ?",
        "compulsory_contributions": "DELETE FROM compulsory_contributions WHERE id = ?",
        "expenses": "DELETE FROM expenses WHERE id = ?",
    }
    if table not in delete_statements:
        raise ValueError("Invalid table.")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(delete_statements[table], (int(rid),))
    if cur.rowcount != 1:
        conn.rollback()
        conn.close()
        raise ValueError("Record not found; nothing was deleted.")
    conn.commit()
    conn.close()


def admin_update_harvest(rid: int, created_date, name, phone, activity, seed, paymode, amount, amount_paid):
    _require_admin_authorized()
    if not str(name).strip():
        raise ValueError("Name is required.")
    if activity not in HARVEST_ACTIVITIES or seed not in SEED_SOWING_LEVELS or paymode not in PAYMENT_MODES:
        raise ValueError("Invalid harvest record selection.")
    created_date = _validated_date(created_date)
    amount = _validated_positive_amount(amount)
    amount_paid = _validated_amount(amount_paid, "Amount paid")
    if amount_paid > amount:
        raise ValueError("Amount paid cannot exceed the pledged amount.")
    if paymode in ("Cash", "Transfer") and amount_paid != amount:
        raise ValueError("Cash and Transfer records must have Amount Paid equal to Amount.")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE harvest_records
        SET created_date = ?, name = ?, phone_number = ?, harvest_activity = ?, seed_sowing_category = ?,
            payment_mode = ?, amount = ?, pledge_amount_paid = ?
        WHERE id = ?
        """,
        (created_date, name.strip(), phone.strip(), activity, seed, paymode, amount, amount_paid, int(rid)),
    )
    if cur.rowcount != 1:
        conn.rollback()
        conn.close()
        raise ValueError("Record not found; nothing was updated.")
    conn.commit()
    conn.close()


def admin_update_compulsory(rid: int, created_date, name, phone, category, amount):
    _require_admin_authorized()
    if not str(name).strip():
        raise ValueError("Name is required.")
    if category not in COMPULSORY_CATEGORIES:
        raise ValueError("Invalid compulsory levy category.")
    created_date = _validated_date(created_date)
    amount = _validated_positive_amount(amount)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE compulsory_contributions
        SET created_date = ?, name = ?, phone_number = ?, category = ?, amount = ?
        WHERE id = ?
        """,
        (created_date, name.strip(), phone.strip(), category, amount, int(rid)),
    )
    if cur.rowcount != 1:
        conn.rollback()
        conn.close()
        raise ValueError("Record not found; nothing was updated.")
    conn.commit()
    conn.close()


def admin_update_expense(rid: int, expense_date, description, amount, approved_by):
    _require_admin_authorized()
    if not str(description).strip() or not str(approved_by).strip():
        raise ValueError("Description and Approved By are required.")
    expense_date = _validated_date(expense_date)
    amount = _validated_positive_amount(amount)
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE expenses
        SET expense_date = ?, description = ?, amount = ?, approved_by = ?
        WHERE id = ?
        """,
        (expense_date, description.strip(), amount, approved_by.strip(), int(rid)),
    )
    if cur.rowcount != 1:
        conn.rollback()
        conn.close()
        raise ValueError("Record not found; nothing was updated.")
    conn.commit()
    conn.close()


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return safe_csv_bytes(df)


def render_table(data, *, formats=None, column_config=None, hide_index=None, height="auto"):
    """Render a consistent, interactive financial grid without altering its data."""
    frame = data.to_frame() if isinstance(data, pd.Series) else data
    automatic_config = monetary_column_config(frame)
    column_config = {**automatic_config, **(column_config or {})}
    styler = frame.style
    if formats:
        styler = styler.format(formats)
    styler = styler.set_properties(
        **{
            "text-align": "center",
            "font-size": "14px",
            "font-weight": "400",
            "padding": "10px 12px",
        }
    ).set_table_styles(
        [
            {
                "selector": "th",
                "props": [
                    ("text-align", "center"),
                    ("font-size", "14px"),
                    ("font-weight", "600"),
                    ("padding", "10px 12px"),
                ],
            }
        ],
        overwrite=False,
    )
    st.dataframe(
        styler,
        width="stretch",
        height=height,
        hide_index=hide_index,
        column_config=column_config,
        row_height=44,
    )


def monetary_column_config(data):
    """Display monetary columns with grouping and no decimals; values stay numeric."""
    frame = data.to_frame() if isinstance(data, pd.Series) else data
    monetary_columns = {
        "Amount", "Amount Paid", "Balance", "Pledged", "Received",
        "Total Amount", "Total Paid", "Total Balance",
    }
    return {
        column: st.column_config.NumberColumn(column, format="localized", step=1)
        for column in frame.columns
        if column in monetary_columns
        and (
            pd.api.types.is_numeric_dtype(frame[column])
            or frame[column].dropna().map(lambda value: isinstance(value, numbers.Number)).all()
        )
    }
def render_activity_summary_table(frame):
    """Balanced read-only presentation for the programme financial summary."""
    rows = []
    for activity, row in frame.iterrows():
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(activity))}</td>"
            f"<td>{naira(row['Pledged'])}</td>"
            f"<td>{naira(row['Received'])}</td>"
            f"<td>{int(row['Records']):,}</td>"
            f"<td>{naira(row['Balance'])}</td>"
            "</tr>"
        )
    st.markdown(
        """
        <div class="financial-table-scroll" role="region" aria-label="Harvest by programme financial table" tabindex="0">
          <table class="financial-summary-table">
            <thead><tr>
              <th>Activity</th><th>Pledged</th><th>Received</th><th>Records</th><th>Balance</th>
            </tr></thead>
            <tbody>
        """
        + "".join(rows)
        + "</tbody></table></div>",
        unsafe_allow_html=True,
    )


# =========================
# THEME / STYLING
# =========================
NAVY = "#172F4D"
GOLD = "#B78B43"
WINE = "#7F2F45"

def inject_css():
    st.markdown(
        """
        <style>
          @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Source+Sans+3:wght@400;500;600;700&display=swap');

          :root {
            --forest:#172F4D; --forest-deep:#0F223A; --forest-soft:#2455A4; --gold:#9A6C25; --gold-soft:#E7D3A8;
            --wine:#7F2F45; --offwhite:#FBFCFE; --paper:#F0F4F9; --card:#FFFFFF; --ink:#24334B;
            --muted:#526278; --line:#CFD9E5; --success:#176B4D; --error:#A93648; --shadow:rgba(15,34,58,.12);
            --blue:#2455A4; --blue-hover:#1C4588; --field-text:#1E293B; --field-placeholder:#66758A;
          }

          .stApp {
            background:
              radial-gradient(1200px 500px at 50% -10%, rgba(36,85,164,.07), transparent 55%),
              linear-gradient(180deg,var(--offwhite) 0%,#F0F4F9 100%);
            background-attachment: fixed;
          }
          .block-container {
            padding-top: 1.4rem; padding-bottom: 3rem;
            max-width: 1480px; padding-left: clamp(1rem,3vw,3rem); padding-right: clamp(1rem,3vw,3rem);
          }
          html, body, [class*="css"], .stMarkdown {
            font-family: "Source Sans 3", "Segoe UI", system-ui, sans-serif; color: var(--ink);
          }
          h1,h2,h3,h4 { font-family: "Cormorant Garamond", Georgia, serif; color: var(--forest); }

          .sjmcc-hero {
            position: relative; text-align:center;
            background: linear-gradient(180deg, #ffffff 0%, #f7f8f4 100%);
            border:1px solid var(--line); border-top:6px solid var(--gold);
            border-bottom:3px solid var(--gold); border-radius: 16px;
            padding: 18px 34px 20px; margin-bottom: 24px;
            box-shadow: 0 12px 28px rgba(18, 42, 35, 0.08);
          }
          .hero-row { display:flex; align-items:center; justify-content:space-between; gap:24px; }
          .hero-text { flex:1 1 auto; min-width:0; }
          .hero-logo {
            height:120px; width:auto; flex:0 0 auto; border-radius:14px;
            background:#ffffff; padding:5px; border:1px solid var(--line);
            box-shadow:0 6px 18px rgba(24,61,50,0.12);
          }
          @media (max-width: 760px) { .hero-logo { height:72px; } .hero-row { gap:12px; }
            .sjmcc-hero h1 { font-size:1.5rem !important; } }
          .hero-text .cross { color: var(--gold); font-size:1.3rem; line-height:1; display:block; margin-bottom:2px; }
          .sjmcc-hero h1 {
            color: var(--forest) !important; font-size:2.55rem; margin:0; font-weight:700;
            line-height:1.08; letter-spacing:.4px;
          }
          .sjmcc-hero .rule {
            width:230px; height:2.5px; margin:9px auto 8px;
            background:linear-gradient(90deg, transparent, var(--gold), transparent);
          }
          .sjmcc-hero p  { color: var(--forest-soft); margin:2px 0 0; font-size:1.45rem; font-weight:700;
            font-family:"Cormorant Garamond",serif; letter-spacing:.5px; }
          .sjmcc-hero small { color: var(--muted); font-size:.82rem; letter-spacing:2px; text-transform:uppercase; font-weight:600; }

          .auth-shell {
            display: flex; justify-content: center; padding: 18px 0 10px;
          }
          .auth-shell-small {
            padding-top: 12px;
          }
          .auth-card {
            width: min(100%, 540px); background: rgba(255,255,255,0.92);
            border: 1px solid var(--line); border-radius: 20px; padding: 26px 28px 18px;
            box-shadow: 0 20px 40px rgba(17, 34, 29, 0.12); backdrop-filter: blur(4px);
          }
          .auth-card-compact {
            padding-top: 22px; padding-bottom: 14px;
          }
          .auth-badge {
            display: inline-block; padding: 6px 10px; border-radius: 999px;
            background: rgba(179,149,85,0.16); color: var(--forest); font-size: 0.72rem;
            font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;
            margin-bottom: 12px; border: 1px solid rgba(179,149,85,0.28);
          }
          .auth-heading {
            color: var(--forest); font-family:"Cormorant Garamond",Georgia,serif;
            font-size: 2.2rem; font-weight: 700; line-height: 1.1; margin: 0; letter-spacing: .2px;
          }
          .auth-subtitle {
            margin: 8px 0 0; color: var(--muted); font-size: 1rem; font-weight: 600;
          }
          .auth-rule {
            width: 100%; height: 2px; background: linear-gradient(90deg, var(--gold), transparent);
            margin: 14px 0 10px;
          }
          .auth-note {
            margin: 6px 0 14px; color: var(--muted); font-size: 0.95rem; font-weight: 500;
          }

          [data-testid="stMetric"] {
            min-height:112px;
            background: linear-gradient(180deg, #ffffff 0%, #f9faf7 100%);
            border:1px solid var(--line); border-top:3px solid var(--gold);
            border-radius:12px; padding:16px 18px; box-shadow:0 6px 16px rgba(15, 31, 28, 0.06);
          }
          [data-testid="stMetric"]:hover { box-shadow:0 10px 22px rgba(15,31,28,0.10); }
          [data-testid="stMetricLabel"] p {
            font-size:.80rem !important; color: var(--muted) !important; font-weight:700;
            text-transform:uppercase; letter-spacing:.12em;
          }
          [data-testid="stMetricValue"] {
            font-size:1.55rem !important; color: var(--forest) !important; font-weight:700;
          }

          .sjmcc-sec {
            color: var(--forest); font-weight:700; font-size:1.45rem;
            font-family:"Cormorant Garamond", Georgia, serif;
            border-bottom:2px solid var(--gold); padding:2px 0 6px; margin:22px 0 12px;
            display:flex; align-items:center; gap:8px;
          }

          .stButton>button, .stFormSubmitButton>button {
            min-height:2.75rem;
            border-radius:12px; font-weight:700; border:1px solid var(--forest);
            background:linear-gradient(180deg, #ffffff 0%, #f3f6f2 100%); color:var(--forest);
            box-shadow:0 2px 8px rgba(16,32,29,0.08); transition:all 0.18s ease;
          }
          .stButton>button:hover, .stFormSubmitButton>button:hover {
            border-color: var(--gold); background: linear-gradient(180deg, rgba(179,149,85,0.12) 0%, rgba(179,149,85,0.18) 100%);
            color: var(--forest-deep); transform: translateY(-1px); box-shadow:0 8px 18px rgba(16,32,29,0.12);
          }
          .stDownloadButton>button {
            min-height:2.75rem;
            border-radius:12px; font-weight:700; letter-spacing:.3px; border:none;
            background:linear-gradient(135deg, var(--forest) 0%, var(--forest-soft) 100%);
            color:#fdfcf8; padding:.7rem 1.2rem; box-shadow:0 8px 18px rgba(24,61,50,0.2);
          }
          .stDownloadButton>button:hover {
            background:linear-gradient(135deg, var(--gold) 0%, #d2b779 100%); color:var(--forest-deep);
          }

          .stTextInput label, .stNumberInput label, .stDateInput label, .stSelectbox label, .stTextArea label {
            color: var(--forest) !important; font-weight: 700; margin-bottom: 6px;
          }
          .stTextInput input, .stNumberInput input, .stDateInput input, textarea,
          div[data-baseweb="select"]>div {
            min-height:2.75rem;
            background:#ffffff !important; border-radius:10px !important; border:1px solid var(--line) !important;
            box-shadow: inset 0 1px 2px rgba(32,41,35,0.02);
          }
          .stTextInput input, .stNumberInput input, .stDateInput input, textarea,
          .stSelectbox span, .stSelectbox div {
            color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important;
            caret-color: var(--forest) !important;
          }
          .stTextInput input:focus, .stNumberInput input:focus, .stDateInput input:focus, textarea:focus,
          div[data-baseweb="select"]:focus-within {
            border-color: var(--gold) !important; box-shadow: 0 0 0 3px rgba(179,149,85,0.18) !important;
          }
          [role="listbox"], [role="option"] { background:#ffffff !important; }
          [role="listbox"] *, [role="option"] * { color:var(--ink) !important; -webkit-text-fill-color:var(--ink) !important; }
          [role="option"]:hover, [role="option"][aria-selected="true"] { background:#e8f0ec !important; }
          [data-baseweb="checkbox"] span, [data-baseweb="radio"] span { color:var(--ink) !important; }
          [data-testid="stForm"] {
            background:#ffffff; border:1px solid var(--line); border-radius:14px;
            padding:clamp(1rem,2vw,1.5rem); box-shadow:0 6px 18px rgba(24,61,50,.05);
          }
          button:focus-visible, input:focus-visible, textarea:focus-visible, [tabindex]:focus-visible {
            outline:3px solid rgba(35,122,87,.28) !important; outline-offset:2px;
          }
          button:disabled { opacity:1 !important; color:#67736d !important; background:#e5eae7 !important; }

          .stTabs [data-baseweb="tab-list"] { gap:6px; border-bottom:2px solid var(--line); }
          .stTabs [data-baseweb="tab"] {
            background:#f0f4ef; border-radius:10px 10px 0 0; padding:8px 16px; color:var(--forest);
            font-weight:600; border:1px solid transparent; border-bottom:none;
          }
          .stTabs [aria-selected="true"] { background:var(--forest); color:#ffffff !important; }
          .stTabs [aria-selected="true"] * { color:#ffffff !important; }

          [data-testid="stDataFrame"] {
            border:1px solid var(--line); border-radius:12px; overflow:hidden;
            box-shadow:0 6px 18px rgba(24,61,50,0.05);
          }
          [data-testid="stDataFrame"] th {
            background: rgba(24,61,50,0.04)!important; color: var(--forest)!important; font-weight:700!important;
          }
          [data-testid="stDataFrame"] td { color: var(--ink)!important; }
          .financial-table-scroll {
            width:100%; overflow-x:auto; margin:0 0 20px; border:1px solid var(--line);
            border-radius:12px; background:#fff; box-shadow:0 6px 18px rgba(15,34,58,.05);
            -webkit-overflow-scrolling:touch;
          }
          .financial-table-scroll:focus-visible { outline:3px solid rgba(36,85,164,.25); outline-offset:2px; }
          .financial-summary-table { width:100%; min-width:760px; border-collapse:separate; border-spacing:0; table-layout:fixed; }
          .financial-summary-table th,.financial-summary-table td {
            height:44px; padding:10px 12px; text-align:center; vertical-align:middle;
            border-right:1px solid #E1E7EF; border-bottom:1px solid #E1E7EF;
            color:#24334B; font-family:"Source Sans 3","Segoe UI",sans-serif; font-size:14px;
            line-height:1.35; white-space:normal; overflow-wrap:anywhere;
          }
          .financial-summary-table th {
            background:#EAF0F8; color:#172F4D; font-weight:600; letter-spacing:.01em;
          }
          .financial-summary-table td { font-weight:450; background:#fff; }
          .financial-summary-table tbody tr:nth-child(even) td { background:#F7F9FC; }
          .financial-summary-table th:first-child,.financial-summary-table td:first-child { width:32%; }
          .financial-summary-table th:nth-child(2),.financial-summary-table td:nth-child(2),
          .financial-summary-table th:nth-child(3),.financial-summary-table td:nth-child(3),
          .financial-summary-table th:nth-child(5),.financial-summary-table td:nth-child(5) { width:19%; }
          .financial-summary-table th:nth-child(4),.financial-summary-table td:nth-child(4) { width:11%; }
          .financial-summary-table th:last-child,.financial-summary-table td:last-child { border-right:0; }
          .financial-summary-table tbody tr:last-child td { border-bottom:0; }
          [data-testid="stVegaLiteChart"], [data-testid="stArrowVegaLiteChart"] {
            background:#ffffff; border:1px solid var(--line); border-radius:12px; padding:10px;
            box-shadow:0 6px 18px rgba(24,61,50,.04);
          }

          [data-testid="stNotification"], .stAlert {
            border-radius:12px; border-left:4px solid var(--gold); background: rgba(255,255,255,0.9);
          }
          .stAlert>div>div>div { color: var(--ink); }

          section[data-testid="stSidebar"] {
            background:linear-gradient(180deg, #102c2b 0%, #183d32 55%, #204e46 100%);
            border-right:3px solid var(--gold);
          }
          section[data-testid="stSidebar"] * { color:#edf4f2; }
          section[data-testid="stSidebar"] h1,
          section[data-testid="stSidebar"] h2,
          section[data-testid="stSidebar"] h3 { color: #f3dca4; }
          section[data-testid="stSidebar"] div[data-baseweb="select"]>div {
            background:#ffffff !important; border:1px solid rgba(211,189,143,0.9) !important;
          }
          section[data-testid="stSidebar"] div[data-baseweb="select"] * { color:var(--forest) !important; }

          #MainMenu, footer, [data-testid="stAppDeployButton"] { visibility:hidden; }
          header[data-testid="stHeader"] { background:transparent; }

          .sjmcc-nav-label {
            color: var(--forest); font-weight:700; font-size:1.05rem;
            font-family:"Cormorant Garamond", Georgia, serif; letter-spacing:.3px;
            margin: 2px 0 -6px;
          }
          .st-key-nav_page div[data-baseweb="select"]>div {
            background:#ffffff !important; border:1.5px solid var(--forest) !important;
            border-radius:12px !important; box-shadow:0 3px 10px rgba(24,61,50,0.07);
          }
          .st-key-nav_page div[data-baseweb="select"] * { color:var(--forest) !important; font-weight:600; }

          @media (max-width: 640px) {
            .block-container { padding-top: 0.9rem; padding-bottom: 2rem; padding-left: 0.8rem; padding-right: 0.8rem; }
            .sjmcc-hero { padding: 14px 14px 16px; margin-bottom: 16px; border-radius: 12px; }
            .hero-row { gap: 12px; }
            .hero-logo { height: 56px; padding: 4px; }
            .sjmcc-hero h1 { font-size: 1.28rem !important; line-height: 1.12; }
            .sjmcc-hero p { font-size: 1.05rem; }
            .sjmcc-hero small { font-size: .68rem; letter-spacing: 1.2px; }
            .sjmcc-hero .rule { width: 150px; }
            [data-testid="stHorizontalBlock"] { flex-wrap: wrap; gap: 10px; }
            [data-testid="stColumn"] { flex: 1 1 100%; min-width: 100%; }
            [data-testid="stColumn"]:has([data-testid="stMetric"]) {
              flex: 1 1 100%; min-width: 100%;
            }
            [data-testid="stMetric"] { padding: 12px 12px; }
            [data-testid="stMetricValue"] { font-size: 1.2rem !important; }
            [data-testid="stMetricLabel"] p { font-size: .68rem !important; }
            .sjmcc-sec { font-size: 1.2rem; margin: 16px 0 10px; }
            .stTabs [data-baseweb="tab-list"] {
              overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch;
            }
            .stTabs [data-baseweb="tab"] { padding: 6px 12px; white-space: nowrap; }
            [data-testid="stDataFrame"] { overflow-x: auto; }
            .stButton>button, .stFormSubmitButton>button, .stDownloadButton>button { width:100%; }
          }
          @media (min-width:641px) and (max-width:1024px) {
            [data-testid="stHorizontalBlock"] { flex-wrap:wrap; }
            [data-testid="stColumn"]:has([data-testid="stMetric"]) { flex:1 1 calc(50% - 1rem); min-width:260px; }
          }
          @media (prefers-reduced-motion:reduce) {
            *, *::before, *::after { scroll-behavior:auto !important; transition:none !important; }
          }

          /* ===== reconstructed product composition ===== */
          .login-brand {
            min-height:680px; position:relative; overflow:hidden; display:flex; flex-direction:column;
            justify-content:space-between; padding:38px 42px; border-radius:24px;
            background:
              radial-gradient(circle at 88% 12%, rgba(182,154,98,.25) 0 2px, transparent 3px),
              radial-gradient(circle at 15% 80%, rgba(255,255,255,.06) 0 1px, transparent 2px),
              linear-gradient(145deg,#102a23 0%,#173d32 58%,#225345 100%);
            background-size:auto,24px 24px,auto; box-shadow:0 28px 70px rgba(16,42,35,.25);
          }
          .login-brand::after {
            content:""; position:absolute; width:440px; height:440px; right:-240px; bottom:-160px;
            border:1px solid rgba(182,154,98,.32); border-radius:50%; box-shadow:0 0 0 54px rgba(182,154,98,.05),0 0 0 108px rgba(182,154,98,.035);
          }
          .login-brand-top { display:flex; align-items:center; gap:14px; color:#fff; font-size:.76rem; font-weight:700; letter-spacing:.14em; text-transform:uppercase; z-index:1; }
          .login-logo { width:58px; height:58px; object-fit:contain; padding:4px; background:#fff; border-radius:14px; }
          .login-brand-copy { z-index:1; max-width:590px; }
          .login-cross { color:var(--gold-soft); font-size:2rem; }
          .login-brand h1 { color:#fff !important; font-size:clamp(2.25rem,4vw,4.25rem); line-height:1.08; letter-spacing:-.035em; margin:12px 0 20px; }
          .login-gold-rule { width:76px; height:3px; background:var(--gold); margin-bottom:20px; }
          .login-brand p { color:#e8eee9; font-size:1.2rem; max-width:430px; }
          .login-brand-foot { color:#cbd8d1; font-size:.75rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; z-index:1; }
          [data-testid="stColumn"]:has(.login-form-kicker) { display:flex; flex-direction:column; justify-content:center; padding:clamp(1rem,4vw,4.5rem); }
          .login-form-kicker, .admin-lock { color:var(--gold); font-size:.72rem; font-weight:800; letter-spacing:.16em; margin-bottom:10px; }
          [data-testid="stColumn"]:has(.login-form-kicker) h1 { font-size:2.5rem; margin-bottom:.2rem; }
          [data-testid="stColumn"]:has(.login-form-kicker) h3 { color:var(--muted); font-family:"Source Sans 3",sans-serif; font-size:1rem; font-weight:500; margin-bottom:1.6rem; }
          [data-testid="stColumn"]:has(.login-form-kicker) .stButton button { width:100%; background:var(--forest); color:#fff; min-height:3.1rem; }

          section[data-testid="stSidebar"] { width:282px !important; min-width:282px !important; border-right:0; box-shadow:8px 0 32px rgba(16,42,35,.12); }
          section[data-testid="stSidebar"] [data-testid="stSidebarContent"] { padding:1.2rem .9rem; }
          .side-brand { display:flex; align-items:center; gap:12px; padding:10px 8px 26px; border-bottom:1px solid rgba(255,255,255,.12); }
          .side-brand img { width:48px; height:48px; object-fit:contain; background:#fff; border-radius:12px; padding:3px; }
          .side-mark { font-size:1.6rem; color:var(--gold-soft) !important; }
          .side-brand strong { display:block; color:#fff !important; font-family:"Cormorant Garamond",serif; font-size:1.3rem; line-height:1.1; }
          .side-brand small { display:block; color:#b9cac2 !important; font-size:.75rem; margin-top:3px; }
          .side-section-label { color:#8fa9a0 !important; font-size:.65rem; font-weight:800; letter-spacing:.16em; padding:24px 12px 8px; }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label {
            padding:10px 12px; margin:2px 0; border-radius:9px; transition:background .15s ease; cursor:pointer;
          }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label > div:first-child { display:none !important; }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover { background:rgba(255,255,255,.08); }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
            background:#fff; box-shadow:0 7px 18px rgba(0,0,0,.14);
          }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * { color:var(--forest) !important; font-weight:700; }
          section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p { color:#e8f0ec; font-size:.91rem; }
          .side-footer { margin-top:28px; padding:18px 12px 8px; border-top:1px solid rgba(255,255,255,.12); }
          .side-footer span,.side-footer small { display:block; color:#d8e3dd !important; }
          .side-footer span { font-weight:700; } .side-footer small { color:#91a9a0 !important; margin-top:3px; }

          .workspace-eyebrow { color:var(--muted); font-size:.68rem; font-weight:800; letter-spacing:.15em; margin:2px 0 12px; }
          .page-head { display:flex; align-items:flex-start; justify-content:space-between; gap:2rem; padding:24px 28px; margin-bottom:28px; background:#fff; border:1px solid var(--line); border-radius:16px; box-shadow:0 8px 26px rgba(24,61,50,.055); }
          .page-badge { display:inline-block; color:var(--gold); font-size:.67rem; font-weight:800; letter-spacing:.15em; margin-bottom:7px; }
          .page-head h1 { margin:0; color:var(--forest); font-size:clamp(1.75rem,2.7vw,2.45rem); line-height:1.15; }
          .page-head p { color:var(--muted); margin:8px 0 0; max-width:700px; }
          .page-head-mark { display:grid; place-items:center; flex:0 0 48px; width:48px; height:48px; color:var(--gold); background:#f6f1e7; border-radius:50%; font-size:1.2rem; }
          .context-panel { position:sticky; top:1rem; min-height:260px; padding:28px; border-radius:16px; color:#fff; background:linear-gradient(145deg,var(--forest-deep),var(--forest)); overflow:hidden; }
          .context-panel::after { content:""; position:absolute; width:180px; height:180px; border:1px solid rgba(182,154,98,.35); border-radius:50%; right:-85px; bottom:-80px; }
          .context-panel>span { display:grid; place-items:center; width:38px; height:38px; border:1px solid rgba(215,195,151,.55); border-radius:50%; color:var(--gold-soft); font-size:.75rem; font-weight:800; }
          .context-panel h3 { color:#fff; margin:48px 0 10px; font-size:1.4rem; }
          .context-panel p { color:#cbd8d1; margin:0; }
          [data-testid="stForm"] { padding:clamp(1.25rem,3vw,2rem); border-radius:16px; box-shadow:0 12px 32px rgba(24,61,50,.06); }

          /* The first financial row carries visual priority; following rows are quieter. */
          .financial-hero { display:grid; grid-template-columns:minmax(280px,1.15fr) minmax(320px,.85fr); background:var(--forest-deep); border-radius:18px; overflow:hidden; margin-bottom:16px; box-shadow:0 16px 34px rgba(16,42,35,.16); }
          .net-position { padding:34px; display:flex; flex-direction:column; justify-content:center; min-height:220px; background:radial-gradient(circle at 10% 10%,rgba(182,154,98,.15),transparent 48%); }
          .net-position span,.financial-stack span { color:#afc1b9; font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.12em; }
          .net-position strong { color:#fff; font-family:"Cormorant Garamond",serif; font-size:clamp(2.5rem,5vw,4rem); line-height:1.1; margin:10px 0; }
          .net-position small { color:#94aaa1; }
          .financial-stack { display:grid; grid-template-rows:repeat(3,1fr); background:rgba(255,255,255,.035); }
          .financial-stack>div { display:flex; align-items:center; justify-content:space-between; gap:1rem; padding:18px 24px; border-left:1px solid rgba(255,255,255,.1); border-bottom:1px solid rgba(255,255,255,.1); }
          .financial-stack>div:last-child { border-bottom:0; }
          .financial-stack strong { color:#fff; font-size:1.25rem; white-space:nowrap; }
          [data-testid="stMetric"] { border-top:0; border-left:4px solid var(--gold); min-height:118px; }
          [data-testid="stHorizontalBlock"]:has([data-testid="stMetric"]) { gap:14px; }

          @media (max-width:800px) {
            .login-brand { min-height:350px; padding:26px; }
            .login-brand h1 { font-size:2.25rem; }
            [data-testid="stColumn"]:has(.login-form-kicker) { padding:2rem .5rem; }
            .page-head { padding:20px; } .page-head-mark { display:none; }
            .context-panel { position:relative; min-height:190px; }
            .context-panel h3 { margin-top:26px; }
            .financial-hero { grid-template-columns:1fr; }
            .net-position { min-height:180px; padding:26px; }
            .financial-stack>div { border-left:0; }
          }

          /* ===== navy visual system and interaction-state guarantees ===== */
          .login-brand {
            background:
              radial-gradient(circle at 88% 12%,rgba(183,139,67,.2) 0 2px,transparent 3px),
              radial-gradient(circle at 15% 80%,rgba(255,255,255,.055) 0 1px,transparent 2px),
              linear-gradient(145deg,#0F223A 0%,#172F4D 58%,#214B7C 100%);
            box-shadow:0 28px 70px rgba(15,34,58,.25);
          }
          .login-art { position:absolute; z-index:0; right:34px; top:96px; width:min(34%,210px); padding:8px; border-radius:18px; background:rgba(255,255,255,.96); border:1px solid rgba(231,211,168,.8); box-shadow:0 18px 34px rgba(5,17,31,.28); transform:rotate(1.25deg); }
          .login-patron { display:block; width:100%; height:auto; max-height:290px; object-fit:contain; border-radius:11px; }
          .login-brand-copy { max-width:68%; }
          .login-brand p { color:#E7EDF6; }
          .login-brand-foot { color:#CFD9E5; }
          .login-form-kicker,.admin-lock,.page-badge { color:#9A6C25; }
          [data-testid="stColumn"]:has(.login-form-kicker) .stButton button,
          .stFormSubmitButton>button { background:var(--blue); border-color:var(--blue); color:#fff !important; }
          [data-testid="stColumn"]:has(.login-form-kicker) .stButton button:hover,
          .stFormSubmitButton>button:hover { background:var(--blue-hover); border-color:var(--blue-hover); color:#fff !important; }

          section[data-testid="stSidebar"] { background:linear-gradient(180deg,#0F223A 0%,#172F4D 58%,#1D3E67 100%); box-shadow:8px 0 32px rgba(15,34,58,.14); }
          .side-brand small { color:#C4D1E1 !important; }
          .side-section-label { color:#A9BCD3 !important; }
          section[data-testid="stSidebar"] [data-testid="stRadio"] [data-testid="stMarkdownContainer"] p { color:#F3F6FA !important; }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { background:#fff; }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) { box-shadow:inset 4px 0 0 var(--blue),0 7px 18px rgba(0,0,0,.14); }
          section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) * { color:#172F4D !important; }
          .side-footer span { color:#F3F6FA !important; }
          .side-footer small { color:#AFC0D4 !important; }
          .context-panel,.financial-hero { background:linear-gradient(145deg,#0F223A,#172F4D); }
          .context-panel p { color:#D6E0EC; }
          .net-position span,.financial-stack span { color:#C3D1E1; }
          .net-position small { color:#B5C5D7; }
          .page-head,[data-testid="stForm"],[data-testid="stMetric"],[data-testid="stDataFrame"] { box-shadow:0 8px 26px rgba(15,34,58,.055); }

          .stTextInput input,.stNumberInput input,.stDateInput input,textarea,
          div[data-baseweb="select"]>div {
            background:#FFFFFF !important; color:var(--field-text) !important;
            -webkit-text-fill-color:var(--field-text) !important; border-color:var(--line) !important;
            caret-color:var(--blue) !important; opacity:1 !important;
          }
          .stTextInput input:hover,.stNumberInput input:hover,.stDateInput input:hover,textarea:hover,
          div[data-baseweb="select"]>div:hover { border-color:#91A5BF !important; }
          .stTextInput input:focus,.stNumberInput input:focus,.stDateInput input:focus,textarea:focus,
          div[data-baseweb="select"]:focus-within {
            background:#FFFFFF !important; color:var(--field-text) !important;
            -webkit-text-fill-color:var(--field-text) !important; border-color:var(--blue) !important;
            box-shadow:0 0 0 3px rgba(36,85,164,.16) !important;
          }
          input::placeholder,textarea::placeholder { color:var(--field-placeholder) !important; -webkit-text-fill-color:var(--field-placeholder) !important; opacity:1 !important; }
          input:-webkit-autofill,input:-webkit-autofill:hover,input:-webkit-autofill:focus,input:-webkit-autofill:active {
            -webkit-text-fill-color:var(--field-text) !important; caret-color:var(--blue) !important;
            -webkit-box-shadow:0 0 0 1000px #FFFFFF inset !important; box-shadow:0 0 0 1000px #FFFFFF inset !important;
            transition:background-color 9999s ease-out 0s;
          }
          input[type="password"],input[type="password"]:hover,input[type="password"]:focus {
            background:#FFFFFF !important; color:var(--field-text) !important; -webkit-text-fill-color:var(--field-text) !important;
            caret-color:var(--blue) !important; color-scheme:light !important;
          }
          [data-baseweb="input"] svg,[data-baseweb="select"] svg { fill:#526278 !important; color:#526278 !important; }
          [role="listbox"],[role="option"] { background:#FFFFFF !important; color:var(--field-text) !important; }
          [role="option"] * { color:var(--field-text) !important; -webkit-text-fill-color:var(--field-text) !important; }
          [role="option"]:hover,[role="option"][aria-selected="true"] { background:#E8EFFA !important; }
          button:focus-visible,input:focus-visible,textarea:focus-visible,[tabindex]:focus-visible { outline:3px solid rgba(36,85,164,.28) !important; outline-offset:2px; }

          @media (max-width:800px) {
            .login-art { right:20px; top:80px; width:120px; padding:5px; }
            .login-patron { max-height:170px; }
            .login-brand-copy { max-width:66%; }
            .login-brand h1 { font-size:clamp(1.7rem,7vw,2.25rem); }
          }
          @media (max-width:480px) {
            .login-brand { min-height:430px; }
            .login-art { position:relative; order:2; top:auto; right:auto; width:92px; margin:12px 0; transform:none; }
            .login-brand-copy { max-width:100%; order:3; }
            .login-brand-foot { order:4; }
            .login-brand h1 { font-size:1.75rem; }
          }

          /* Sidebar safety: permanent on desktop, recoverable overlay on smaller screens. */
          @media (min-width:1024px) {
            [data-testid="stToolbar"] { visibility:hidden !important; }
            section[data-testid="stSidebar"] {
              display:block !important; visibility:visible !important; opacity:1 !important;
              transform:none !important; left:0 !important; margin-left:0 !important;
              width:282px !important; min-width:282px !important;
              transition:none !important;
            }
            [data-testid="stSidebarCollapseButton"],
            [data-testid="stSidebarCollapsedControl"],
            [data-testid="stExpandSidebarButton"] { display:none !important; }
          }
          @media (max-width:1023px) {
            [data-testid="stToolbar"] { visibility:visible !important; }
            [data-testid="stToolbar"] * { visibility:hidden !important; }
            [data-testid="stSidebarCollapseButton"] { display:block !important; visibility:visible !important; }
            [data-testid="stSidebarCollapseButton"] button { visibility:visible !important; }
            [data-testid="stSidebarCollapsedControl"],
            [data-testid="stExpandSidebarButton"] {
              display:block !important; visibility:visible !important; position:fixed !important; top:10px !important; left:10px !important;
              z-index:1000000 !important;
            }
            [data-testid="stSidebarCollapsedControl"] button,
            [data-testid="stExpandSidebarButton"],
            [data-testid="stExpandSidebarButton"] button {
              width:44px !important; height:44px !important; border-radius:10px !important;
              background:#172F4D !important; color:#FFFFFF !important; border:1px solid #2455A4 !important;
              box-shadow:0 6px 18px rgba(15,34,58,.22) !important;
            }
            [data-testid="stSidebarCollapsedControl"] button *,
            [data-testid="stExpandSidebarButton"],
            [data-testid="stExpandSidebarButton"] * {
              visibility:visible !important; color:#FFFFFF !important; fill:#FFFFFF !important;
            }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _logo_tag(filename):
    """Return an <img> tag (base64) for assets/<filename>, or '' if missing."""
    data_uri = _asset_data_uri(filename)
    if not data_uri:
        return ""
    return f'<img class="hero-logo" src="{data_uri}" alt="">'


def render_hero():
    # accepts left.png/jpg and right.png/jpg (first match wins)
    def pick(side):
        for ext in ("png", "jpg", "jpeg", "webp"):
            tag = _logo_tag(f"{side}.{ext}")
            if tag:
                return tag
        return ""

    left = pick("left")
    right = pick("right")
    st.markdown(
        f"""
        <div class="sjmcc-hero">
          <div class="hero-row">
            {left}
            <div class="hero-text">
              <span class="cross">✝</span>
              <h1>St Joseph Military Catholic Church, Lokoja</h1>
              <div class="rule"></div>
              <p>2026 Harvest Financial Management</p>
              <small>Account Statement &amp; Records System</small>
            </div>
            {right}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title):
    st.markdown(f'<div class="sjmcc-sec">{title}</div>', unsafe_allow_html=True)


def page_header(title, description, badge="2026 HARVEST"):
    st.markdown(
        f"""
        <header class="page-head">
          <div><span class="page-badge">{badge}</span><h1>{title}</h1><p>{description}</p></div>
          <span class="page-head-mark">✝</span>
        </header>
        """,
        unsafe_allow_html=True,
    )


def context_panel(number, title, copy):
    st.markdown(
        f'<aside class="context-panel"><span>{number}</span><h3>{title}</h3><p>{copy}</p></aside>',
        unsafe_allow_html=True,
    )


# =========================
# APP START
# =========================
st.set_page_config(
    page_title="SJMCC — 2026 Harvest Finance",
    page_icon="⛪",
    layout="wide",
    initial_sidebar_state="expanded",
)
inject_css()

# 1) App password gate
if not require_app_login():
    st.stop()

init_db_and_migrate()

# ---- enterprise application shell ----
with st.sidebar:
    side_logo = _asset_data_uri("left.png")
    side_logo_html = f'<img src="{side_logo}" alt="">' if side_logo else '<span class="side-mark">✝</span>'
    st.markdown(
        f"""
        <div class="side-brand">
          {side_logo_html}
          <div><strong>St Joseph</strong><small>Harvest Finance</small></div>
        </div>
        <div class="side-section-label">WORKSPACE</div>
        """,
        unsafe_allow_html=True,
    )
    page = st.radio(
        "Navigation",
        [
        "Summary / Statistics",
        "New Harvest Record",
        "Pledge Update",
        "New Compulsory Levy",
        "New Expense",
        "Downloads / View Data",
        "Admin Dashboard",
        "Admin Editor (Edit/Delete)",
        ],
        label_visibility="collapsed",
        key="nav_page",
    )
    if st.button("Log out", use_container_width=True):
        clear_authentication(st.session_state)
        st.rerun()
    st.markdown(
        '<div class="side-footer"><span>2026 Harvest</span><small>Account Statement &amp; Records System</small></div>',
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="workspace-eyebrow">ST JOSEPH MILITARY CATHOLIC CHURCH · LOKOJA</div>',
    unsafe_allow_html=True,
)

# -------------------------
# Summary / Statistics  (landing page)
# -------------------------
def naira(x):
    try:
        return f"₦{float(x):,.0f}"
    except Exception:
        return "₦0"


def light_chart(chart, height):
    """Apply the product's explicit light visualization theme."""
    return (
        chart.properties(height=height, background="#FFFFFF")
        .configure_view(stroke="#E1E7EF", fill="#FFFFFF")
        .configure_axis(
            labelColor="#526278", titleColor="#24334B", gridColor="#E6ECF3",
            domainColor="#CFD9E5", tickColor="#CFD9E5", labelFontSize=12,
            titleFontSize=12, titleFontWeight=600,
        )
        .configure_legend(
            labelColor="#24334B", titleColor="#24334B", orient="top",
            direction="horizontal", labelFontSize=12, symbolType="square",
        )
    )


if page == "Summary / Statistics":
    page_header("Financial overview", "A complete view of harvest income, obligations, expenses, and collection performance.")
    dfh = list_harvest_records(limit=50000)
    dfc = list_compulsory(limit=50000)
    dfe = list_expenses(limit=50000)

    h_amount = float(pd.to_numeric(dfh["Amount"], errors="coerce").fillna(0).sum()) if not dfh.empty else 0.0
    h_paid = float(pd.to_numeric(dfh["Amount Paid"], errors="coerce").fillna(0).sum()) if not dfh.empty else 0.0
    h_bal = h_amount - h_paid
    c_amount = float(pd.to_numeric(dfc["Amount"], errors="coerce").fillna(0).sum()) if not dfc.empty else 0.0
    e_amount = float(pd.to_numeric(dfe["Amount"], errors="coerce").fillna(0).sum()) if not dfe.empty else 0.0
    income = h_paid + c_amount
    net = income - e_amount

    n_records = int(len(dfh))
    n_contrib = int(dfh["Name"].nunique()) if not dfh.empty else 0
    n_paid = int((dfh["Status"] == "Paid").sum()) if not dfh.empty else 0
    n_unpaid = int((dfh["Status"] == "Unpaid").sum()) if not dfh.empty else 0

    section("Financial Position at a Glance")
    st.markdown(
        f"""
        <section class="financial-hero">
          <div class="net-position"><span>Net Balance</span><strong>{naira(net)}</strong><small>Income received less total expenses</small></div>
          <div class="financial-stack">
            <div><span>Total Income Received</span><strong>{naira(income)}</strong></div>
            <div><span>Total Expenses</span><strong>{naira(e_amount)}</strong></div>
            <div><span>Outstanding Pledges</span><strong>{naira(h_bal)}</strong></div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    a, b, c, d = st.columns(4)
    a.metric("Total Harvest Pledged", naira(h_amount))
    b.metric("Harvest Received", naira(h_paid))
    c.metric("Compulsory Levies", naira(c_amount))
    d.metric("Harvest Records", f"{n_records:,}")

    a, b, c, d = st.columns(4)
    a.metric("Unique Contributors", f"{n_contrib:,}")
    b.metric("Fully Paid", f"{n_paid:,}")
    c.metric("Unpaid / Pledged", f"{n_unpaid:,}")
    rate = (h_paid / h_amount * 100) if h_amount else 0
    d.metric("Collection Rate", f"{rate:.1f}%")

    # ---- Full professional report download ----
    section("Download Full Account Statement (Excel)")
    st.caption(
        "A professionally formatted, multi-sheet Excel workbook: an executive summary, "
        "a sheet for every harvest programme, a comprehensive combined sheet, plus "
        "compulsory levies and expenses — ready to present to stakeholders."
    )
    try:
        xlsx_bytes = build_excel_report(DB_PATH)
        st.download_button(
            "⬇️  Download Account Statement (.xlsx)",
            data=xlsx_bytes,
            file_name=REPORT_FILENAME,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
            use_container_width=True,
        )
    except Exception:
        st.error("Could not build the Excel report. Please contact an administrator.")

    if dfh.empty:
        st.info("No harvest records captured yet.")
    else:
        # ---- Charts ----
        section("Harvest by Programme / Activity")
        byact = dfh.copy()
        byact["Amount"] = pd.to_numeric(byact["Amount"], errors="coerce").fillna(0)
        byact["Amount Paid"] = pd.to_numeric(byact["Amount Paid"], errors="coerce").fillna(0)
        agg = byact.groupby("Activity").agg(
            Pledged=("Amount", "sum"),
            Received=("Amount Paid", "sum"),
            Records=("id", "count"),
        )
        agg["Balance"] = agg["Pledged"] - agg["Received"]
        agg = agg.sort_values("Pledged", ascending=False)

        chart_data = (
            agg.reset_index()
            .melt(
                id_vars=["Activity"], value_vars=["Pledged", "Received"],
                var_name="Financial measure", value_name="Amount",
            )
        )
        chart_data["Full amount"] = chart_data["Amount"].map(naira)
        activity_order = agg.index.tolist()
        programme_chart = (
            alt.Chart(chart_data)
            .mark_bar(cornerRadiusEnd=4, height=9)
            .encode(
                y=alt.Y(
                    "Activity:N", sort=activity_order, title=None,
                    axis=alt.Axis(labelLimit=310, labelPadding=9, ticks=False),
                ),
                x=alt.X(
                    "Amount:Q", title="Amount (Naira)",
                    axis=alt.Axis(
                        tickCount=6,
                        labelExpr="datum.value == 0 ? '₦0' : '₦' + format(datum.value / 1000000, '.1~f') + 'M'",
                    ),
                ),
                yOffset=alt.YOffset("Financial measure:N"),
                color=alt.Color(
                    "Financial measure:N", title=None,
                    scale=alt.Scale(domain=["Pledged", "Received"], range=["#79B8EA", "#2455A4"]),
                ),
                tooltip=[
                    alt.Tooltip("Activity:N", title="Programme / Activity"),
                    alt.Tooltip("Financial measure:N", title="Measure"),
                    alt.Tooltip("Full amount:N", title="Amount"),
                ],
            )
        )
        chart_height = max(390, len(activity_order) * 34)
        st.altair_chart(light_chart(programme_chart, chart_height), use_container_width=True, theme=None)

        render_activity_summary_table(agg)

        cols = st.columns(2)
        with cols[0]:
            section("By Payment Mode")
            bymode = byact.groupby("Payment Mode").agg(
                Pledged=("Amount", "sum"), Received=("Amount Paid", "sum"),
                Records=("id", "count"),
            ).sort_values("Pledged", ascending=False)
            bymode_data = bymode.reset_index()
            mode_chart = (
                alt.Chart(bymode_data).mark_bar(color="#2455A4", cornerRadiusEnd=4)
                .encode(
                    x=alt.X(
                        "Received:Q", title="Amount received",
                        axis=alt.Axis(labelExpr="datum.value == 0 ? '₦0' : '₦' + format(datum.value / 1000000, '.1~f') + 'M'"),
                    ),
                    y=alt.Y("Payment Mode:N", sort="-x", title=None),
                    tooltip=[alt.Tooltip("Payment Mode:N"), alt.Tooltip("Received:Q", format=",.0f")],
                )
            )
            st.altair_chart(light_chart(mode_chart, 250), use_container_width=True, theme=None)
            mshow = bymode.copy()
            mshow["Pledged"] = mshow["Pledged"].map(naira)
            mshow["Received"] = mshow["Received"].map(naira)
            render_table(mshow, hide_index=False)
        with cols[1]:
            section("Payment Status")
            status_counts = dfh["Status"].value_counts()
            status_data = status_counts.rename_axis("Status").reset_index(name="Records")
            status_chart = (
                alt.Chart(status_data).mark_bar(color="#79B8EA", cornerRadiusEnd=4)
                .encode(
                    x=alt.X("Records:Q", title="Records", axis=alt.Axis(tickMinStep=1)),
                    y=alt.Y("Status:N", sort="-x", title=None),
                    tooltip=["Status:N", "Records:Q"],
                )
            )
            st.altair_chart(light_chart(status_chart, 250), use_container_width=True, theme=None)
            if not dfc.empty:
                st.markdown("**Compulsory Levies by Category**")
                cc = dfc.copy()
                cc["Amount"] = pd.to_numeric(cc["Amount"], errors="coerce").fillna(0)
                ccg = cc.groupby("Category").agg(Records=("id", "count"), Amount=("Amount", "sum"))
                ccg["Amount"] = ccg["Amount"].map(naira)
                render_table(ccg, hide_index=False)

        if not dfe.empty:
            section("Expenses Summary")
            st.metric("Total Expenses", naira(e_amount))
            render_table(dfe)

    section("Financial Records & Individual Datasets")
    st.caption("Review the original source records or download each dataset in CSV format.")
    tab1, tab2, tab3 = st.tabs(["Harvest Records", "Compulsory", "Expenses"])
    with tab1:
        render_table(dfh)
        st.download_button("Download Harvest CSV", df_to_csv_bytes(dfh), "harvest_records.csv", "text/csv")
    with tab2:
        render_table(dfc)
        st.download_button("Download Compulsory CSV", df_to_csv_bytes(dfc), "compulsory_contributions.csv", "text/csv")
    with tab3:
        render_table(dfe)
        st.download_button("Download Expenses CSV", df_to_csv_bytes(dfe), "expenses.csv", "text/csv")

# -------------------------
# New Harvest Record
# -------------------------
elif page == "New Harvest Record":
    page_header("New Harvest Record", "Capture a harvest contribution while retaining the established payment workflow.", "INCOME MANAGEMENT")

    guide, workspace = st.columns([0.34, 0.66], gap="large")
    with guide:
        context_panel("01", "Contributor details", "Record the contributor, programme and payment information. Required fields are marked with an asterisk.")
    with workspace:
      with st.form("harvest_form", clear_on_submit=True):
        identity_a, identity_b = st.columns(2)
        with identity_a:
            name = st.text_input("Name *")
        with identity_b:
            phone = st.text_input("Phone Number *")
        activity = st.selectbox("Harvest Activity *", HARVEST_ACTIVITIES)

        if activity == "Seed Sowing":
            seed_cat = st.selectbox("Seed Sowing Category *", [x for x in SEED_SOWING_LEVELS if x != ""])
        else:
            seed_cat = st.selectbox("Seed Sowing Category", SEED_SOWING_LEVELS, index=0)

        pay_mode = st.selectbox("Payment Mode *", PAYMENT_MODES)
        amount = st.number_input("Amount *", min_value=0, step=100, value=0)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not name.strip() or not phone.strip():
            st.error("Name and Phone Number are required.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            insert_harvest_record(name, phone, activity, seed_cat, pay_mode, amount)
            st.success("Saved ✅")

# -------------------------
# Pledge Update
# -------------------------
elif page == "Pledge Update":
    page_header("Pledge Update (Redeem Pledges)", "Find a contributor record and apply a payment to its outstanding pledge.", "PLEDGE MANAGEMENT")

    df = list_harvest_records(limit=50000)
    if df.empty:
        st.warning("No harvest records yet.")
    else:
        search = st.text_input("Search (Name or Phone)", placeholder="Type a name or phone number")
        q = (search or "").strip().lower()
        pledge_records = df[(df["Payment Mode"] == "Pledge") & (df["Balance"] > 0)].copy()
        filtered = pledge_records if not q else pledge_records[
            pledge_records["Name"].str.lower().str.contains(q, na=False)
            | pledge_records["Phone"].astype(str).str.lower().str.contains(q, na=False)
        ].copy()

        st.write(f"Matches: {len(filtered)}")

        options = []
        id_map = {}
        for _, r in filtered.head(300).iterrows():
            rid = int(r["id"])
            label = f"Id {rid} | {r['Name']} | {r.get('Phone','')} | Mode: {r['Payment Mode']} | Balance: {r['Balance']} | Status: {r['Status']}"
            options.append(label)
            id_map[label] = rid

        if options:
            picked = st.selectbox("Select record to update", options)
            rid = id_map[picked]

            row = df[df["id"] == rid].iloc[0]
            st.info(
                f"Amount: {row['Amount']} | Amount Paid: {row['Amount Paid']} | Balance: {row['Balance']} | Status: {row['Status']} | Mode: {row['Payment Mode']}"
            )

            outstanding = float(row["Balance"])
            add_now = st.number_input(
                "Add Payment Now", min_value=0.0, max_value=outstanding, step=100.0, value=0.0
            )
            if st.button("Update Amount Paid"):
                if add_now <= 0:
                    st.error("Enter an amount greater than 0.")
                else:
                    try:
                        new_paid = update_amount_paid_add(rid, add_now)
                        st.success(f"Updated ✅ New Amount Paid = {new_paid}")
                    except ValueError as exc:
                        st.error(str(exc))
        else:
            st.warning("No matching records found.")

# -------------------------
# New Compulsory Levy
# -------------------------
elif page == "New Compulsory Levy":
    page_header("New Compulsory Levy", "Record a compulsory contribution against the appropriate contributor category.", "CONTRIBUTIONS")

    guide, workspace = st.columns([0.34, 0.66], gap="large")
    with guide:
        context_panel("02", "Levy details", "Capture the contributor identity, applicable category and received amount.")
    with workspace:
      with st.form("compulsory_form", clear_on_submit=True):
        name = st.text_input("Name *")
        phone = st.text_input("Phone Number *")
        cat = st.selectbox("Category *", COMPULSORY_CATEGORIES)
        amount = st.number_input("Amount *", min_value=0, step=100, value=0)
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not name.strip() or not phone.strip():
            st.error("Name and Phone Number are required.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            insert_compulsory(name, phone, cat, amount)
            st.success("Saved ✅")

# -------------------------
# New Expense
# -------------------------
elif page == "New Expense":
    page_header("New Expense", "Capture an approved harvest expense with its date and authorising officer.", "EXPENSE MANAGEMENT")

    guide, workspace = st.columns([0.34, 0.66], gap="large")
    with guide:
        context_panel("03", "Expense details", "Record the description, amount and approval information for this expense.")
        use_auto_date = st.checkbox("Use automatic date (today)", value=True)

    with workspace, st.form("expense_form", clear_on_submit=True):
        exp_date = None
        if not use_auto_date:
            exp_date = st.date_input("Date *", value=date.today())

        desc = st.text_input("Description *")
        amount = st.number_input("Amount *", min_value=0, step=100, value=0)
        approved = st.text_input("Approved by *")
        submitted = st.form_submit_button("Submit")

    if submitted:
        if not desc.strip() or not approved.strip():
            st.error("Description and Approved by are required.")
        elif amount <= 0:
            st.error("Amount must be greater than 0.")
        else:
            insert_expense(use_auto_date, exp_date, desc, amount, approved)
            st.success("Saved ✅")

# -------------------------
# Downloads / View Data
# -------------------------
elif page == "Downloads / View Data":
    page_header("Downloads / View Data", "Review source records and prepare existing financial datasets for download.", "REPORTING")
    section("Full Account Statement (Excel)")
    st.caption(
        "Professionally formatted workbook for stakeholders — executive summary, one sheet "
        "per harvest programme, a comprehensive combined sheet, compulsory levies and expenses."
    )
    try:
        st.download_button(
            "⬇️  Download Account Statement (.xlsx)",
            data=build_excel_report(DB_PATH),
            file_name=REPORT_FILENAME,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )
    except Exception:
        st.error("Could not build the Excel report. Please contact an administrator.")

    section("Individual Datasets (CSV)")
    tab1, tab2, tab3 = st.tabs(["Harvest Records", "Compulsory", "Expenses"])

    with tab1:
        dfh = list_harvest_records(limit=50000)
        render_table(dfh)
        st.download_button("Download Harvest CSV", df_to_csv_bytes(dfh), "harvest_records.csv", "text/csv")

    with tab2:
        dfc = list_compulsory(limit=50000)
        render_table(dfc)
        st.download_button("Download Compulsory CSV", df_to_csv_bytes(dfc), "compulsory_contributions.csv", "text/csv")

    with tab3:
        dfe = list_expenses(limit=50000)
        render_table(dfe)
        st.download_button("Download Expenses CSV", df_to_csv_bytes(dfe), "expenses.csv", "text/csv")

# -------------------------
# Admin Dashboard (requires ADMIN password)
# -------------------------
elif page == "Admin Dashboard":
    if not require_admin_login():
        st.stop()

    page_header("Admin Dashboard (Overview)", "Filter and inspect the complete administrative financial position.", "ADMINISTRATION")

    dfh = list_harvest_records(limit=50000)
    dfe = list_expenses(limit=50000)

    if dfh.empty:
        st.warning("No harvest records yet.")
    else:
        dfh["_date"] = pd.to_datetime(dfh["Date"], errors="coerce").dt.date
        min_d = dfh["_date"].min() or date.today()
        max_d = dfh["_date"].max() or date.today()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            start = st.date_input("Start Date", value=min_d)
        with c2:
            end = st.date_input("End Date", value=max_d)
        with c3:
            activity = st.selectbox("Activity", ["All"] + sorted(dfh["Activity"].dropna().unique().tolist()))
        with c4:
            mode = st.selectbox("Payment Mode", ["All"] + sorted(dfh["Payment Mode"].dropna().unique().tolist()))

        status = st.selectbox("Status", ["All", "Paid", "Unpaid"])

        filt = dfh[(dfh["_date"] >= start) & (dfh["_date"] <= end)].copy()
        if activity != "All":
            filt = filt[filt["Activity"] == activity]
        if mode != "All":
            filt = filt[filt["Payment Mode"] == mode]
        if status != "All":
            filt = filt[filt["Status"] == status]

        total_amount = float(pd.to_numeric(filt["Amount"], errors="coerce").fillna(0).sum())
        total_paid = float(pd.to_numeric(filt["Amount Paid"], errors="coerce").fillna(0).sum())
        total_balance = float(pd.to_numeric(filt["Balance"], errors="coerce").fillna(0).sum())

        count_all = int(len(filt))
        count_paid = int((filt["Status"] == "Paid").sum())
        count_unpaid = int((filt["Status"] == "Unpaid").sum())

        section("Summary (Filtered)")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Records", f"{count_all:,}")
        m2.metric("Total Amount", f"₦{total_amount:,.0f}")
        m3.metric("Total Paid", f"₦{total_paid:,.0f}")
        m4.metric("Total Balance", f"₦{total_balance:,.0f}")
        m5, m6 = st.columns(2)
        m5.metric("Paid", f"{count_paid:,}")
        m6.metric("Unpaid", f"{count_unpaid:,}")

        section("Breakdown")
        colA, colB = st.columns(2)
        with colA:
            st.write("By Payment Mode")
            render_table(filt["Payment Mode"].value_counts().rename("Count"), hide_index=False)
        with colB:
            st.write("By Activity")
            render_table(filt["Activity"].value_counts().head(15).rename("Count"), hide_index=False)

        st.write("### Expenses Summary")
        if dfe.empty:
            st.info("No expenses yet.")
        else:
            dfe["_date"] = pd.to_datetime(dfe["Date"], errors="coerce").dt.date
            exp_f = dfe[(dfe["_date"] >= start) & (dfe["_date"] <= end)].copy()
            exp_total = float(pd.to_numeric(exp_f["Amount"], errors="coerce").fillna(0).sum())
            st.write(f"- Total Expenses in range: **{exp_total:,.0f}**")
            render_table(exp_f.drop(columns=["_date"]))

        st.write("### Filtered Harvest Records")
        render_table(filt.drop(columns=["_date"]))
        st.download_button(
            "Download Filtered Harvest CSV",
            df_to_csv_bytes(filt.drop(columns=["_date"])),
            "harvest_filtered.csv",
            "text/csv",
        )

# -------------------------
# Admin Editor (requires ADMIN password) — SEARCH POPUP STYLE
# -------------------------
elif page == "Admin Editor (Edit/Delete)":
    if not require_admin_login():
        st.stop()

    page_header("Admin Editor (Search → Edit → Save)", "Search all financial records, then correct or delete one exact entry.", "RECORD CONTROL")

    if notice := st.session_state.pop("editor_notice", None):
        st.success(notice)

    harvest_df = list_harvest_records(limit=50000)
    compulsory_df = list_compulsory(limit=50000)
    expense_df = list_expenses(limit=50000)

    search_rows = []
    for _, record in harvest_df.iterrows():
        module = "Pledge Updates" if record.get("Payment Mode") == "Pledge" else "Harvest Records"
        search_rows.append({
            "_table": "harvest_records", "_id": int(record["id"]), "Module": module,
            "Reference": f"H-{int(record['id'])}", "Date": record.get("Date", ""),
            "Contributor / Description": record.get("Name", ""), "Phone": record.get("Phone", ""),
            "Category": record.get("Activity", ""), "Amount": record.get("Amount", 0),
            "Status": record.get("Status", ""),
        })
    for _, record in compulsory_df.iterrows():
        search_rows.append({
            "_table": "compulsory_contributions", "_id": int(record["id"]), "Module": "Compulsory Levies",
            "Reference": f"L-{int(record['id'])}", "Date": record.get("Date", ""),
            "Contributor / Description": record.get("Name", ""), "Phone": record.get("Phone", ""),
            "Category": record.get("Category", ""), "Amount": record.get("Amount", 0), "Status": "Received",
        })
    for _, record in expense_df.iterrows():
        search_rows.append({
            "_table": "expenses", "_id": int(record["id"]), "Module": "Expenses",
            "Reference": f"E-{int(record['id'])}", "Date": record.get("Date", ""),
            "Contributor / Description": record.get("Description", ""), "Phone": "",
            "Category": record.get("Approved By", ""), "Amount": record.get("Amount", 0), "Status": "Paid",
        })

    records = pd.DataFrame(search_rows)
    section("Search Financial Records")
    search_col, module_col = st.columns([0.7, 0.3])
    with search_col:
        query = st.text_input(
            "Search by contributor, record ID/reference, phone, date, activity or category",
            placeholder="e.g. Philip, H-42, 2026-06-01, Seed Sowing",
        )
    with module_col:
        module_filter = st.selectbox(
            "Record category", ["All Records", "Harvest Records", "Pledge Updates", "Compulsory Levies", "Expenses"]
        )

    matches = records.copy()
    if module_filter != "All Records" and not matches.empty:
        matches = matches[matches["Module"] == module_filter]
    if query.strip() and not matches.empty:
        searchable = ["Reference", "Date", "Contributor / Description", "Phone", "Category", "Module", "Status"]
        combined = matches[searchable].fillna("").astype(str).agg(" ".join, axis=1)
        matches = matches[combined.str.contains(query.strip(), case=False, regex=False)]

    if records.empty:
        st.warning("No financial records are available.")
        st.stop()
    if matches.empty:
        st.warning("No matching records. Try a different name, ID, reference, date, or category.")
        st.stop()

    st.caption(f"{len(matches):,} matching record(s). Select one exact record to edit or delete.")
    render_table(matches.drop(columns=["_table", "_id"]).head(500))

    option_map = {}
    for _, record in matches.head(500).iterrows():
        label = (
            f"{record['Reference']} | {record['Module']} | "
            f"{record['Contributor / Description']} | {record['Date']} | ₦{float(record['Amount']):,.0f}"
        )
        option_map[label] = (record["_table"], int(record["_id"]))
    picked = st.selectbox("Select the exact record", list(option_map))
    table_choice, rid = option_map[picked]

    source_df = {
        "harvest_records": harvest_df,
        "compulsory_contributions": compulsory_df,
        "expenses": expense_df,
    }[table_choice]
    row = source_df[source_df["id"] == rid].iloc[0].to_dict()

    section("Selected Record")
    st.info(picked)

    st.write("### Edit Record (Auto-filled)")

    if table_choice == "harvest_records":
        with st.form("edit_harvest"):
            created_date = st.text_input("Date (YYYY-MM-DD)", value=str(row.get("Date", "")))
            name = st.text_input("Name", value=str(row.get("Name", "")))
            phone = st.text_input("Phone", value=str(row.get("Phone", "")))

            activity = st.selectbox(
                "Activity", HARVEST_ACTIVITIES,
                index=HARVEST_ACTIVITIES.index(row.get("Activity")) if row.get("Activity") in HARVEST_ACTIVITIES else 0,
            )
            seed = st.selectbox(
                "Seed Category", SEED_SOWING_LEVELS,
                index=SEED_SOWING_LEVELS.index(row.get("Seed Category")) if row.get("Seed Category") in SEED_SOWING_LEVELS else 0,
            )
            paymode = st.selectbox(
                "Payment Mode", PAYMENT_MODES,
                index=PAYMENT_MODES.index(row.get("Payment Mode")) if row.get("Payment Mode") in PAYMENT_MODES else 0,
            )

            amount = st.number_input("Amount", min_value=0.0, step=100.0, value=float(row.get("Amount") or 0))
            amount_paid = st.number_input("Amount Paid", min_value=0.0, step=100.0, value=float(row.get("Amount Paid") or 0))
            save = st.form_submit_button("Save Changes")

        if save:
            try:
                admin_update_harvest(rid, created_date, name, phone, activity, seed, paymode, amount, amount_paid)
                st.session_state["editor_notice"] = f"{picked} was updated. Financial totals have been recalculated."
                st.rerun()
            except (ValueError, PermissionError) as exc:
                st.error(str(exc))

    elif table_choice == "compulsory_contributions":
        with st.form("edit_compulsory"):
            created_date = st.text_input("Date (YYYY-MM-DD)", value=str(row.get("Date", "")))
            name = st.text_input("Name", value=str(row.get("Name", "")))
            phone = st.text_input("Phone", value=str(row.get("Phone", "")))
            category = st.selectbox(
                "Category", COMPULSORY_CATEGORIES,
                index=COMPULSORY_CATEGORIES.index(row.get("Category")) if row.get("Category") in COMPULSORY_CATEGORIES else 0,
            )
            amount = st.number_input("Amount", min_value=0.0, step=100.0, value=float(row.get("Amount") or 0))
            save = st.form_submit_button("Save Changes")

        if save:
            try:
                admin_update_compulsory(rid, created_date, name, phone, category, amount)
                st.session_state["editor_notice"] = f"{picked} was updated. Financial totals have been recalculated."
                st.rerun()
            except (ValueError, PermissionError) as exc:
                st.error(str(exc))

    else:
        with st.form("edit_expense"):
            exp_date = st.text_input("Date (YYYY-MM-DD)", value=str(row.get("Date", "")))
            desc = st.text_input("Description", value=str(row.get("Description", "")))
            amount = st.number_input("Amount", min_value=0.0, step=100.0, value=float(row.get("Amount") or 0))
            approved = st.text_input("Approved By", value=str(row.get("Approved By", "")))
            save = st.form_submit_button("Save Changes")

        if save:
            try:
                admin_update_expense(rid, exp_date, desc, amount, approved)
                st.session_state["editor_notice"] = f"{picked} was updated. Financial totals have been recalculated."
                st.rerun()
            except (ValueError, PermissionError) as exc:
                st.error(str(exc))

    st.write("### Delete Record")

    @st.dialog("Confirm record deletion")
    def confirm_record_deletion(table_name, record_id, record_label):
        st.error("You are about to permanently delete this exact financial record:")
        st.write(record_label)
        with st.form(f"delete_{table_name}_{record_id}"):
            confirmed = st.checkbox("I confirm that this is the record I intend to delete.")
            delete_submitted = st.form_submit_button("Delete selected record", type="primary")
        if delete_submitted:
            if not confirmed:
                st.warning("Confirm the exact record before deleting it.")
            else:
                try:
                    admin_delete(table_name, record_id)
                    st.session_state["editor_notice"] = (
                        f"{record_label} was deleted. Other contributor records were preserved and totals were recalculated."
                    )
                    st.rerun()
                except (ValueError, PermissionError) as exc:
                    st.error(str(exc))

    if st.button("Delete this record", type="secondary"):
        confirm_record_deletion(table_choice, rid, picked)
