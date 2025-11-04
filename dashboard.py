import streamlit as st
import pandas as pd
import sys 

sys.path.insert(1, 'bt_utils')
import execute_btsql as bt_sql

# Set up the data
merchant_summary, raw_data = bt_sql.generate_sample_data()

st.set_page_config(layout="wide", page_title="Transaction Hotspots by Merchant (last hour)")
st.title("🔥Transaction Hotspots by Merchant (last hour)🔥")

# Create the main four columns container
col1, col2, col3, col4 = st.columns([2, 1, 3, 1])

with col1:
    st.markdown("**Merchant Name**")
with col2:
    st.markdown("**Transaction Count**")
with col3:
    st.markdown("**Review AI Analysis**")
with col4:
    st.markdown("**Action**")

st.markdown("---") # Visual separator

# Iterate through the summary data to display rows
for index, row in merchant_summary.iterrows():
    # Use st.columns for the row layout inside the loop
    r_col1, r_col2, r_col3, r_col4 = st.columns([2, 1, 3, 1])
    
    # Column 1: Merchant Name
    r_col1.write(f"*{row['merchant']}*")
    
    # Column 2: Count
    r_col2.write(row['approx_distinct_transaction_count'])
    
    # Column 3: Review Analysis Button (opens the Accordion)
    
    # A unique key is necessary for each button/element in a loop
    #analysis_button_key = f"analysis_btn_{index}"
    
    # Use a placeholder (empty container) to insert the content below the button later
    accordion_placeholder = r_col3.empty()
    
    # The actual button: if clicked, its key is now 'in' st.session_state
    #if r_col3.button("Review AI Analysis", key=analysis_button_key):
        
    # Filter the raw data for the current merchant
    current_merchant_data = raw_data[raw_data['merchant'] == row['merchant']]
        
        # Create an accordion inside the placeholder
    with accordion_placeholder.expander(f"*Detailed Analysis for {row['merchant']}*"):
            # Display a summary first
            total_fraud_count = current_merchant_data['is_fraud'].sum()
            total_records = len(current_merchant_data)
            
            st.info(f"Summary: **{total_fraud_count}** of {total_records} transactions flagged as potential fraud.")
            
            # Display the individual records (is_fraud and fraud_analysis)
            analysis_df = current_merchant_data[['is_fraud', 'fraud_analysis']].reset_index(drop=True)
            
            st.dataframe(
                analysis_df, 
                width="stretch",
                column_config={
                    "is_fraud": st.column_config.CheckboxColumn(
                        "Is Fraud?", help="AI Model's Fraud Flag", default=False
                    ),
                    "fraud_analysis": "AI Analysis Details"
                }
            )

    # Column 4: Add to Blocklist Button (makes a toast appear)
    blocklist_button_key = f"blocklist_btn_{index}"
    
    # The action that happens when the button is clicked
    if r_col4.button("Add to Blocklist", key=blocklist_button_key, type="primary"):
        st.toast(f"*{row['merchant']}* has been added to the blocklist successfully!", icon='🚨')
        
    st.markdown("---") # Separator between merchant rows