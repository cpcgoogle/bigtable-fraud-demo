# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import pandas as pd
from numpy.random import default_rng as rng
import sys

# Assume bt_utils and read_bt_row are set up correctly
# For this example, we will define a placeholder function for bt_read.return_df()
# so the code runs without external files.
# --- PLACEHOLDER CODE START ---
def return_df():
    data = {
        'timestamp': pd.to_datetime(['2025-10-25 10:00:00', '2025-10-24 15:30:00', '2025-10-23 09:15:00']),
        'amount': [150.75, 5.00, 2000.99],
        'merchant': ['Fictional Merchant 1', 'Small Coffee Shop', 'Travel Agency XYZ'],
        'anomaly_score': [0.12, 0.01, 0.95],
        'agent_decision': ['Low Risk', 'Safe', 'High Risk - Flagged']
    }
    df = pd.DataFrame(data)
    return df

# If you need to keep your import structure, ensure these files are accessible:
# sys.path.insert(1, 'bt_utils')
# import read_bt_row as bt_read
# --- PLACEHOLDER CODE END ---

st.set_page_config(layout="wide")

st.image("https://storage.mtls.cloud.google.com/crosbie/btfraud.png", width=650)
st.title("Enter Credit Card Transaction")

# Step 1: Initialize Session State Variables 
if 'submitted_transaction' not in st.session_state:
    st.session_state.submitted_transaction = False
if 'agent_ran' not in st.session_state:
    st.session_state.agent_ran = False
# Store the transaction details to persist after rerun
if 'transaction_data' not in st.session_state:
    st.session_state.transaction_data = {}

# Variables defined outside the form need to be initialized for the first run
credit_card_str = ''
amount = 0.0
category = 'food_dining'
merchant = ''


# --- 2. First Form Definition: transaction_form ---
with st.form("transaction_form"):
    # --- Form Fields ---
    credit_card_str = st.text_input("Credit Card Number", help="Enter the numeric credit card number.")
    
    credit_card_validated = None
    if credit_card_str:
        if credit_card_str.isdigit():
            credit_card_validated = int(credit_card_str)
        else:
            st.error("Invalid input: Credit card number must contain only digits.")

    amount = st.number_input("Amount", format="%.2f", step=0.01, help="Enter the transaction amount.")

    category = st.selectbox(
        "Category",
        ("food_dining", "personal_care", "entertainment", "shopping_pos", "kids_pets", "health_fitness", "grocery_pos", "misc_net", "travel", "shopping_net", "gas_transport", "grocery_net", "home", "misc_pos"),
    )

    merchant = st.text_input("Merchant", help="Enter the merchant name.")

    submitted = st.form_submit_button("Submit to Bigtable")

# --- 3. Logic for First Submission ---
if submitted:
    # Set state variable to show the next UI sections
    st.session_state.submitted_transaction = True
    st.session_state.agent_ran = False # Reset agent analysis display
    
    # Store data in session state for display after rerun
    st.session_state.transaction_data = {
        'credit_card_str': credit_card_str,
        'amount': amount,
        'category': category,
        'merchant': merchant
    }
    # Optional: Use st.rerun() to immediately update the page
    # st.rerun() 

# --- 4. Display Transaction Results and Second Button (controlled by session state) ---
if st.session_state.submitted_transaction:
    st.markdown("---")
    
    # Content that used to be inside the now-removed second form
    green_check_url = "https://media.istockphoto.com/id/1416145560/vector/green-circle-with-green-tick-flat-ok-sticker-icon-green-check-mark-icon-tick-symbol-in-green.jpg?s=612x612&w=0&k=20&c=Uh3KS7c_o5QmrfisyV-aRzDUNqtAM7QUVJrc8bniVsQ="
    conditional_write = """
        <b>Conditional Write Against Bigtable</b><br>
        <div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
        <pre style="background-color: #e0e0e0; padding: 10px; border-radius: 3px; overflow-x: auto;">
            condition_filter = ValueRegexFilter(b'pending')
            mutation.check_and_mutate(
                predicate=condition_filter,
                # True mutation: executed if the predicate (condition_filter) passes
                true_mutations=[
                    ('set_cell', column_family_id, column_qualifier, new_value, None)
                ],
                # False mutations=[]
            )
            </pre>
            </div>"""
    st.markdown(conditional_write, unsafe_allow_html=True)
        
    st.write(f'<img src="{green_check_url}" width="100">', unsafe_allow_html=True)
    st.write("<b>Rules based check sucessfull - Transaction Submitted to Bigtable</b>", unsafe_allow_html=True)

    # --- Display Collected Data ---
    st.markdown("---")
    st.header("Submitted Transaction")
    
    data = st.session_state.transaction_data
    # Use stored data for display
    st.write(f"**Credit Card Number:** **** **** **** {data['credit_card_str'][-4:]}")
    st.write(f"**Transaction Amount:** ${data['amount']:.2f}")
    st.write(f"**Category:** {data['category']}")
    st.write(f"**Merchant:** {data['merchant']}")
    
    # and place it OUTSIDE the form definition.
    agent_analysis = st.button("Run fraud detection agent on historical transactions")

    if agent_analysis:
        # Toggle the state to show the agent analysis results
        st.session_state.agent_ran = True

# --- 5. Logic for Agent Analysis Results (controlled by a separate state) ---
if st.session_state.agent_ran:
    st.markdown("---")
    st.header("Fraud Detection Agent Analysis 🤖")
    st.markdown("**Historical data analysis complete.**")
    
    # Call your data function here
    st.dataframe(return_df()) # Using the placeholder/imported function