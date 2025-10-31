#transaction_entry.py
import streamlit as st
import pandas as pd
import asyncio
from numpy.random import default_rng as rng
import sys

sys.path.insert(1, 'bt_utils')
import execute_btsql as bt_sql

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
    st.markdown(conditional_write, unsafe_allow_html=True)
            
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

    # Run the query and display the result
    df = bt_sql.return_transaction_hx_df(form_data['credit_card_str'])
    st.dataframe(df)
    