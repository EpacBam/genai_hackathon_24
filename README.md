
# GenAI System Integration Hub

This application leverages OpenAI's GPT-4 to create an intelligent system integration hub for querying and visualizing data across multiple datasets. The hub interprets user questions and dynamically retrieves tables, generates statistics, and creates charts (e.g., bar charts, line charts) based on the query's intent.

## Features

1. **Natural Language Query Interpretation**: Uses GPT-4 to interpret user queries and determine if the user wants tables, statistics, charts, or a combination.
2. **Flexible Data Access**: Retrieves relevant datasets based on user role permissions and query context.
3. **Dynamic Visualization**: Generates tables, descriptive statistics, and visualizations (bar charts, line charts, pie charts) on demand.
4. **Access Control**: Only accessible datasets are displayed based on the user's role, as defined in `permissions.json`.

## Prerequisites

- Python 3.8+
- An OpenAI API key with access to GPT-4
- Streamlit, Pandas, Matplotlib, and OpenAI Python packages

## Setup Instructions

1. **Clone the Repository**:

   ```bash
   git clone <repository-url>
   cd GenAI-System-Integration-Hub
   ```

2. **Install Dependencies**:

   Install the required Python packages using the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

3. **Add Your OpenAI API Key**:

   Replace `"YOUR_OPENAI_API_KEY"` in `query_handler.py` with your actual OpenAI API key.

4. **Data Preparation**:

   Ensure the following files are present in the `data` folder:
   - `customer_demographics.csv`
   - `credit_transactions.csv`
   - `customer_risk_markers.csv`
   - ...and other relevant datasets

   Each dataset should match the format specified in `data_dictionary.json`.

5. **Permissions**:

   Customize `permissions.json` to define dataset access per user role.

## Usage Instructions

1. **Run the Application**:

   Start the Streamlit application by running:

   ```bash
   streamlit run src/app.py
   ```

2. **Interacting with the Application**:

   - **Enter a Query**: Type in a question, such as:
     - "Show statistics on customer transactions."
     - "Display a table of customer demographics."
     - "Create a bar chart for customer risk markers."
   - **Select Role**: Choose your role (e.g., analyst or manager) to access datasets allowed by your permissions.

3. **Query Types**:

   The application can handle various query types based on your intent:
   - **Tables**: View raw data tables from requested datasets.
   - **Statistics**: Generate descriptive statistics for numerical data.
   - **Charts**: Create bar charts, line charts, and pie charts based on the query.

4. **Follow-up Questions**:

   Use the follow-up input box to ask further questions based on previous results.

## Files and Directory Structure

Below is the structure of the repository and descriptions of each file:

```
GenAI-System-Integration-Hub/
├── data/                           # Folder containing dataset CSV files
│   ├── customer_demographics.csv
│   ├── credit_transactions.csv
│   └── customer_risk_markers.csv
├── src/                            # Source code folder
│   ├── app.py                      # Main Streamlit app
│   └── query_handler.py            # Contains functions for data interpretation and retrieval
├── data_dictionary.json            # Defines columns and metadata for each dataset
├── permissions.json                # Defines dataset access permissions per user role
├── requirements.txt                # Lists required Python packages
└── README.md                       # Project documentation (this file)
```

## Example Queries

- "Can you provide a table of customer transactions?"
- "Show statistics for customer demographics and transactions."
- "Create a bar chart for customer risk markers."
- "Display both the table and statistics for customer risk and demographics."

## Technical Notes

1. **Using GPT-4**: This app leverages GPT-4 (or GPT-4-turbo) to interpret natural language queries and identify user intent, requested datasets, and visualization types.
2. **Dynamic Data Loading**: Datasets are loaded dynamically based on the user query, combined if needed, and filtered as per user request.
3. **Chart Generation**: Uses Matplotlib to generate visualizations based on interpreted chart type (e.g., bar chart, line chart).

## Troubleshooting

- Ensure your OpenAI API key is valid and has access to GPT-4.
- Verify dataset availability in the `data` folder.
- Check role permissions in `permissions.json` to ensure you have access to the requested datasets.

## License

This project is licensed under the MIT License.

## Contact

For support, please reach out to the development team.
