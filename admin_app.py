from datetime import datetime
import os
import random
import string
from zoneinfo import ZoneInfo
import pandas as pd
import requests
import streamlit as st

# JSONBin Configuration (Replace with your actual Bin ID and API Key)
JSONBIN_BIN_ID = "YOUR_BIN_ID_HERE"
JSONBIN_API_KEY = "YOUR_MASTER_KEY_HERE"

HEADERS = {
    "Content-Type": "application/json",
    "X-Master-Key": JSONBIN_API_KEY,
}


def load_cloud_pins():
  url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
  try:
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
      # JSONBin wraps data inside a "record" dictionary
      return response.json().get("record", {})
  except Exception:
    pass
  return {}


def save_cloud_pins(data):
  url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
  try:
    requests.put(url, json=data, headers=HEADERS)
  except Exception:
    pass


def generate_pin():
  p1 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
  p2 = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
  return f"VK-{p1}-{p2}"


st.title("🛡️ Vektor AI - Master Admin Portal")

st.header("🔑 Generate Activation Codes")
col1, col2 = st.columns(2)

with col1:
  days_to_add = st.number_input(
      "Days of Access to Grant:", min_value=1, value=30
  )
  is_lifetime = st.checkbox("Make it a Lifetime/Forever Code?")

  if st.button("Generate New Activation PIN", type="primary"):
    new_pin = generate_pin()
    pins_db = load_cloud_pins()

    pins_db[new_pin] = {
        "status": "Unused",
        "created_at": datetime.now(ZoneInfo("Africa/Lagos")).strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "days_allotted": int(days_to_add),
        "is_forever": bool(is_lifetime),
        "claimed_by": None,
    }
    save_cloud_pins(pins_db)
    st.success(f"Successfully generated PIN: **{new_pin}**")

with col2:
  st.subheader("Existing PINs")
  pins_data = load_cloud_pins()
  if pins_data:
    pins_df = pd.DataFrame.from_dict(pins_data, orient="index")
    st.dataframe(pins_df, use_container_width=True)
  else:
    st.info("No pins generated yet.")
