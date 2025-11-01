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

#transaction_entry.py
import streamlit as st
import pandas as pd
import asyncio
from numpy.random import default_rng as rng
import sys
import re

sys.path.insert(1, 'bt_utils')
import execute_btsql as bt_sql

sys.path.insert(1, 'bt_fraud_agent')
import agent_analyzer as agent_analyzer

st.set_page_config(layout="wide")

st.image("https://storage.mtls.cloud.google.com/crosbie/btfraud.png", width=650)
st.title("Enter Credit Card Transaction")

#st.title(agent_analyzer.run_fraud_agent("What is the current time in Ramsey, NJ"))

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

with st.form("transaction_form"):
    # --- Form Fields ---
    # --- Credit Card ---
    # Using text_input for validation flexibility
    credit_card_str = st.text_input("Credit Card Number", help="Enter the numeric credit card number.")
    credit_card_validated = None
    if credit_card_str:
        if credit_card_str.isdigit():
            credit_card_validated = int(credit_card_str)
        else:
            st.error("Invalid input: Credit card number must contain only digits.")

    # --- Amount ---
    # number_input is ideal for float values
    amount = st.number_input("Amount", format="%.2f", step=0.01, help="Enter the transaction amount.")

    category = st.selectbox(
        "Category",
        ("food_dining", "personal_care", "entertainment", "shopping_pos", "kids_pets", "health_fitness", "grocery_pos", "misc_net", "travel", "shopping_net", "gas_transport", "grocery_net", "home", "misc_pos"),
    )

    merchant = st.text_input("Merchant", help="Enter the merchant name.")

    #flexible schema
    if 'key_value_pairs' not in st.session_state:
        # Start with one empty pair
        st.session_state.key_value_pairs = [{'key': '', 'value': ''}]

    def add_pair():
        """Adds an empty key-value pair to the session state."""
        st.session_state.key_value_pairs.append({'key': '', 'value': ''})

    def remove_pair(index):
        """Removes a key-value pair at the given index from the session state."""
        if len(st.session_state.key_value_pairs) > 1:
            st.session_state.key_value_pairs.pop(index)
        else:
            # Optionally clear the fields if only one remains
            st.session_state.key_value_pairs[0] = {'key': '', 'value': ''}
            st.warning("Cannot remove the last pair. Fields have been reset.")

    st.subheader("Add flexible schema")
        # Create an input for each key-value pair in the session state
    for i, pair in enumerate(st.session_state.key_value_pairs):
            
        # Use columns to align the Key input, Value input, and a Remove button
        col1, col2 = st.columns([0.4, 0.4])
            
        # Key Input
        with col1:
            key_input = st.text_input(
                label=f"Key {i+1}", 
                value=pair['key'], 
                key=f"key_{i}",
                label_visibility="collapsed",
                placeholder="Enter Key Name"
            )
                
            # Value Input
            with col2:
                value_input = st.text_input(
                label=f"Value {i+1}", 
                value=pair['value'], 
                key=f"value_{i}",
                label_visibility="collapsed",
                placeholder="Enter Value"
            )
                
            # Update the session state as the user types (important for adding/removing)
            st.session_state.key_value_pairs[i]['key'] = key_input
            st.session_state.key_value_pairs[i]['value'] = value_input
            

    #orginal submission for form
    submitted = st.form_submit_button("Submit to Bigtable")

if submitted:
    st.session_state.submitted_transaction = True
    st.session_state.agent_ran = False # Reset agent analysis display

    # Store data for later display
    st.session_state.transaction_data = {
        'credit_card_str': credit_card_str,
        'amount': amount,
        'category': category,
        'merchant': merchant
    }
    # Reruns the app immediately to process the form submission and show the conditional write
    #st.rerun()

