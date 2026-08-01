from datetime import datetime
import json
import os
import random
import string
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st

# File Paths (Must match the main app)
METRICS_FILE = ".vektor_admin_metrics.json"
PINS_FILE = ".vektor_activation_pins.json"

st.set_page_config(page_title="Vektor Admin Portal", layout="wide")


def load_json(filepath):
  if os.path.exists(filepath):
    try:
      with open(filepath, "r") as f:
        return json.load(f)
    except:
      return {}
  return {}


def save_json(filepath, data):
  with open(filepath, "w") as f:
    json.dump(data, f)


def generate_pin():
  # Generates a random pin like VK-A1B2-C3D4
  p1 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
  p2 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
  return f"VK-{p1}-{p2}"


st.title("🛡️ Vektor AI - Master Admin Portal")

# ==========================================
# 1. USER TRACKING & SECURITY DASHBOARD
# ==========================================
st.header("👥 User Activity & Security Monitor")
users_data = load_json(METRICS_FILE)

if users_data:
  # Convert JSON to a readable table
  df = pd.DataFrame.from_dict(users_data, orient="index")
  st.dataframe(
      df[[
          "username",
          "status",
          "payment_status",
          "registered_at",
          "last_active",
          "license_expiry",
      ]],
      use_container_width=True,
  )
else:
  st.info("No users registered yet.")

st.write("---")

# ==========================================
# 2. ACTIVATION CODE GENERATOR
# ==========================================
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
        "days_allotted": days_to_add,
        "is_forever": is_lifetime,
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
