import openai
import pandas as pd
import matplotlib.pyplot as plt
import json

# Load data dictionary for reference
with open("data_dictionary.json", "r") as f:
    data_dictionary = json.load(f)

#openai.api_key = "YOUR_OPENAI_API_KEY"  # Set up your API key here
openai.api_key = "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"  # Set up your API key here

def interpret_question_with_openai(query):
    data_dictionary_str = json.dumps(data_dictionary, indent=2)
    prompt = f"""
    You have access to the following datasets and their columns:
    {data_dictionary_str}
    
    Based on the user's query, determine:
    1. The specific datasets needed to answer the query.
    2. What kind of summary, statistics, or insights to provide (e.g., "calculate average transaction amount," "show distribution of risk markers").
    3. Whether a table view, chart (and type), or detailed summary is appropriate for the query.
    
    Respond with a JSON object with four keys:
    - "datasets": a list of relevant datasets.
    - "summary_actions": a list of instructions for processing data (e.g., "calculate average," "show distribution").
    - "action": "table", "statistics", "chart", or "both".
    - "chart_type": "bar", "line", "pie", or null if no chart is requested.
    
    User Query: {query}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a data assistant that identifies user intent, datasets, and analysis instructions based on a query."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300,
        temperature=0.3
    )
    answer = response.choices[0].message['content'].strip()
    parsed_answer = json.loads(answer)
    return parsed_answer['datasets'], parsed_answer['summary_actions'], parsed_answer['action'], parsed_answer['chart_type']

def load_data(dataset_name):
    """
    Load individual datasets from the data folder.
    """
    file_path = f"data/{dataset_name}.csv"
    try:
        data = pd.read_csv(file_path)
        print(f"Loaded data from {file_path}")
        return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def combine_customer_transaction_data():
    """
    Combine customer risk and transaction data using the mapping table.
    """
    # Load datasets
    credit_transactions = load_data("credit_transactions")
    debit_transactions = load_data("debit_transactions")
    customer_risk_markers = load_data("customer_risk_markers")
    account_customer_mapping = load_data("account_customer_mapping")

    # Check if all datasets loaded successfully
    if credit_transactions is None or debit_transactions is None or customer_risk_markers is None or account_customer_mapping is None:
        print("One or more datasets could not be loaded.")
        return None

    # Combine credit and debit transactions into one DataFrame
    transaction_data = pd.concat([credit_transactions, debit_transactions], ignore_index=True)
    
    # Merge transaction data with account-customer mapping on 'account_id'
    transaction_with_customer = transaction_data.merge(account_customer_mapping, on="account_id", how="left")

    # Now merge with customer risk markers on 'customer_id'
    combined_data = transaction_with_customer.merge(customer_risk_markers, on="customer_id", how="left")

    print("Combined Data:")
    print(combined_data.head())
    return combined_data

def query_data(query, role):
    """
    Process the query and generate an appropriate response.
    """
    if "risk stats" in query and "transaction stats" in query:
        combined_data = combine_customer_transaction_data()
        
        if combined_data is not None:
            # Generate summary statistics for risk and transaction data
            summary = {
                "Total Transactions": combined_data["transaction_amount"].count(),
                "Total Transaction Amount": combined_data["transaction_amount"].sum(),
                "Risk Marker Count": combined_data["risk_marker"].value_counts().to_dict()
            }
            
            # Create a preview for Streamlit output
            preview = combined_data.head(10)
            
            # Output to Streamlit
            result = {
                "message": "Data retrieved successfully.",
                "summary": summary,
                "preview": preview
            }
            return result
        else:
            return {
                "message": "Failed to load combined data.",
                "preview": None
            }
    else:
        return {
            "message": "Query not recognized. Try asking for risk and transaction stats.",
            "preview": None
        }