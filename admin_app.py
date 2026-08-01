from datetime import datetime
import json
import os
import random
import string
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st

# Shared File Paths
METRICS_FILE = ".vektor_admin_metrics.json"
PINS_FILE = ".vektor_activation_pins.json"

st.set_page_config(page_title="Vektor AI Portal", layout="wide")


def load_json(filepath):
  if os.path.exists(filepath):
    try:
      with open(filepath, "r") as f:
        return json.load(f)
    except Exception:
      return {}
  return {}


def save_json(filepath, data):
  with open(filepath, "w") as f:
    json.dump(data, f)


def generate_pin():
  p1 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
  p2 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
  return f"VK-{p1}-{p2}"


# Sidebar Navigation to switch between Main App and Admin Portal
st.sidebar.title("Navigation")
app_mode = st.sidebar.selectbox("Choose Portal", ["Main App", "Admin Portal"])

if app_mode == "Admin Portal":
  st.title("🛡️ Vektor AI - Master Admin Portal")

  st.header("👥 User Activity & Security Monitor")
  users_data = load_json(METRICS_FILE)
  if users_data:
    df = pd.DataFrame.from_dict(users_data, orient="index")
    st.dataframe(df, use_container_width=True)
  else:
    st.info("No users registered yet.")

  st.write("---")

  st.header("🔑 Generate Activation Codes")
  col1, col2 = st.columns(2)

  with col1:
    days_to_add = st.number_input(
        "Days of Access to Grant:", min_value=1, value=30
    )
    is_lifetime = st.checkbox("Make it a Lifetime/Forever Code?")

    if st.button("Generate New Activation PIN", type="primary"):
      new_pin = generate_pin()
      pins_db = load_json(PINS_FILE)

      pins_db[new_pin] = {
          "status": "Unused",
          "created_at": datetime.now(ZoneInfo("Africa/Lagos")).strftime(
              "%Y-%m-%d %H:%M:%S"
          ),
          "days_allotted": int(days_to_add),
          "is_forever": bool(is_lifetime),
          "claimed_by": None,
      }
      save_json(PINS_FILE, pins_db)
      st.success(f"Successfully generated PIN: **{new_pin}**")

  with col2:
    st.subheader("Existing PINs")
    pins_data = load_json(PINS_FILE)
    if pins_data:
      pins_df = pd.DataFrame.from_dict(pins_data, orient="index")
      st.dataframe(pins_df, use_container_width=True)
    else:
      st.info("No pins generated yet.")

else:
  # ==========================================
  # MAIN APP PORTAL
  # ==========================================
  st.title("🚀 Vektor AI - Main App")

  # Initialize session state for authentication if not present
  if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

  if not st.session_state.authenticated:
    st.subheader("🔑 Apply New Strategic License Token Override")
    user_pin = st.text_input(
        "Input Generated Administration Activation Key (PIN):"
    ).strip()

    if st.button("🔒 Submit Registration Renewal Block", type="primary"):
      pins_db = load_json(PINS_FILE)

      if user_pin in pins_db:
        pin_info = pins_db[user_pin]
        if pin_info["status"] == "Unused":
          # Mark pin as used
          pin_info["status"] = "Used"
          save_json(PINS_FILE, pins_db)

          # Grant authentication
          st.session_state.authenticated = True
          st.success("Activation successful! Loading app...")
          st.rerun()
        else:
          st.error(
              "Specified verification key index string is invalid or already"
              " consumed."
          )
      else:
        st.error(
            "Specified verification key index string is invalid or already"
            " consumed."
        )
  else:
    st.success("Welcome! You are authenticated and have access to the app.")
    if st.button("Log Out"):
      st.session_state.authenticated = False
      st.rerun()
