import openai
import streamlit as st
from query_handler import query_data
import matplotlib.pyplot as plt
from PIL import Image

# Custom CSS for Barclays colors and styles
st.markdown("""
    <style>
        /* Barclays color palette */
        .main-header { color: #00AEEF; font-size: 40px; font-weight: bold; text-align: center; }
        .sub-header { color: #0072CE; font-size: 20px; text-align: center; }
        .stButton>button { background-color: #00AEEF; color: white; border-radius: 5px; border: none; }
        .stTextInput>label { color: #0072CE; font-weight: bold; }
        .sidebar .sidebar-content { background-color: #E6F2FF; color: #0056A3; }
        .stSelectbox>label { color: #0056A3; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# Load Barclays logo
logo = Image.open("barclays_logo.png")  # Make sure to have barclays_logo.png in the project folder

# Display the logo and main header
st.image(logo, width=200)
st.markdown("<h1 class='main-header'>GenAI System Integration Hub</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Powered by AI to streamline data access and insights across Barclays</p>", unsafe_allow_html=True)

# Initialize conversation history
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []

# Function to handle query processing
def handle_query(query, role):
    # Retrieve conversation history for follow-up questions
    conversation_history = st.session_state.conversation_history
    result = query_data(query, role, conversation_history)
    
    # Update conversation history
    conversation_history.append({"query": query, "response": result})
    st.session_state.conversation_history = conversation_history
    
    # Display result
    st.markdown("### Query Result:")
    st.write(result["message"])
    
    if result.get("summary"):
        st.markdown("### Summary Statistics:")
        st.json(result["summary"])
    
    if result.get("preview") is not None:
        st.markdown("### Data Table Preview:")
        st.dataframe(result["preview"])
    
    # Display a chart if requested and summary_actions is available
    if result.get("chart_type") and result.get("summary_actions"):
        st.write(f"Chart Type Requested: {result['chart_type']}")
        create_bar_chart(result["preview"], result["summary_actions"])
    elif result.get("chart_type"):
        st.write("Chart Type Requested but 'summary_actions' is missing.")

    # Follow-up question input
    follow_up_query = st.text_input("Ask a follow-up question based on previous results:")
    if st.button("Submit Follow-Up"):
        handle_query(follow_up_query, role)

# Function to create bar charts based on query results
def create_bar_chart(data, summary_actions):
    """
    Generate a bar chart from the given data based on summary actions.
    """
    try:
        x_column = summary_actions.get("x_column", data.columns[0])
        y_column = summary_actions.get("y_column", data.columns[1])

        plt.figure(figsize=(10, 5))
        data.groupby(x_column)[y_column].sum().plot(kind="bar", color="#00AEEF")
        plt.title(f"{y_column} by {x_column}")
        plt.xlabel(x_column)
        plt.ylabel(y_column)
        st.pyplot(plt)
    except Exception as e:
        st.write(f"Error generating chart: {e}")

# Streamlit UI setup
st.markdown("<hr>", unsafe_allow_html=True)
query = st.text_input("Enter your query:")
role = st.selectbox("Select your role:", ["manager", "analyst"])

if st.button("Submit"):
    handle_query(query, role)

# Option to clear conversation history
if st.button("Clear Conversation History"):
    st.session_state.conversation_history = []
    st.write("Conversation history cleared.")