import openai
import pandas as pd
import json

# Load the data dictionary
with open("data_dictionary.json", "r") as f:
    data_dictionary = json.load(f)

# Set up OpenAI API key
#openai.api_key = "YOUR_OPENAI_API_KEY"  # Set up your API key here
openai.api_key = "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"  # Set up your API key here

def interpret_question_with_openai(query, conversation_history):
    """
    Use OpenAI API to interpret the query with conversation history for context.
    """
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
    
    # Combine the conversation history with the current prompt
    messages = conversation_history + [
        {"role": "system", "content": "You are a data assistant that identifies user intent, datasets, and analysis instructions based on a query."},
        {"role": "user", "content": prompt}
    ]
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
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

def query_data(query, role, conversation_history):
    """
    Main function to interpret the query with follow-up context, load necessary datasets, and generate a response.
    """
    # Use OpenAI to interpret the question and identify required datasets and actions
    datasets, summary_actions, action, chart_type = interpret_question_with_openai(query, conversation_history)

    # Load each required dataset dynamically
    data_frames = {}
    for dataset in datasets:
        data_frames[dataset] = load_data(dataset)
    
    # Verify that all required datasets are loaded
    if any(df is None for df in data_frames.values()):
        return {
            "message": "Failed to load one or more required datasets.",
            "summary": None,
            "preview": None,
            "chart_type": chart_type
        }
    
    # Combine datasets if needed (example: merging customer and transaction data)
    if "customer_risk_markers" in data_frames and ("debit_transactions" in data_frames or "credit_transactions" in data_frames):
        transaction_data = pd.concat(
            [data_frames.get("credit_transactions"), data_frames.get("debit_transactions")],
            ignore_index=True
        )
        transaction_with_customer = transaction_data.merge(data_frames["account_customer_mapping"], on="account_id", how="left")
        combined_data = transaction_with_customer.merge(data_frames["customer_risk_markers"], on="customer_id", how="left")
    else:
        # If no merging is required, use the first dataset for preview
        combined_data = list(data_frames.values())[0]

    # Generate summary based on the summary actions
    summary = {}
    for action in summary_actions:
        if action == "calculate average transaction amount" and "transaction_amount" in combined_data.columns:
            summary["Average Transaction Amount"] = combined_data["transaction_amount"].mean()
        elif action == "show distribution of risk markers" and "risk_marker" in combined_data.columns:
            summary["Risk Marker Distribution"] = combined_data["risk_marker"].value_counts().to_dict()
    
    # Create a preview of the combined or single dataset for Streamlit output
    preview = combined_data.head(10)

    return {
        "message": "Data retrieved successfully.",
        "summary": summary,
        "preview": preview,
        "chart_type": chart_type
    }