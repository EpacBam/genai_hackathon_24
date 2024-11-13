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
    3. Generate a natural language summary of the data based on the query, similar to an analysis a data analyst might provide.
    
    Respond with a JSON object with four keys:
    - "datasets": a list of relevant datasets.
    - "summary_actions": a list of instructions for processing data (e.g., "calculate average," "show distribution").
    - "action": "table", "statistics", "chart", or "both".
    - "chart_type": "bar", "line", "pie", or null if no chart is requested.
    
    User Query: {query}
    """
    
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
    Load individual datasets from the data folder with debugging.
    """
    file_path = f"data/{dataset_name}.csv"
    try:
        data = pd.read_csv(file_path)
        print(f"Loaded data from {file_path}")
        print(f"Data Types for {dataset_name}:\n{data.dtypes}")
        print(f"First few rows of {dataset_name}:\n{data.head()}")
        return data
    except FileNotFoundError:
        print(f"File {file_path} not found.")
        return None

def debug_data(df, name):
    """
    Print debugging information for a DataFrame.
    """
    if df is not None:
        print(f"--- {name} ---")
        print(f"Shape: {df.shape}")
        print(f"Data Types:\n{df.dtypes}")
        print(f"Missing values:\n{df.isnull().sum()}")
        print(f"First few rows:\n{df.head()}\n")
    else:
        print(f"Data for {name} is None.")

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
        debug_data(data_frames[dataset], dataset)
    
    # Verify that all required datasets are loaded
    if any(df is None for df in data_frames.values()):
        return {
            "message": "Failed to load one or more required datasets.",
            "summary": None,
            "preview": None,
            "chart_type": chart_type
        }
    
    # Combine datasets if needed (example: merging customer and transaction data)
    combined_data = pd.concat(data_frames.values(), ignore_index=True) if len(data_frames) > 1 else list(data_frames.values())[0]
    debug_data(combined_data, "Combined Data")

    # Generate summary based on the summary actions
    summary = {}
    for action in summary_actions:
        if action == "calculate average transaction amount" and "transaction_amount" in combined_data.columns:
            summary["Average Transaction Amount"] = combined_data["transaction_amount"].mean()
        elif action == "show distribution of risk markers" and "risk_marker" in combined_data.columns:
            summary["Risk Marker Distribution"] = combined_data["risk_marker"].value_counts().to_dict()
    
    # Create a preview of the combined or single dataset for Streamlit output
    preview = combined_data.head(10)
    
    # Use GPT-4 to generate analysis based on the summary
    analysis_prompt = f"""
    Here are the calculated statistics based on the user's query:
    {summary}
    
    Please provide an analytical summary in natural language, highlighting key insights.
    """
    
    analysis_response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are a data analyst who provides insights based on data summaries."},
                  {"role": "user", "content": analysis_prompt}],
        max_tokens=300,
        temperature=0.5
    )
    analysis_text = analysis_response.choices[0].message['content'].strip()

    return {
        "message": "Data retrieved successfully.",
        "summary": summary,
        "preview": preview,
        "chart_type": chart_type,
        "analysis": analysis_text
    }