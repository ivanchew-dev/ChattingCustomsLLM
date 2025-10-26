import streamlit as st
from helper import login_util
import pandas as pd
from datetime import datetime, timedelta # Added timedelta
# Conceptual import for the external LLM routing function
from core import router
from helper import rag_util
import os
import altair as alt # Added Altair for the chart

# --- Configuration and Setup ---

# Set wide layout and page title
st.set_page_config(layout="wide", page_title="Simple AI Chat Client")

# Define file paths
THREAT_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "datastore", "appData", "threatData.csv")


# --- Data Loading Functions ---
def load_threat_data_fresh(file_path):        
    """Load threat data without caching to get the latest updates."""
    try:
        df = pd.read_csv(file_path)
        # Convert 'date' column to date objects for comparison/filtering
        df['date'] = pd.to_datetime(df['date']).dt.date
        # Ensure numeric columns are correctly typed for map and chart
        df['latitude'] = pd.to_numeric(df['latitude'])
        df['longitude'] = pd.to_numeric(df['longitude'])
        return df
    except Exception as e:
        st.error(f"Error loading threat data: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

@st.cache_data
def load_threat_data_cached(file_path, cache_key, file_mod_time):        
    """Load threat data with cache that can be busted by changing cache_key or file modification time."""
    try:
        if not os.path.exists(file_path):
            st.error(f"Threat data file not found: {file_path}")
            return pd.DataFrame()
        
        df = pd.read_csv(file_path)
        # Convert 'date' column to date objects for comparison/filtering
        df['date'] = pd.to_datetime(df['date']).dt.date
        # Ensure numeric columns are correctly typed for map and chart
        df['latitude'] = pd.to_numeric(df['latitude'])
        df['longitude'] = pd.to_numeric(df['longitude'])
        
        # Add debug info
        st.info(f"📁 Loaded {len(df)} records from: {file_path}")
        return df
    except Exception as e:
        st.error(f"Error loading threat data: {e}")
        return pd.DataFrame() # Return empty DataFrame on error

# --- State Management ---

if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
    
# State variable to manage the current main view
if "current_view" not in st.session_state:
    st.session_state.current_view = "chat" # Default is chat

# --- Main App Functions ---

def handle_login(username, password):
    """Conceptual login function."""
    if username == "admin" and password == "secure":
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success(f"Welcome, {username}!")
        st.rerun()
    elif username and password:
        st.error("Invalid credentials.")

def handle_chat_input(prompt):
    """Handles the user's chat input."""

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner("AI is thinking..."):
            try:
                ai_response = router.route_to_chatbot(prompt)
            except Exception as e:
                ai_response = f"**Error:** Could not connect to AI service. *Router error: {e}*"

        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        st.rerun()

def Load_Rag():
    """Load RAG data function."""
    try:
        # Add your RAG loading logic here
        rag_data_path = os.path.join(os.path.dirname(__file__), "..", "..", "datastore", "ragData")
        rag_util.load_rag(rag_data_path, '*.txt')
        st.success("RAG data loaded successfully!")
        # You can add actual RAG loading implementation here
        # For example: load documents, create embeddings, etc.
    except Exception as e:
        st.error(f"Error loading RAG data: {e}")

# --- Data Viewer Function ---

def display_threat_data_viewer():
    """Displays the interactive Threat Data Viewer, including chart and map."""
    st.title("🛡️ Threat Data Viewer")
    
    # Add refresh button to reload data
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Refresh Data", help="Reload threat data from CSV"):
            # Clear cache to force reload
            if 'threat_data_cache_key' in st.session_state:
                st.session_state.threat_data_cache_key += 1
            else:
                st.session_state.threat_data_cache_key = 1
            st.success("Data refreshed!")
    
    # Initialize cache key if not exists
    if 'threat_data_cache_key' not in st.session_state:
        st.session_state.threat_data_cache_key = 0
    
    # Get file modification time for cache invalidation
    try:
        file_mod_time = os.path.getmtime(THREAT_DATA_FILE)
    except OSError:
        file_mod_time = 0
    
    # Load threat data with file modification time for automatic cache busting
    threat_df = load_threat_data_cached(THREAT_DATA_FILE, st.session_state.threat_data_cache_key, file_mod_time)
    
    # Show data loading status
    current_time = datetime.now().strftime("%H:%M:%S")
    if not threat_df.empty:
        st.success(f"📊 Loaded {len(threat_df)} threat records at {current_time}")
    else:
        st.warning(f"⚠️ No threat data available (checked at {current_time})")
    
    if not threat_df.empty:
        # --- 3. Filtered List View ---
        st.header("Filtered Threat List")
        
        # Get unique categories and sort them
        categories = ['All'] + sorted(threat_df['threat_category'].unique().tolist())
        selected_category = st.selectbox("Filter by Threat Category", categories)

        # Date range slider
        min_date = threat_df['date'].min()
        max_date = threat_df['date'].max()
        
        if min_date and max_date:
            try:
                date_range = st.date_input(
                    "Select Date Range",
                    value=(min_date, max_date),
                    min_value=min_date,
                    max_value=max_date
                )
            except Exception:
                st.warning("Could not determine a valid date range from the data.")
                return

            # Ensure date_range is a tuple of length 2
            if isinstance(date_range, tuple) and len(date_range) == 2:
                start_date, end_date = date_range
                
                # Filter data
                filtered_df = threat_df[
                    (threat_df['date'] >= start_date) &
                    (threat_df['date'] <= end_date)
                ].copy()

                if selected_category != 'All':
                    filtered_df = filtered_df[
                        filtered_df['threat_category'] == selected_category
                    ]
                
                # Select only the required columns for the list view
                display_cols = ['date', 'threat_category', 'threat_category_value', 'ip_address', 'query']
                display_df = filtered_df[display_cols]
                st.markdown(f"**Found {len(filtered_df)} items**")
                
                # Display the data
                if st.button("Display Filtered Threat Data (Expanded List)"):
                    if not display_df.empty:
                        # Use markdown to format the data neatly showing the required columns
                        for _, row in display_df.iterrows():
                            st.markdown(f"""
                                **Date:** {row['date']} | **Category:** `{row['threat_category']}` | **Severity:** `{row['threat_category_value']}`
                                **IP:** `{row['ip_address']}` | **Query:** `{row['query']}`

                                ---
                            """)
                    else:
                        st.info("No data found for the selected filters.")
            else:
                 st.warning("Please select a valid date range.") 
        # --- 1. Trend Line Chart (Last 7 Days) ---
        st.header("Threat Trend: Last 7 Days")
        
        max_date = threat_df['date'].max()
        # Calculate the start date for the last 7 days (inclusive of max_date)
        start_date_7d = max_date - timedelta(days=6)
        
        # Filter for the last 7 days
        df_7d = threat_df[threat_df['date'] >= start_date_7d].copy()
        
        if not df_7d.empty:
            # Group by date and threat_category, then count
            df_trend = df_7d.groupby(['date', 'threat_category']).size().reset_index(name='count')
            df_trend['date'] = pd.to_datetime(df_trend['date']) # Convert back to datetime for Altair
            
            # Create the Altair chart
            chart = alt.Chart(df_trend).mark_line(point=True).encode(
                x=alt.X('date', title='Date'),
                y=alt.Y('count', title='Threat Count'),
                color='threat_category',
                tooltip=['date', 'threat_category', 'count']
            ).properties(
                title=f"Threat Count by Category ({start_date_7d.isoformat()} to {max_date.isoformat()})"
            ).interactive()
            
            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("Not enough data to generate a 7-day trend chart.")
        
        st.divider()

        # --- 2. Map View ---
        st.header("Geographic Threat Locations")

        # Prepare data for st.map (it requires 'lat' and 'lon' as columns)
        # Using a small radius to group nearby incidents.
        st.map(threat_df[['latitude', 'longitude', 'threat_category']].rename(
            columns={'latitude': 'lat', 'longitude': 'lon'}
        ), zoom=2)
        
        st.divider()
    else:
        st.warning("Threat data is not available.")
        
# --- Sidebar (Left) ---

with st.sidebar:
    st.title("User & Navigation")
    st.divider()

    ## 1. User Login / Status
    st.header("User Status")
    if not login_util.check_password():  

        st.info("You can chat without logging in.")
    else:
        st.success(f"Logged in as: **Customs Officer**")
        
        # 💡 Navigation Toggling button logic
        if st.session_state.current_view == "chat":
            button_label = "View Threat Data 🛡️"
            next_view = "data"
        else:
            button_label = "View Chat Interface 🤖"
            next_view = "chat"
            
        if st.button(button_label, key="view_toggle_button"):
            st.session_state.current_view = next_view
            st.rerun()

        if st.button("Load RAG 📚", key="load_rag_button"):
            Load_Rag()

        if st.button("Logout"):
            st.session_state["password_correct"] = False
            st.session_state.current_view = "chat" # Reset view on logout
            st.rerun()

    st.divider()

# --- Main Content (Conditional Display) ---

if st.session_state.current_view == "chat":
    # --- Chat Interface ---
    st.title("🤖 AI Chat Interface")
    st.markdown("Feel free to start chatting! Login is optional.")

    # Display chat messages from history
    for message in st.session_state.messages:
        if message["role"] == "assistant":
            st.chat_message(message["role"]).markdown(message["content"])
        else:
            st.chat_message(message["role"]).write(message["content"])

    # Chat Input
    with st.container():
        user_prompt = st.chat_input(
            "Enter your message below:",
            key="multi_line_chat_input",
        )

        if user_prompt:
            handle_chat_input(user_prompt)

elif st.session_state.current_view == "data":
    # --- Data Viewer ---
    if st.session_state.get("password_correct", False):
        display_threat_data_viewer()
    else:
        # Failsafe if the state got corrupted
        st.error("You must be logged in to view the Threat Data.")
        st.session_state.current_view = "chat"
        st.rerun()