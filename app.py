"""Streamlit front-end for Age & Era Calculator."""
from __future__ import annotations

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import streamlit as st
from datetime import date, datetime
import time

from logic import (
    compute_periods,
    decade_label,
    generate_summary,
    get_generation,
    get_star_sign,
    parse_birthdate,
)

# Apply custom styles
st.set_page_config(
    page_title="Age & Era Calculator", 
    page_icon="📅", 
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "About": "Calculate your cultural eras based on birth year."
    }
)

# Set dark theme
st.markdown("""
<style>
    .main-header {text-align: center; margin-bottom: 1rem;}
    .stButton button {width: 100%}
    .stRadio > div {flex-direction: row; justify-content: center;}
    .results-section {margin-top: 2rem; padding: 1rem; border-radius: 5px;}
    .stDateInput > div > div > input {max-width: 100%;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-header'>📅 Age & Era Calculator</h1>", unsafe_allow_html=True)

# Initialize session state for input type if not exists
if 'input_type' not in st.session_state:
    st.session_state.input_type = "Date of Birth"

# Function to handle radio button change
def change_input_type():
    st.session_state.input_type = st.session_state.new_input_type

# Input selection with horizontal radio buttons
st.radio(
    "Choose input type:",
    options=["Date of Birth", "Age"],
    key="new_input_type",
    on_change=change_input_type,
    horizontal=True,
    index=0 if st.session_state.input_type == "Date of Birth" else 1
)

with st.form("input_form"):
    if st.session_state.input_type == "Date of Birth":
        min_date = date(1900, 1, 1)
        max_date = date.today()
        dob_input = st.date_input(
            "Date of birth", 
            value=date(1995, 1, 1),
            min_value=min_date,
            max_value=max_date,
            format="YYYY-MM-DD"
        )
        age_input = None
    else:
        age_input = st.number_input("Age (years)", min_value=1, max_value=129, step=1, format="%d")
        dob_input = None

    country = st.text_input("Country of upbringing (optional)")
    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        if st.session_state.input_type == "Date of Birth":
            birth = parse_birthdate(dob=dob_input)
        else:
            birth = parse_birthdate(age=int(age_input))
    except ValueError as exc:
        st.error(str(exc))
    else:
        child_start, child_end, teen_start, teen_end, ya_start, ya_end = compute_periods(birth)

        st.subheader("Results")

        st.markdown(
            f"**Childhood years:** {child_start.year} – {child_end.year} "
            f"({decade_label(child_start.year)})"
        )
        st.markdown(
            f"**Teenage years:** {teen_start.year} – {teen_end.year} "
            f"({decade_label(teen_start.year)})"
        )
        st.markdown(
            f"**Young adult years:** {ya_start.year} – {ya_end.year} "
            f"({decade_label(ya_start.year)})"
        )
        st.markdown(f"**Star sign:** {get_star_sign(birth)}")
        st.markdown(f"**Generation:** {get_generation(birth.year)}")

        # LLM summary (optional)
        with st.spinner("Generating cultural summary..."):
            summary = generate_summary(
                teen_start=teen_start.year,
                teen_end=teen_end.year,
                ya_start=ya_start.year,
                ya_end=ya_end.year,
                country=country or "their country",
                # Include childhood years in the prompt as well
                child_start=child_start.year,
                child_end=child_end.year,
            )
        st.markdown("---")
        st.subheader("Cultural Snapshot")
        st.markdown(summary)

        # Shareable link
        params = {
            "dob": birth.isoformat(),
            "country": country,
        }
        # Create shareable link
        st.markdown("---")
        st.subheader("Share this link")
        timestamp = int(time.time())
        shareable_id = f"{birth.year}-{birth.month}-{birth.day}-{timestamp}"
        
        # Avoid using the deprecated experimental_get_query_params
        share_placeholder = f"unique-id-{shareable_id}"
        st.text_input("Share ID", value=share_placeholder, disabled=True)