if st.session_state.submitted_transaction:
 
    green_check_url = "https://media.istockphoto.com/id/1416145560/vector/green-circle-with-green-tick-flat-ok-sticker-icon-green-check-mark-icon-tick-symbol-in-green.jpg?s=612x612&w=0&k=20&c=Uh3KS7c_o5QmrfisyV-aRzDUNqtAM7QUVJrc8bniVsQ="
    text = "Validated against users flagged merchants"
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
                    # False mutation: executed if the predicate (condition_filter) fails
                    false_mutations=[]
                )
                </pre>
                </div>"""
    #st.markdown(conditional_write, unsafe_allow_html=True)
    st.code("""
                condition_filter = ValueRegexFilter(b'pending')
                mutation.check_and_mutate(
                    predicate=condition_filter,
                    # True mutation: executed if the predicate (condition_filter) passes
                    true_mutations=[
                        ('set_cell', column_family_id, column_qualifier, new_value, None)
                    ],
                    # False mutation: executed if the predicate (condition_filter) fails
                    false_mutations=[]""", 
                    language='python'
            )

    ##st.write(f"![Check Logo]({green_check_url}) {text}")
    st.write(f'<img src="{green_check_url}" width="100">', unsafe_allow_html=True)
    st.write("<b>Rules based check sucessfull - Transaction Submitted to Bigtable</b>", unsafe_allow_html=True)
    # --- Display Collected Data ---
    st.markdown("---")
    st.header("Submitted Transaction")

    #if credit_card_validated and amount > 0:
            # Display the captured data in a structured way
    form_data = st.session_state.transaction_data
    st.write(f"**Credit Card Number:** **** **** **** {form_data['credit_card_str'][-4:]}")
    st.write(f"**Transaction Amount:** ${form_data['amount']:.2f}")
    st.write(f"**Category:** {form_data['category']}")
    st.write(f"**Merchant:** {form_data['merchant']}")
 
    agent_analysis = st.button("Run fraud detection agent on historical transactions")
    if agent_analysis:
        st.session_state.agent_ran = True

if st.session_state.agent_ran:
    st.header("Fraud Detection Agent Analysis 🤖")
    st.markdown("**Running fraud detection on recent transactions.**")
    # --- Call the Fraud Agent ---
    with st.spinner("Agent is thinking..."):
        # Run the query and display the result
        st.write("Pulling a timeseries of transaction history from Bigtable logical view for analysis")
        df = bt_sql.return_transaction_hx_df(form_data['credit_card_str'])
        st.dataframe(df)

        #AGENT GETS RUN HERE
        fruad_analysis = agent_analyzer.run_fraud_agent("Create a fraud analysis for" + form_data['credit_card_str'])

        st.write("Agent fraud analysis summary for last transaction on card <strong>" + form_data['credit_card_str'] + "</strong>", 
        unsafe_allow_html=True)

        #parse out fraud recomendation 
        pattern = r"IS_FRAUD:(\d+)"
        match = re.search(pattern, text)
        if match:
            is_fraud = int(match.group(1))
        else:
            is_fraud = 0

        if is_fraud == 1:

            st.write(
            """<div style="background-color: red; padding: 15px; border-radius: 5px;">
            <pre style="background-color: red; padding: 10px; border-radius: 3px; overflow-x: auto;">"""
            + "<b>Potential fraud detected</b>"
            + """</pre></div>""",
            unsafe_allow_html=True,
            )

            st.write(
            """<div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
            <pre style="background-color: #e0e0e0; padding: 10px; border-radius: 3px; overflow-x: auto;">"""
            + fruad_analysis.replace("IS_FRAUD: 1", "").replace("FRAUD_ANALYSIS:", "")
            + """</pre></div>""",
            unsafe_allow_html=True,
        )        
        else:
            st.write(
            """<div style="background-color: green; padding: 15px; border-radius: 5px;">
            <pre style="background-color: green; padding: 10px; border-radius: 3px; overflow-x: auto;">"""
            + "<b>No fraud detected</b>"
            + """</pre></div>""",
            unsafe_allow_html=True,
            )

            st.write(
            """<div style="background-color: #f0f0f0; padding: 15px; border-radius: 5px;">
            <pre style="background-color: #e0e0e0;; padding: 10px; border-radius: 3px; overflow-x: auto;">"""
            + fruad_analysis.replace("IS_FRAUD: 0", "").replace("FRAUD_ANALYSIS:", "")
            + """</pre></div>""",
            unsafe_allow_html=True,
            )
            





  

    
    