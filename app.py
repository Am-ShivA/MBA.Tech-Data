import streamlit as st
import pandas as pd
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import base64
from PIL import Image
import io
import sqlite3

# Set page configuration
st.set_page_config(
    page_title="MBA.Tech Data",
    page_icon="🧑🏻‍💻",
    layout="wide"
)

# Initialize session state for login attempts if not exists
if 'login_attempts' not in st.session_state:
    st.session_state.login_attempts = 0

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

MAIN_PASSWORD = "placecom"
CONTACT_PASSWORD = "svkm@nmims"

def check_main_password():
    """Main password authentication system"""
    if st.session_state.login_attempts >= 3:
        st.error("Maximum login attempts exceeded. Application is locked.")
        st.stop()
    
    if not st.session_state.authenticated:
        st.markdown("""
            <style>
                /* Hide all main content when not authenticated */
                #MainMenu {visibility: hidden;}
                div[data-testid="stSidebarContent"] {visibility: hidden;}
                footer {visibility: hidden;}
            </style>
        """, unsafe_allow_html=True)
        
        st.title("MBA.Tech Batch Data Viewer")
        st.write("### Authentication Required")
        
        # Password input
        password = st.text_input("Enter Password", type="password", key="main_password")
        
        if st.button("Login"):
            if password == MAIN_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.login_attempts = 0
                st.rerun()
            else:
                st.session_state.login_attempts += 1
                remaining_attempts = 3 - st.session_state.login_attempts
                if remaining_attempts > 0:
                    st.error(f"Incorrect password. {remaining_attempts} attempts remaining.")
                else:
                    st.error("Maximum login attempts exceeded. Application is locked.")
                st.stop()
        
        # Stop execution if not authenticated
        st.stop()

# Check main password before showing any content
check_main_password()

# Add custom CSS and JavaScript for enhanced protection
st.markdown("""
    <style>
        /* Disable right-click on the entire app */
        #root {
            -webkit-user-select: none;
            -ms-user-select: none;
            user-select: none;
        }
        
        /* Hide all download buttons and related elements */
        .downloadButton,
        .exporterButton,
        button[aria-label*="Download"],
        button[title*="Download"],
        .stDownloadButton,
        .css-1a1fmpi,  /* Streamlit's download button class */
        .css-1b0udgb,  /* Streamlit's export button class */
        [data-testid="StyledFullScreenButton"],
        .element-container button,
        .stDataFrame button {
            display: none !important;
        }
        
        /* Hide the menu button */
        .stDeployButton {
            display: none !important;
        }
        
        /* Disable iframe downloads in plotly charts */
        iframe {
            pointer-events: none !important;
        }
        
        /* Disable text selection in dataframes and tables */
        .stDataFrame, .dataframe, table {
            -webkit-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
        
        /* Hide export menu items */
        div[role="menu"] button {
            display: none !important;
        }
        
        /* Disable copy functionality in tables */
        .stTable, .table {
            -webkit-touch-callout: none !important;
            -webkit-user-select: none !important;
            -khtml-user-select: none !important;
            -moz-user-select: none !important;
            -ms-user-select: none !important;
            user-select: none !important;
        }
        
        /* Hide any potential CSV download links */
        a[href$=".csv"],
        a[href$=".xlsx"],
        a[href$=".xls"] {
            display: none !important;
        }
    </style>
    <script>
        // Disable right-click
        document.addEventListener('contextmenu', function(e) {
            e.preventDefault();
        });
        
        // Disable keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && 
                (e.key === 'p' || 
                 e.key === 's' || 
                 e.key === 'c' || 
                 e.key === 'v' ||
                 e.key === 'a')) {
                e.preventDefault();
            }
        });
        
        // Disable drag and drop
        document.addEventListener('dragstart', function(e) {
            e.preventDefault();
        });
        
        // Disable copy
        document.addEventListener('copy', function(e) {
            e.preventDefault();
        });
        
        // Additional protection for tables
        window.addEventListener('load', function() {
            // Disable right-click on tables
            const tables = document.getElementsByTagName('table');
            for (let table of tables) {
                table.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                });
            }
            
            // Remove download buttons that might be dynamically added
            setInterval(function() {
                const buttons = document.querySelectorAll('button');
                buttons.forEach(function(button) {
                    if (button.innerText.toLowerCase().includes('download') ||
                        button.innerText.toLowerCase().includes('export') ||
                        button.title.toLowerCase().includes('download') ||
                        button.title.toLowerCase().includes('export')) {
                        button.style.display = 'none';
                    }
                });
            }, 1000);
        });
    </script>
""", unsafe_allow_html=True)

# Add title
st.title("MBA.Tech Batch Data Viewer")

# Function to configure plotly figures with disabled download options
def configure_plotly_figure(fig):
    fig.update_layout(
        modebar=dict(
            remove=[
                'sendDataToCloud', 'select2d', 'lasso2d', 'zoomIn2d', 
                'zoomOut2d', 'autoScale2d', 'resetScale2d', 
                'hoverClosestCartesian', 'hoverCompareCartesian',
                'toggleSpikelines', 'pan2d', 'downloadImage', 
                'toImage', 'saveAsPng', 'saveAsSvg', 'saveAsPdf',
                'downloadCsv', 'downloadXlsx', 'downloadJSON'
            ]
        ),
        dragmode=False,  # Disable drag mode
        showlegend=True,
        hovermode='closest'
    )
    return fig

# Function to display plotly chart with protection
def display_plotly_chart(fig):
    """Helper function to display plotly charts with protection against downloads"""
    configured_fig = configure_plotly_figure(fig)
    st.plotly_chart(configured_fig, use_container_width=True, config={'displayModeBar': False})

# Function to display dataframes securely
def display_secure_dataframe(df, use_container_width=True, hide_index=True):
    """Display dataframe with security measures using Streamlit's native dataframe"""
    # Configure the dataframe display
    st.dataframe(
        df,
        use_container_width=use_container_width,
        hide_index=hide_index,
        column_config={
            "_index": None,  # Hide index column
            **{col: st.column_config.Column(
                width="medium"
            ) for col in df.columns}  # Set consistent column widths
        }
    )

# Function to mask contact numbers
def mask_contact_number(contact):
    if pd.isna(contact) or contact == "Not Assigned":
        return contact
    return "*** *** ****"

# Function to check password
def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["password"] == CONTACT_PASSWORD:  # Updated password
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show input for password.
        st.text_input(
            "Please enter the password to view contact numbers", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input(
            "Please enter the password to view contact numbers", 
            type="password", 
            on_change=password_entered, 
            key="password"
        )
        st.error("😕 Password incorrect")
        return False
    else:
        # Password correct.
        return True

# Create batch selection dropdown in sidebar
batch = st.sidebar.selectbox(
    "Select Batch",
    ["MBA.Tech '25", "MBA.Tech '26"]
)

# Function to load data based on batch selection
def load_batch_data(batch):
    """Load data for a specific batch from SQLite database"""
    conn = sqlite3.connect('mba_tech_data.db')
    
    # Map batch names to table names
    batch_to_table = {
        'MBA.Tech 23': 'mba_tech_23',
        'MBA.Tech 24': 'mba_tech_24',
        'MBA.Tech 25': 'mba_tech_25'
    }
    
    # Read data from the appropriate table
    query = f"SELECT * FROM {batch_to_table[batch]}"
    df = pd.read_sql_query(query, conn)
    
    # Standardize column names
    df.columns = [col.strip().replace('_', ' ').title() for col in df.columns]
    
    conn.close()
    return df

def load_all_data():
    """Load all batch data from SQLite database"""
    conn = sqlite3.connect('mba_tech_data.db')
    df = pd.read_sql_query("SELECT * FROM all_batches", conn)
    conn.close()
    return df

# Function to create select all widget
def multiselect_with_select_all(label, options, key):
    select_all = st.sidebar.checkbox(f"Select All {label}", key=f"select_all_{key}")
    if select_all:
        return st.sidebar.multiselect(
            label,
            options,
            default=list(options),
            key=key
        )
    else:
        return st.sidebar.multiselect(
            label,
            options,
            key=key
        )

def create_distribution_analysis(df, column, title, chart_type="bar", hole=0.4):
    """
    Generic function to create distribution analysis for any column
    """
    st.write(f"### {title}")
    
    # Count distribution
    counts = df[column].value_counts().reset_index()
    counts.columns = [column, "Number of Students"]
    
    # Create visualization
    if chart_type == "bar":
        fig = px.bar(
            counts,
            x=column,
            y="Number of Students",
            title=f"Distribution of Students Across {column}",
            text="Number of Students"
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            height=500
        )
    else:  # pie chart
        fig = px.pie(
            counts,
            values="Number of Students",
            names=column,
            title=f"Distribution of Students Across {column}",
            hole=hole
        )
        fig.update_layout(height=500)
    
    display_plotly_chart(fig)
    
    # Display statistics
    st.write(f"#### {column}-wise Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"##### Student Count by {column}")
        display_secure_dataframe(counts)
    
    with col2:
        st.write("##### Percentage Distribution")
        percent_df = counts.copy()
        total_students = percent_df["Number of Students"].sum()
        percent_df["Percentage"] = (percent_df["Number of Students"] / total_students * 100).round(2)
        percent_df["Percentage"] = percent_df["Percentage"].astype(str) + "%"
        display_secure_dataframe(percent_df)
    
    return counts

def create_cross_tab_analysis(df, row_col, col_col, title):
    """
    Create cross-tabulation analysis between two columns
    """
    st.write(f"### {title}")
    
    # Create cross-tabulation
    cross_tab = pd.crosstab(df[row_col], df[col_col])
    
    # Create heatmap
    fig = px.imshow(
        cross_tab,
        labels=dict(x=col_col, y=row_col, color="Number of Students"),
        title=f"{row_col} vs {col_col} Distribution",
        aspect="auto"
    )
    fig.update_layout(height=600)
    display_plotly_chart(fig)

def create_subject_enrollment_analysis(df, semester):
    """
    Analyze subject enrollment for a specific semester
    """
    subject_cols = [col for col in df.columns if col.startswith(f"Sub {semester}")]
    
    # Create a long format dataframe for all subjects
    all_subjects_data = pd.DataFrame()
    for sub in subject_cols:
        sub_counts = df[sub].value_counts().reset_index()
        sub_counts.columns = ["Subject", "Count"]
        sub_counts["Subject Code"] = sub
        all_subjects_data = pd.concat([all_subjects_data, sub_counts])
    
    # Get top 20 subjects by enrollment
    top_20_subjects = all_subjects_data.nlargest(20, "Count")
    
    # Create bar chart
    fig = px.bar(
        top_20_subjects,
        x="Subject",
        y="Count",
        color="Subject Code",
        title=f"Top 20 {semester} Subject Enrollments",
        labels={"Subject": "Subject Name", "Count": "Number of Students"}
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        height=600,
        showlegend=True
    )
    display_plotly_chart(fig)

def create_combined_distribution_analysis(df, has_major=True):
    """
    Create a combined distribution analysis showing multiple metrics in a single view
    """
    st.write("### Combined Distribution Analysis")
    
    # Create subplots with appropriate layout based on available data
    if has_major:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Campus Distribution", "Branch Distribution", 
                           "Major Distribution", "MIP Company Distribution"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                  [{"type": "pie"}, {"type": "bar"}]]
        )
    else:
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=("Campus Distribution", "Branch Distribution", 
                           "Division Distribution", "MIP Company Distribution"),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                  [{"type": "pie"}, {"type": "bar"}]]
        )
    
    # Campus Distribution (Pie Chart)
    campus_counts = df["CAMPUS"].value_counts()
    fig.add_trace(
        go.Pie(labels=campus_counts.index, values=campus_counts.values, hole=0.4),
        row=1, col=1
    )
    
    # Branch Distribution (Bar Chart)
    branch_counts = df["BRANCH"].value_counts()
    fig.add_trace(
        go.Bar(x=branch_counts.index, y=branch_counts.values, text=branch_counts.values,
               textposition='auto'),
        row=1, col=2
    )
    
    if has_major:
        # Major Distribution (Pie Chart)
        major_counts = df["Major"].value_counts()
        fig.add_trace(
            go.Pie(labels=major_counts.index, values=major_counts.values, hole=0.4),
            row=2, col=1
        )
    else:
        # Division Distribution (Pie Chart)
        div_counts = df["Div"].value_counts()
        fig.add_trace(
            go.Pie(labels=div_counts.index, values=div_counts.values, hole=0.4),
            row=2, col=1
        )
    
    # MIP Company Distribution (Top 10 Bar Chart)
    company_counts = df["MIP Company"].value_counts().head(10)
    fig.add_trace(
        go.Bar(x=company_counts.index, y=company_counts.values, text=company_counts.values,
               textposition='auto'),
        row=2, col=2
    )
    
    fig.update_layout(height=800, showlegend=False)
    display_plotly_chart(fig)

def create_advanced_analytics(df, has_major=True):
    """
    Create advanced analytics including correlations and patterns
    """
    st.write("### Advanced Analytics")
    
    # Create tabs for different advanced analyses
    if has_major:
        tabs = st.tabs(["Subject Combinations", "Campus Insights", "Career Trends"])
    else:
        tabs = st.tabs(["Campus Insights", "Career Trends"])
    
    if has_major:
        with tabs[0]:
            st.write("#### Popular Subject Combinations")
            
            # Analyze common subject combinations for Semester 9
            s9_subjects = [col for col in df.columns if col.startswith("Sub S9")]
            s9_combinations = df[s9_subjects].value_counts().head(10)
            
            st.write("Top Subject Combinations (Semester 9)")
            combo_df = pd.DataFrame(s9_combinations).reset_index()
            combo_df.columns = ['Subject 1', 'Subject 2', 'Subject 3', 'Subject 4', 
                              'Subject 5', 'Subject 6', 'Subject 7', 'Count']
            st.dataframe(combo_df, hide_index=True)
    
    tab_index = 1 if has_major else 0
    with tabs[tab_index]:
        st.write("#### Campus-wise Analysis")
        
        if has_major:
            # Campus vs Major vs Branch Analysis
            campus_analysis = pd.crosstab(
                [df['CAMPUS'], df['BRANCH']], 
                df['Major']
            ).reset_index()
            
            # Create a heatmap
            campus_major_data = []
            for campus in df['CAMPUS'].unique():
                campus_data = df[df['CAMPUS'] == campus]
                for major in df['Major'].unique():
                    count = len(campus_data[campus_data['Major'] == major])
                    campus_major_data.append({
                        'Campus': campus,
                        'Major': major,
                        'Count': count
                    })
            
            campus_major_df = pd.DataFrame(campus_major_data)
            fig = px.density_heatmap(
                campus_major_df,
                x='Campus',
                y='Major',
                z='Count',
                title='Campus-Major Distribution Heatmap'
            )
            display_plotly_chart(fig)
        
        # Add Branch-wise comparison between Mumbai and Shirpur
        st.write("#### Branch Distribution: Mumbai vs Shirpur")
        
        # Create branch counts for each campus
        mumbai_counts = df[df['CAMPUS'] == 'Mumbai']['BRANCH'].value_counts()
        shirpur_counts = df[df['CAMPUS'] == 'Shirpur']['BRANCH'].value_counts()
        
        # Create a DataFrame for comparison
        branch_comparison = pd.DataFrame({
            'Mumbai': mumbai_counts,
            'Shirpur': shirpur_counts
        }).fillna(0)
        
        # Create grouped bar chart
        fig = go.Figure()
        
        # Add bars for Mumbai
        fig.add_trace(go.Bar(
            name='Mumbai',
            x=branch_comparison.index,
            y=branch_comparison['Mumbai'],
            text=branch_comparison['Mumbai'].astype(int),
            textposition='auto',
        ))
        
        # Add bars for Shirpur
        fig.add_trace(go.Bar(
            name='Shirpur',
            x=branch_comparison.index,
            y=branch_comparison['Shirpur'],
            text=branch_comparison['Shirpur'].astype(int),
            textposition='auto',
        ))
        
        # Update layout
        fig.update_layout(
            title='Branch-wise Distribution: Mumbai vs Shirpur',
            xaxis_title='Branch',
            yaxis_title='Number of Students',
            barmode='group',
            height=500
        )
        
        display_plotly_chart(fig)
        
        # Add percentage distribution table
        st.write("#### Percentage Distribution by Campus")
        total_mumbai = branch_comparison['Mumbai'].sum()
        total_shirpur = branch_comparison['Shirpur'].sum()
        
        branch_comparison['Mumbai %'] = (branch_comparison['Mumbai'] / total_mumbai * 100).round(2)
        branch_comparison['Shirpur %'] = (branch_comparison['Shirpur'] / total_shirpur * 100).round(2)
        
        # Format percentage columns
        branch_comparison['Mumbai %'] = branch_comparison['Mumbai %'].map(lambda x: f"{x}%")
        branch_comparison['Shirpur %'] = branch_comparison['Shirpur %'].map(lambda x: f"{x}%")
        
        display_secure_dataframe(branch_comparison)
    
    tab_index = 2 if has_major else 1
    with tabs[tab_index]:
        st.write("#### Career and Placement Insights")
        
        # MIP Company distribution by Branch and Campus
        col1, col2 = st.columns(2)
        
        with col1:
            # Top companies by branch
            branch_company = pd.crosstab(df['BRANCH'], df['MIP Company'])
            top_companies_branch = branch_company.sum().sort_values(ascending=False).head(5)
            
            fig = px.bar(
                x=top_companies_branch.index,
                y=top_companies_branch.values,
                title="Top 5 Companies Overall",
                labels={'x': 'Company', 'y': 'Number of Students'}
            )
            display_plotly_chart(fig)
        
        with col2:
            # Branch-wise placement distribution
            branch_placement = df.groupby('BRANCH')['MIP Company'].nunique()
            fig = px.pie(
                values=branch_placement.values,
                names=branch_placement.index,
                title="Branch-wise Company Distribution",
                hole=0.4
            )
            display_plotly_chart(fig)

def create_subject_trend_analysis(df, semester):
    """
    Create comprehensive subject trend analysis
    """
    st.write(f"### {semester} Subject Analysis")
    
    subject_cols = [col for col in df.columns if col.startswith(f"Sub {semester}")]
    
    # Create a long format dataframe for all subjects
    all_subjects_data = pd.DataFrame()
    for sub in subject_cols:
        sub_counts = df[sub].value_counts().reset_index()
        sub_counts.columns = ["Subject", "Count"]
        sub_counts["Subject Code"] = sub
        all_subjects_data = pd.concat([all_subjects_data, sub_counts])
    
    # Get top subjects by enrollment
    top_subjects = all_subjects_data.nlargest(10, "Count")
    
    # Create visualization
    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=("Top 10 Subjects", "Subject Distribution"),
                        specs=[[{"type": "bar"}, {"type": "pie"}]])
    
    # Bar chart for top 10 subjects
    fig.add_trace(
        go.Bar(x=top_subjects["Subject"], y=top_subjects["Count"],
               text=top_subjects["Count"], textposition='auto'),
        row=1, col=1
    )
    
    # Pie chart for distribution
    fig.add_trace(
        go.Pie(labels=top_subjects["Subject"], values=top_subjects["Count"],
               hole=0.4),
        row=1, col=2
    )
    
    fig.update_layout(height=500, showlegend=False)
    display_plotly_chart(fig)
    
    # Subject popularity by branch
    st.write("#### Subject Popularity by Branch")
    top_5_subjects = top_subjects.head()["Subject"].tolist()
    branch_subject_data = []
    
    for subject in top_5_subjects:
        for branch in df["BRANCH"].unique():
            branch_data = df[df["BRANCH"] == branch]
            count = 0
            for sub_col in subject_cols:
                count += len(branch_data[branch_data[sub_col] == subject])
            branch_subject_data.append({
                "Subject": subject,
                "Branch": branch,
                "Count": count
            })
    
    branch_subject_df = pd.DataFrame(branch_subject_data)
    fig = px.density_heatmap(
        branch_subject_df,
        x="Branch",
        y="Subject",
        z="Count",
        title="Subject Popularity Across Branches"
    )
    display_plotly_chart(fig)

def create_mba26_advanced_analytics(df):
    """
    Create advanced analytics specifically for MBA.Tech '26 batch
    """
    st.write("### Advanced Analytics for MBA.Tech '26")
    
    # Create tabs for different analyses
    tabs = st.tabs([
        "Branch & Campus Analysis",
        "Placement Insights",
        "Division Analysis",
        "Contact Information Analysis"
    ])
    
    with tabs[0]:
        st.write("#### Branch and Campus Distribution Analysis")
        
        # Branch distribution by campus with percentage
        branch_campus_dist = pd.crosstab(
            df['BRANCH'], 
            df['CAMPUS'], 
            margins=True, 
            margins_name='Total'
        )
        
        # Calculate percentages
        branch_campus_pct = pd.crosstab(
            df['BRANCH'], 
            df['CAMPUS'], 
            normalize='columns',
            margins=True,
            margins_name='Total'
        ) * 100
        
        # Create a comparison visualization
        fig = go.Figure()
        
        campuses = df['CAMPUS'].unique()
        branches = df['BRANCH'].unique()
        
        for campus in campuses:
            campus_data = []
            for branch in branches:
                count = len(df[(df['CAMPUS'] == campus) & (df['BRANCH'] == branch)])
                campus_data.append(count)
            
            fig.add_trace(go.Bar(
                name=campus,
                x=branches,
                y=campus_data,
                text=[f"{x}" for x in campus_data],
                textposition='auto',
            ))
        
        fig.update_layout(
            title='Branch Distribution Across Campuses',
            xaxis_title='Branch',
            yaxis_title='Number of Students',
            barmode='group',
            height=500
        )
        
        display_plotly_chart(fig)
        
        # Display detailed statistics
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("##### Raw Numbers")
            st.dataframe(branch_campus_dist, use_container_width=True)
        
        with col2:
            st.write("##### Percentage Distribution")
            st.dataframe(branch_campus_pct.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)
    
    with tabs[1]:
        st.write("#### Placement Analysis")
        
        # Company distribution analysis
        col1, col2 = st.columns(2)
        
        with col1:
            # Top companies overall
            company_counts = df['MIP Company'].value_counts().head(10)
            fig = px.bar(
                x=company_counts.index,
                y=company_counts.values,
                title='Top 10 Companies by Student Count',
                labels={'x': 'Company', 'y': 'Number of Students'},
                text=company_counts.values
            )
            fig.update_traces(textposition='auto')
            display_plotly_chart(fig)
        
        with col2:
            # Company distribution by campus
            campus_company = pd.crosstab(df['CAMPUS'], df['MIP Company'])
            company_by_campus = campus_company.sum(axis=0).sort_values(ascending=False).head(10)
            
            fig = px.pie(
                values=company_by_campus.values,
                names=company_by_campus.index,
                title='Top 10 Companies Distribution',
                hole=0.4
            )
            display_plotly_chart(fig)
        
        # Branch-wise company distribution
        branch_company_dist = pd.crosstab(df['BRANCH'], df['MIP Company'])
        
        # Create heatmap
        fig = px.imshow(
            branch_company_dist,
            title='Branch-wise Company Distribution Heatmap',
            labels=dict(x='Company', y='Branch', color='Number of Students'),
            aspect='auto'
        )
        display_plotly_chart(fig)
    
    with tabs[2]:
        st.write("#### Division Analysis")
        
        # Division distribution across branches and campuses
        col1, col2 = st.columns(2)
        
        with col1:
            # Division distribution by branch
            div_branch = pd.crosstab(df['Div'], df['BRANCH'])
            fig = px.bar(
                div_branch,
                title='Division Distribution by Branch',
                barmode='group',
                labels={'value': 'Number of Students', 'Div': 'Division'}
            )
            display_plotly_chart(fig)
        
        with col2:
            # Division distribution by campus
            div_campus = pd.crosstab(df['Div'], df['CAMPUS'])
            fig = px.pie(
                values=df['Div'].value_counts().values,
                names=df['Div'].value_counts().index,
                title='Overall Division Distribution',
                hole=0.4
            )
            display_plotly_chart(fig)
        
        # Detailed division statistics
        div_stats = pd.crosstab(
            [df['Div'], df['BRANCH']], 
            df['CAMPUS'], 
            margins=True,
            margins_name='Total'
        )
        st.write("#### Detailed Division Statistics")
        st.dataframe(div_stats, use_container_width=True)
    
    with tabs[3]:
        st.write("#### Contact Information Analysis")
        
        # Function to check email pattern
        def is_valid_email(email):
            return "@" in email and "." in email and email != "Not Assigned"
        
        # Function to check contact number pattern
        def is_valid_contact(contact):
            return len(str(contact).replace(" ", "")) >= 10 and contact != "Not Assigned"
        
        # Calculate completeness metrics
        total_students = len(df)
        email_complete = sum(df['NMIMS Email ID'].apply(is_valid_email))
        contact_complete = sum(df['Contact No.'].apply(is_valid_contact))
        
        # Create metrics display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Students",
                total_students
            )
        
        with col2:
            st.metric(
                "Email Information Complete",
                f"{email_complete} ({(email_complete/total_students*100):.1f}%)"
            )
        
        with col3:
            st.metric(
                "Contact Information Complete",
                f"{contact_complete} ({(contact_complete/total_students*100):.1f}%)"
            )
        
        # Contact information completeness by branch and campus
        st.write("#### Contact Information Completeness by Branch")
        
        # Calculate completeness by branch
        branch_stats = df.groupby('BRANCH').agg({
            'NMIMS Email ID': lambda x: sum(x.apply(is_valid_email)),
            'Contact No.': lambda x: sum(x.apply(is_valid_contact)),
            'BRANCH': 'count'
        }).rename(columns={'BRANCH': 'Total'})
        
        branch_stats['Email %'] = (branch_stats['NMIMS Email ID'] / branch_stats['Total'] * 100).round(1)
        branch_stats['Contact %'] = (branch_stats['Contact No.'] / branch_stats['Total'] * 100).round(1)
        
        # Format percentage columns
        branch_stats['Email %'] = branch_stats['Email %'].apply(lambda x: f"{x}%")
        branch_stats['Contact %'] = branch_stats['Contact %'].apply(lambda x: f"{x}%")
        
        st.dataframe(branch_stats, use_container_width=True)

def create_major_company_analysis(df):
    """
    Create major-wise company distribution analysis with interactive company filter
    """
    st.write("### Major-wise Company Distribution Analysis")
    
    # Get unique companies
    companies = sorted(df["MIP Company"].unique().tolist())
    
    # Create a multiselect with search for companies
    selected_companies = st.multiselect(
        "Select Companies to Analyze",
        companies,
        default=companies[:5],  # Default to top 5 companies
        help="You can search and select multiple companies to analyze their distribution across majors"
    )
    
    if selected_companies:
        # Create filtered dataframe
        company_major_data = []
        for company in selected_companies:
            for major in df["Major"].unique():
                count = len(df[(df["MIP Company"] == company) & (df["Major"] == major)])
                company_major_data.append({
                    "Company": company,
                    "Major": major,
                    "Count": count
                })
        
        company_major_df = pd.DataFrame(company_major_data)
        
        # Create visualizations
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create heatmap
            fig = px.imshow(
                pd.pivot_table(
                    company_major_df,
                    values="Count",
                    index="Major",
                    columns="Company"
                ),
                title="Major-Company Distribution Heatmap",
                labels=dict(x="Company", y="Major", color="Number of Students"),
                aspect="auto",
                height=400
            )
            display_plotly_chart(fig)
        
        with col2:
            # Create summary pie chart
            company_totals = company_major_df.groupby("Company")["Count"].sum()
            fig = px.pie(
                values=company_totals.values,
                names=company_totals.index,
                title="Selected Companies Distribution",
                hole=0.4
            )
            fig.update_layout(height=400)
            display_plotly_chart(fig)
        
        # Add Company Preference Analysis
        st.write("### Company Major Preferences")
        
        # Calculate percentage distribution for each company
        company_preferences = []
        for company in selected_companies:
            company_data = df[df["MIP Company"] == company]
            if not company_data.empty:
                total_students = len(company_data)
                for major in df["Major"].unique():
                    major_count = len(company_data[company_data["Major"] == major])
                    if major_count > 0:  # Only include majors with students
                        percentage = (major_count / total_students) * 100
                        company_preferences.append({
                            "Company": company,
                            "Major": major,
                            "Percentage": percentage,
                            "Count": major_count,
                            "Total": total_students
                        })
        
        pref_df = pd.DataFrame(company_preferences)
        
        # Create stacked bar chart
        fig = go.Figure()
        
        # Add bars for each major
        for major in df["Major"].unique():
            major_data = pref_df[pref_df["Major"] == major]
            if not major_data.empty:
                fig.add_trace(go.Bar(
                    name=major,
                    x=major_data["Company"],
                    y=major_data["Percentage"],
                    text=[f"{p:.1f}%" for p in major_data["Percentage"]],
                    textposition="inside",
                    hovertemplate="<br>".join([
                        "Company: %{x}",
                        "Major: " + major,
                        "Percentage: %{text}",
                        "Count: %{customdata[0]}",
                        "Total Students: %{customdata[1]}"
                    ]),
                    customdata=major_data[["Count", "Total"]].values
                ))
        
        fig.update_layout(
            title="Major Distribution within Companies",
            xaxis_title="Company",
            yaxis_title="Percentage of Students",
            barmode="stack",
            height=500,
            showlegend=True,
            legend_title="Major",
            yaxis=dict(tickformat=".1f", ticksuffix="%")
        )
        
        display_plotly_chart(fig)
        
        # Detailed statistics
        st.write("#### Detailed Statistics")
        
        # Create cross tab with percentages
        cross_tab = pd.crosstab(
            df[df["MIP Company"].isin(selected_companies)]["Major"],
            df[df["MIP Company"].isin(selected_companies)]["MIP Company"],
            margins=True,
            margins_name="Total"
        )
        
        # Calculate percentages
        percentage_tab = pd.crosstab(
            df[df["MIP Company"].isin(selected_companies)]["Major"],
            df[df["MIP Company"].isin(selected_companies)]["MIP Company"],
            normalize="columns",
            margins=True,
            margins_name="Total"
        ) * 100
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("##### Raw Numbers")
            st.dataframe(cross_tab, use_container_width=True)
        
        with col2:
            st.write("##### Percentage Distribution")
            st.dataframe(percentage_tab.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)
        
        # Additional insights
        st.write("#### Key Insights")
        
        # Most popular major for each company
        top_majors = pd.DataFrame()
        for company in selected_companies:
            company_data = df[df["MIP Company"] == company]
            if not company_data.empty:
                major_counts = company_data["Major"].value_counts()
                top_major = major_counts.index[0]
                top_count = major_counts.values[0]
                total_count = len(company_data)
                percentage = (top_count / total_count) * 100
                
                top_majors = pd.concat([top_majors, pd.DataFrame({
                    "Company": [company],
                    "Top Major": [top_major],
                    "Count": [top_count],
                    "Total Students": [total_count],
                    "Percentage": [f"{percentage:.1f}%"]
                })])
        
        st.dataframe(
            top_majors.set_index("Company"),
            use_container_width=True
        )
    else:
        st.warning("Please select at least one company to analyze.")

def create_major_subject_analysis(df, semester):
    """
    Create subject analysis based on majors
    """
    st.write(f"### {semester} Subject Analysis by Major")
    
    # Get subject columns for the selected semester
    subject_cols = [col for col in df.columns if col.startswith(f"Sub {semester}")]
    
    # Get unique majors
    majors = sorted(df["Major"].unique().tolist())
    
    # Create major selector
    selected_majors = st.multiselect(
        "Select Majors to Analyze",
        majors,
        default=majors,
        help="You can select specific majors to analyze their subject preferences"
    )
    
    if selected_majors:
        # Create subject preference data
        subject_pref_data = []
        
        for major in selected_majors:
            major_students = df[df["Major"] == major]
            total_students = len(major_students)
            
            for subject_col in subject_cols:
                subject_counts = major_students[subject_col].value_counts()
                for subject, count in subject_counts.items():
                    if subject != "Not Selected" and subject != "Not Assigned":
                        percentage = (count / total_students) * 100
                        subject_pref_data.append({
                            "Major": major,
                            "Subject": subject,
                            "Count": count,
                            "Total Students": total_students,
                            "Percentage": percentage
                        })
        
        if subject_pref_data:
            pref_df = pd.DataFrame(subject_pref_data)
            
            # Create visualizations
            st.write("#### Subject Preferences by Major")
            
            # Create a heatmap of subject preferences
            pivot_table = pd.pivot_table(
                pref_df,
                values="Percentage",
                index="Major",
                columns="Subject",
                fill_value=0
            )
            
            fig = px.imshow(
                pivot_table,
                title="Subject Preference Heatmap",
                labels=dict(x="Subject", y="Major", color="Percentage of Students"),
                aspect="auto",
                height=400,
                color_continuous_scale="YlOrRd"
            )
            
            # Update colorbar
            fig.update_traces(hoverongaps=False)
            fig.update_layout(
                coloraxis_colorbar=dict(
                    title="Percentage",
                    ticksuffix="%"
                )
            )
            
            display_plotly_chart(fig)
            
            # Top subjects for each major
            st.write("#### Top Subjects by Major")
            
            for major in selected_majors:
                major_data = pref_df[pref_df["Major"] == major]
                if not major_data.empty:
                    st.write(f"##### {major} Major")
                    
                    # Sort subjects by percentage
                    top_subjects = major_data.sort_values("Percentage", ascending=False).head(5)
                    
                    # Create horizontal bar chart
                    fig = go.Figure()
                    fig.add_trace(go.Bar(
                        y=top_subjects["Subject"],
                        x=top_subjects["Percentage"],
                        orientation='h',
                        text=[f"{p:.1f}% ({c} students)" for p, c in zip(top_subjects["Percentage"], top_subjects["Count"])],
                        textposition='auto',
                    ))
                    
                    fig.update_layout(
                        title=f"Top 5 Subjects for {major} Major",
                        xaxis_title="Percentage of Students",
                        yaxis_title="Subject",
                        height=300,
                        xaxis=dict(ticksuffix="%"),
                        showlegend=False
                    )
                    
                    display_plotly_chart(fig)
            
            # Subject popularity comparison
            st.write("#### Subject Popularity Comparison Across Majors")
            
            # Create grouped bar chart
            fig = go.Figure()
            
            for major in selected_majors:
                major_data = pref_df[pref_df["Major"] == major]
                if not major_data.empty:
                    fig.add_trace(go.Bar(
                        name=major,
                        x=major_data["Subject"],
                        y=major_data["Percentage"],
                        text=[f"{p:.1f}%" for p in major_data["Percentage"]],
                        textposition="auto",
                        hovertemplate="<br>".join([
                            "Subject: %{x}",
                            "Major: " + major,
                            "Percentage: %{text}",
                            "Count: %{customdata[0]}",
                            "Total Students: %{customdata[1]}"
                        ]),
                        customdata=major_data[["Count", "Total Students"]].values
                    ))
            
            fig.update_layout(
                title="Subject Selection Patterns Across Majors",
                xaxis_title="Subject",
                yaxis_title="Percentage of Students",
                barmode="group",
                height=500,
                showlegend=True,
                legend_title="Major",
                yaxis=dict(ticksuffix="%"),
                xaxis_tickangle=-45
            )
            
            display_plotly_chart(fig)
            
            # Detailed Statistics
            st.write("#### Detailed Statistics")
            
            # Create pivot table with both counts and percentages
            stats_df = pd.pivot_table(
                pref_df,
                values=["Count", "Percentage"],
                index="Subject",
                columns="Major",
                fill_value=0
            )
            
            # Format percentages
            percentage_df = stats_df["Percentage"].round(1).applymap(lambda x: f"{x}%")
            counts_df = stats_df["Count"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("##### Student Counts")
                st.dataframe(counts_df, use_container_width=True)
            
            with col2:
                st.write("##### Percentage Distribution")
                st.dataframe(percentage_df, use_container_width=True)
            
        else:
            st.warning("No subject data available for the selected majors.")
    else:
        st.warning("Please select at least one major to analyze.")

def create_company_relationship_analysis(df):
    """
    Create analysis showing relationships between companies and branch, division, and campus
    """
    st.write("### Company Relationship Analysis")
    
    # Create tabs for different analyses
    tabs = st.tabs([
        "Company-Branch Analysis",
        "Company-Division Analysis",
        "Company-Campus Analysis",
        "Combined Analysis"
    ])
    
    # Store companies list for reuse
    companies = sorted(df['MIP Company'].unique().tolist())
    
    with tabs[0]:
        st.write("#### Company Distribution by Branch")
        
        # Add company selector
        selected_companies = st.multiselect(
            "Select Companies to Analyze",
            companies,
            default=companies[:5],  # Default to first 5 companies
            key="branch_company_selector"
        )
        
        if selected_companies:
            # Filter data for selected companies
            filtered_df = df[df['MIP Company'].isin(selected_companies)]
            
            # Create cross-tabulation
            branch_company = pd.crosstab(filtered_df['BRANCH'], filtered_df['MIP Company'])
            
            # Create heatmap
            fig = px.imshow(
                branch_company,
                title='Company Distribution Across Branches',
                labels=dict(x='Company', y='Branch', color='Number of Students'),
                aspect='auto',
                height=600
            )
            display_plotly_chart(fig)
            
            # Create stacked bar chart
            fig = px.bar(
                branch_company,
                title='Branch-wise Company Distribution',
                barmode='stack',
                height=600
            )
            fig.update_layout(
                xaxis_title='Branch',
                yaxis_title='Number of Students',
                showlegend=True,
                legend_title='Company'
            )
            display_plotly_chart(fig)
            
            # Display statistics
            st.write("##### Branch-wise Company Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Raw Numbers")
                st.dataframe(branch_company, use_container_width=True)
            
            with col2:
                st.write("Percentage Distribution")
                branch_company_pct = branch_company.div(branch_company.sum(axis=1), axis=0) * 100
                st.dataframe(branch_company_pct.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)
        else:
            st.warning("Please select at least one company to analyze.")
    
    with tabs[1]:
        st.write("#### Company Distribution by Division")
        
        # Add company selector for division analysis
        selected_companies_div = st.multiselect(
            "Select Companies to Analyze",
            companies,
            default=companies[:5],  # Default to first 5 companies
            key="division_company_selector"
        )
        
        if selected_companies_div:
            # Filter data for selected companies
            filtered_df_div = df[df['MIP Company'].isin(selected_companies_div)]
            
            # Create cross-tabulation
            div_company = pd.crosstab(filtered_df_div['Div'], filtered_df_div['MIP Company'])
            
            # Create heatmap
            fig = px.imshow(
                div_company,
                title='Company Distribution Across Divisions',
                labels=dict(x='Company', y='Division', color='Number of Students'),
                aspect='auto',
                height=600
            )
            display_plotly_chart(fig)
            
            # Create stacked bar chart
            fig = px.bar(
                div_company,
                title='Division-wise Company Distribution',
                barmode='stack',
                height=600
            )
            fig.update_layout(
                xaxis_title='Division',
                yaxis_title='Number of Students',
                showlegend=True,
                legend_title='Company'
            )
            display_plotly_chart(fig)
            
            # Display statistics
            st.write("##### Division-wise Company Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Raw Numbers")
                st.dataframe(div_company, use_container_width=True)
            
            with col2:
                st.write("Percentage Distribution")
                div_company_pct = div_company.div(div_company.sum(axis=1), axis=0) * 100
                st.dataframe(div_company_pct.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)
        else:
            st.warning("Please select at least one company to analyze.")
    
    with tabs[2]:
        st.write("#### Company Distribution by Campus")
        
        # Add company selector for campus analysis
        selected_companies_campus = st.multiselect(
            "Select Companies to Analyze",
            companies,
            default=companies[:5],  # Default to first 5 companies
            key="campus_company_selector"
        )
        
        if selected_companies_campus:
            # Filter data for selected companies
            filtered_df_campus = df[df['MIP Company'].isin(selected_companies_campus)]
            
            # Create cross-tabulation
            campus_company = pd.crosstab(filtered_df_campus['CAMPUS'], filtered_df_campus['MIP Company'])
            
            # Create heatmap
            fig = px.imshow(
                campus_company,
                title='Company Distribution Across Campuses',
                labels=dict(x='Company', y='Campus', color='Number of Students'),
                aspect='auto',
                height=600
            )
            display_plotly_chart(fig)
            
            # Create stacked bar chart
            fig = px.bar(
                campus_company,
                title='Campus-wise Company Distribution',
                barmode='stack',
                height=600
            )
            fig.update_layout(
                xaxis_title='Campus',
                yaxis_title='Number of Students',
                showlegend=True,
                legend_title='Company'
            )
            display_plotly_chart(fig)
            
            # Display statistics
            st.write("##### Campus-wise Company Statistics")
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("Raw Numbers")
                st.dataframe(campus_company, use_container_width=True)
            
            with col2:
                st.write("Percentage Distribution")
                campus_company_pct = campus_company.div(campus_company.sum(axis=1), axis=0) * 100
                st.dataframe(campus_company_pct.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)
        else:
            st.warning("Please select at least one company to analyze.")
    
    with tabs[3]:
        st.write("#### Combined Company Distribution Analysis")
        
        # Add company selector for highlighting in Sankey diagrams
        selected_companies_combined = st.multiselect(
            "Select Companies to Highlight",
            companies,
            default=[companies[0]] if companies else [],  # Default to first company
            key="combined_company_selector"
        )
        
        # Create Sankey diagram data
        def prepare_sankey_data(df, dim1, dim2, highlight_companies=None):
            # Create links
            cross_tab = pd.crosstab(df[dim1], df[dim2])
            
            # Get unique values for both dimensions
            dim1_vals = df[dim1].unique()
            dim2_vals = df[dim2].unique()
            
            # Create node labels
            nodes = list(dim1_vals) + list(dim2_vals)
            
            # Create source-target pairs
            sources = []
            targets = []
            values = []
            colors = []  # Add colors for links
            
            for i, d1 in enumerate(dim1_vals):
                for j, d2 in enumerate(dim2_vals):
                    if cross_tab.loc[d1, d2] > 0:
                        sources.append(i)
                        targets.append(len(dim1_vals) + j)
                        values.append(cross_tab.loc[d1, d2])
                        
                        # Set color based on whether company is highlighted
                        if highlight_companies and d2 in highlight_companies:
                            colors.append('rgba(255, 0, 0, 0.8)')  # Red for highlighted
                        else:
                            colors.append('rgba(169, 169, 169, 0.3)')  # Light gray for others
            
            return nodes, sources, targets, values, colors
        
        # Create three Sankey diagrams
        col1, col2 = st.columns(2)
        
        with col1:
            # Branch to Company
            nodes, sources, targets, values, colors = prepare_sankey_data(
                df, 'BRANCH', 'MIP Company', selected_companies_combined
            )
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes,
                    color="lightblue"
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=colors  # Add colors to links
                )
            )])
            fig.update_layout(title_text="Branch to Company Flow", height=600)
            display_plotly_chart(fig)
        
        with col2:
            # Division to Company
            nodes, sources, targets, values, colors = prepare_sankey_data(
                df, 'Div', 'MIP Company', selected_companies_combined
            )
            fig = go.Figure(data=[go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=nodes,
                    color="lightgreen"
                ),
                link=dict(
                    source=sources,
                    target=targets,
                    value=values,
                    color=colors  # Add colors to links
                )
            )])
            fig.update_layout(title_text="Division to Company Flow", height=600)
            display_plotly_chart(fig)
        
        # Campus to Company
        nodes, sources, targets, values, colors = prepare_sankey_data(
            df, 'CAMPUS', 'MIP Company', selected_companies_combined
        )
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="black", width=0.5),
                label=nodes,
                color="lightpink"
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=colors  # Add colors to links
            )
        )])
        fig.update_layout(title_text="Campus to Company Flow", height=600)
        display_plotly_chart(fig)
        
        # Add summary statistics
        st.write("#### Summary Statistics")
        
        # Calculate diversity metrics
        def calculate_diversity_metrics(df, group_col, company_col='MIP Company'):
            metrics = []
            for group in df[group_col].unique():
                group_data = df[df[group_col] == group]
                total_students = len(group_data)
                unique_companies = len(group_data[company_col].unique())
                metrics.append({
                    'Group': group,
                    'Total Students': total_students,
                    'Unique Companies': unique_companies,
                    'Companies per Student': round(unique_companies / total_students, 2)
                })
            return pd.DataFrame(metrics)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.write("Branch Diversity")
            st.dataframe(calculate_diversity_metrics(df, 'BRANCH'), use_container_width=True)
        
        with col2:
            st.write("Division Diversity")
            st.dataframe(calculate_diversity_metrics(df, 'Div'), use_container_width=True)
        
        with col3:
            st.write("Campus Diversity")
            st.dataframe(calculate_diversity_metrics(df, 'CAMPUS'), use_container_width=True)

def create_contact_info_analysis(df):
    """
    Create analysis for contact information completeness and patterns
    """
    st.write("### Contact Information Analysis")
    
    # Create tabs for different analyses
    tabs = st.tabs([
        "Completeness Analysis",
        "Email Domain Analysis",
        "Contact Distribution",
        "Campus-wise Analysis"
    ])
    
    with tabs[0]:
        st.write("#### Data Completeness Analysis")
        
        # Function to check completeness
        def check_completeness(value):
            if pd.isna(value) or value == "Not Assigned" or value.strip() == "":
                return False
            return True
        
        # Calculate completeness metrics
        total_students = len(df)
        email_complete = sum(df['NMIMS Email ID'].apply(check_completeness))
        contact_complete = sum(df['Contact No.'].apply(check_completeness))
        
        # Create metrics display
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Total Students",
                total_students
            )
        
        with col2:
            email_percent = (email_complete/total_students*100)
            st.metric(
                "Email Information Complete",
                f"{email_complete}",
                f"{email_percent:.1f}%"
            )
        
        with col3:
            contact_percent = (contact_complete/total_students*100)
            st.metric(
                "Contact Information Complete",
                f"{contact_complete}",
                f"{contact_percent:.1f}%"
            )
        
        # Create completeness heatmap
        completeness_data = pd.DataFrame({
            'Email': df['NMIMS Email ID'].apply(check_completeness),
            'Contact': df['Contact No.'].apply(check_completeness)
        })
        
        fig = px.imshow(
            completeness_data.astype(int).T,
            title='Information Completeness Heatmap',
            labels=dict(x='Student Index', y='Information Type', color='Complete'),
            color_continuous_scale=[(0, 'red'), (1, 'green')],
            aspect='auto'
        )
        display_plotly_chart(fig)
    
    with tabs[1]:
        st.write("#### Email Domain Analysis")
        
        # Extract email domains
        def extract_domain(email):
            if pd.isna(email) or email == "Not Assigned" or email.strip() == "":
                return "Missing"
            try:
                return email.split('@')[1]
            except:
                return "Invalid Format"
        
        df['Email Domain'] = df['NMIMS Email ID'].apply(extract_domain)
        
        # Create domain distribution
        domain_counts = df['Email Domain'].value_counts()
        
        # Create visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=domain_counts.values,
                names=domain_counts.index,
                title='Email Domain Distribution',
                hole=0.4
            )
            display_plotly_chart(fig)
        
        with col2:
            fig = px.bar(
                x=domain_counts.index,
                y=domain_counts.values,
                title='Email Domain Counts',
                labels={'x': 'Domain', 'y': 'Number of Students'}
            )
            fig.update_layout(xaxis_tickangle=-45)
            display_plotly_chart(fig)
    
    with tabs[2]:
        st.write("#### Contact Number Distribution")
        
        # Analyze contact number patterns
        def analyze_contact(contact):
            if pd.isna(contact) or contact == "Not Assigned" or contact.strip() == "":
                return "Missing"
            contact = str(contact).replace(" ", "").replace("-", "").replace("+", "")
            if contact.startswith("91"):
                return "Starts with 91"
            elif len(contact) == 10:
                return "10 Digits"
            else:
                return "Other Format"
        
        df['Contact Pattern'] = df['Contact No.'].apply(analyze_contact)
        
        # Create pattern distribution
        pattern_counts = df['Contact Pattern'].value_counts()
        
        # Create visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.pie(
                values=pattern_counts.values,
                names=pattern_counts.index,
                title='Contact Number Pattern Distribution',
                hole=0.4
            )
            display_plotly_chart(fig)
        
        with col2:
            fig = px.bar(
                x=pattern_counts.index,
                y=pattern_counts.values,
                title='Contact Pattern Counts',
                labels={'x': 'Pattern', 'y': 'Number of Students'}
            )
            display_plotly_chart(fig)
    
    with tabs[3]:
        st.write("#### Campus-wise Contact Information Analysis")
        
        # Create cross-tabulation
        campus_email = pd.crosstab(
            df['CAMPUS'],
            df['NMIMS Email ID'].apply(check_completeness),
            margins=True
        )
        campus_contact = pd.crosstab(
            df['CAMPUS'],
            df['Contact No.'].apply(check_completeness),
            margins=True
        )
        
        # Calculate percentages
        campus_email_pct = campus_email.div(campus_email['All'], axis=0) * 100
        campus_contact_pct = campus_contact.div(campus_contact['All'], axis=0) * 100
        
        # Create visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("##### Email Completeness by Campus")
            fig = px.bar(
                x=campus_email_pct.index[:-1],  # Exclude 'All'
                y=campus_email_pct[True][:-1],  # Exclude 'All'
                title='Email Information Completeness by Campus',
                labels={'x': 'Campus', 'y': 'Completeness %'}
            )
            fig.update_layout(yaxis_range=[0, 100])
            display_plotly_chart(fig)
        
        with col2:
            st.write("##### Contact Completeness by Campus")
            fig = px.bar(
                x=campus_contact_pct.index[:-1],  # Exclude 'All'
                y=campus_contact_pct[True][:-1],  # Exclude 'All'
                title='Contact Information Completeness by Campus',
                labels={'x': 'Campus', 'y': 'Completeness %'}
            )
            fig.update_layout(yaxis_range=[0, 100])
            display_plotly_chart(fig)
        
        # Display detailed statistics
        st.write("#### Detailed Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Email Information")
            st.dataframe(campus_email_pct.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)
        
        with col2:
            st.write("Contact Information")
            st.dataframe(campus_contact_pct.round(2).applymap(lambda x: f"{x}%"), use_container_width=True)

# Load and display data based on selection
if batch:
    df = load_batch_data(batch)
    if df is not None:
        st.write(f"### Data for {batch}")
        
        # Add filters for MBA.Tech '25 batch
        if batch == "MBA.Tech '25":
            # Convert columns to string type and handle NaN values
            df["Div"] = df["Div"].fillna("Not Assigned").astype(str)
            df["BRANCH"] = df["BRANCH"].fillna("Not Assigned").astype(str)
            df["CAMPUS"] = df["CAMPUS"].fillna("Not Assigned").astype(str)
            df["Major"] = df["Major"].fillna("Not Assigned").astype(str)
            df["MIP Company"] = df["MIP Company"].fillna("Not Assigned").astype(str)
            df["Contact No."] = df["Contact No."].fillna("Not Assigned").astype(str)
            df["NMIMS Email ID"] = df["NMIMS Email ID"].fillna("Not Assigned").astype(str)
            
            # Add filters to sidebar
            st.sidebar.write("### Filters")
            
            # Division filter with select all
            div_filter = multiselect_with_select_all(
                "Division",
                sorted(df["Div"].unique().tolist()),
                "div_filter"
            )
            
            # Branch filter with select all
            branch_filter = multiselect_with_select_all(
                "Branch",
                sorted(df["BRANCH"].unique().tolist()),
                "branch_filter"
            )
            
            # Campus filter with select all
            campus_filter = multiselect_with_select_all(
                "Campus",
                sorted(df["CAMPUS"].unique().tolist()),
                "campus_filter"
            )
            
            # Roll No filter
            roll_no_filter = st.sidebar.text_input(
                "Roll No. (Enter comma-separated values)",
                key="roll_no_filter"
            )
            
            # SAP ID filter
            sap_id_filter = st.sidebar.text_input(
                "SAP ID (Enter comma-separated values)",
                key="sap_id_filter"
            )
            
            # Name filter
            name_filter = st.sidebar.text_input(
                "Name (Enter to search)",
                key="name_filter"
            )
            
            # Contact Number filter
            contact_filter = st.sidebar.text_input(
                "Contact No. (Enter to search)",
                key="contact_filter"
            )
            
            # NMIMS Email ID filter
            email_filter = st.sidebar.text_input(
                "NMIMS Email ID (Enter to search)",
                key="email_filter"
            )
            
            # MIP Company filter with select all
            mip_filter = multiselect_with_select_all(
                "MIP Company",
                sorted(df["MIP Company"].unique().tolist()),
                "mip_filter"
            )
            
            # Major filter with select all
            major_filter = multiselect_with_select_all(
                "Major",
                sorted(df["Major"].unique().tolist()),
                "major_filter"
            )
            
            # Create expandable section for subject filters in sidebar
            with st.sidebar.expander("Subject Filters"):
                st.write("#### Semester 9 Subjects")
                for i in range(1, 8):
                    col_name = f"Sub S9 {i}"
                    if col_name in df.columns:
                        # Convert subject column to string
                        df[col_name] = df[col_name].fillna("Not Selected").astype(str)
                        locals()[f"sub_s9_{i}_filter"] = multiselect_with_select_all(
                            f"Subject {i}",
                            sorted(df[col_name].unique().tolist()),
                            f"sub_s9_{i}_filter"
                        )
                
                st.write("#### Semester 10 Subjects")
                for i in range(8, 15):
                    col_name = f"Sub S10 {i}"
                    if col_name in df.columns:
                        # Convert subject column to string
                        df[col_name] = df[col_name].fillna("Not Selected").astype(str)
                        locals()[f"sub_s10_{i}_filter"] = multiselect_with_select_all(
                            f"Subject {i}",
                            sorted(df[col_name].unique().tolist()),
                            f"sub_s10_{i}_filter"
                        )
            
            # Apply filters
            mask = pd.Series(True, index=df.index)
            
            if div_filter:
                mask &= df["Div"].isin(div_filter)
            if branch_filter:
                mask &= df["BRANCH"].isin(branch_filter)
            if campus_filter:
                mask &= df["CAMPUS"].isin(campus_filter)
            if roll_no_filter:
                roll_nos = [x.strip().lower() for x in roll_no_filter.split(",")]
                mask &= df["Roll No."].astype(str).str.lower().isin(roll_nos)
            if sap_id_filter:
                sap_ids = [x.strip().lower() for x in sap_id_filter.split(",")]
                mask &= df["SAP ID"].astype(str).str.lower().isin(sap_ids)
            if name_filter:
                mask &= df["NAME"].str.lower().str.contains(name_filter.lower(), na=False)
            if contact_filter:
                mask &= df["Contact No."].astype(str).str.lower().str.contains(contact_filter.lower(), na=False)
            if email_filter:
                mask &= df["NMIMS Email ID"].str.lower().str.contains(email_filter.lower(), na=False)
            if mip_filter:
                mask &= df["MIP Company"].isin(mip_filter)
            if major_filter:
                mask &= df["Major"].isin(major_filter)
            
            # Apply subject filters
            for i in range(1, 8):
                col_name = f"Sub S9 {i}"
                filter_name = f"sub_s9_{i}_filter"
                if col_name in df.columns and locals()[filter_name]:
                    mask &= df[col_name].isin(locals()[filter_name])
            
            for i in range(8, 15):
                col_name = f"Sub S10 {i}"
                filter_name = f"sub_s10_{i}_filter"
                if col_name in df.columns and locals()[filter_name]:
                    mask &= df[col_name].isin(locals()[filter_name])
            
            # Create a proper copy of the filtered data
            filtered_df = df[mask].copy()
            
            # Add password protection for contact numbers
            show_contacts = False
            if 'Contact No.' in filtered_df.columns:
                st.write("### Contact Number Protection")
                show_contacts = check_password()
            
            # Create display dataframe with proper copy
            display_df = filtered_df.copy()
            if 'Contact No.' in display_df.columns:
                if not show_contacts:
                    # Show masked contact numbers if password not entered/incorrect
                    display_df['Contact No.'] = display_df['Contact No.'].apply(mask_contact_number)
            
            # Ensure all column names are strings
            display_df.columns = display_df.columns.astype(str)
            
            # Display the data
            st.write("### Data View")
            st.write(f"Showing {len(display_df)} out of {len(df)} total records")
            display_secure_dataframe(display_df)
            
            # Analysis Section
            if len(filtered_df) > 0:
                st.write("---")
                st.write("## Data Analysis")
                
                # Analysis tabs
                tabs = st.tabs([
                    "Overview", 
                    "Advanced Analytics",
                    "Major-Company Analysis",
                    "Major-Subject Analysis",
                    "Subject Analysis",
                    "Company Relationships",
                    "Contact Information Analysis" # New tab
                ])
                
                with tabs[0]:
                    create_combined_distribution_analysis(filtered_df, has_major=True)
                
                with tabs[1]:
                    create_advanced_analytics(filtered_df, has_major=True)
                
                with tabs[2]:
                    create_major_company_analysis(filtered_df)
                
                with tabs[3]:
                    semester = st.radio(
                        "Select Semester",
                        ["S9", "S10"],
                        key="major_subject_semester"
                    )
                    create_major_subject_analysis(filtered_df, semester)
                
                with tabs[4]:
                    semester = st.radio(
                        "Select Semester",
                        ["S9", "S10"],
                        key="subject_analysis_semester"
                    )
                    create_subject_trend_analysis(filtered_df, semester)
                
                with tabs[5]:
                    create_company_relationship_analysis(filtered_df)
                
                with tabs[6]: # New tab content
                    create_contact_info_analysis(filtered_df)
        else:
            # Convert columns to string type and handle NaN values
            columns_to_process = {
                "Div": "Div",
                "BRANCH": "BRANCH",
                "CAMPUS": "CAMPUS",
                "MIP Company": "MIP Company",
                "Contact No.": "Contact No.",
                "NMIMS Email ID": "NMIMS Email ID"
            }
            
            for col in columns_to_process:
                if col in df.columns:
                    df[col] = df[col].fillna("Not Assigned").astype(str)
            
            # Add filters to sidebar
            st.sidebar.write("### Filters")
            
            # Division filter with select all
            if "Div" in df.columns:
                div_filter = multiselect_with_select_all(
                    "Division",
                    sorted(df["Div"].unique().tolist()),
                    "div_filter_26"
                )
            
            # Branch filter with select all
            if "BRANCH" in df.columns:
                branch_filter = multiselect_with_select_all(
                    "Branch",
                    sorted(df["BRANCH"].unique().tolist()),
                    "branch_filter_26"
                )
            
            # Campus filter with select all
            if "CAMPUS" in df.columns:
                campus_filter = multiselect_with_select_all(
                    "Campus",
                    sorted(df["CAMPUS"].unique().tolist()),
                    "campus_filter_26"
                )
            
            # Roll No filter
            if "Roll Number" in df.columns:
                roll_no_filter = st.sidebar.text_input(
                    "Roll No. (Enter comma-separated values)",
                    key="roll_no_filter_26"
                )
            
            # SAP ID filter
            if "SAP ID" in df.columns:
                sap_id_filter = st.sidebar.text_input(
                    "SAP ID (Enter comma-separated values)",
                    key="sap_id_filter_26"
                )
            
            # Name filter
            if "NAME" in df.columns:
                name_filter = st.sidebar.text_input(
                    "Name (Enter to search)",
                    key="name_filter_26"
                )
            
            # Contact Number filter
            if "Contact No." in df.columns:
                contact_filter = st.sidebar.text_input(
                    "Contact No. (Enter to search)",
                    key="contact_filter_26"
                )
            
            # NMIMS Email ID filter
            if "NMIMS Email ID" in df.columns:
                email_filter = st.sidebar.text_input(
                    "NMIMS Email ID (Enter to search)",
                    key="email_filter_26"
                )
            
            # MIP Company filter with select all
            if "MIP Company" in df.columns:
                mip_filter = multiselect_with_select_all(
                    "MIP Company",
                    sorted(df["MIP Company"].unique().tolist()),
                    "mip_filter_26"
                )
            
            # Apply filters
            mask = pd.Series(True, index=df.index)
            
            if "Div" in df.columns and div_filter:
                mask &= df["Div"].isin(div_filter)
            if "BRANCH" in df.columns and branch_filter:
                mask &= df["BRANCH"].isin(branch_filter)
            if "CAMPUS" in df.columns and campus_filter:
                mask &= df["CAMPUS"].isin(campus_filter)
            if "Roll Number" in df.columns and roll_no_filter:
                roll_nos = [x.strip().lower() for x in roll_no_filter.split(",")]
                mask &= df["Roll Number"].astype(str).str.lower().isin(roll_nos)
            if "SAP ID" in df.columns and sap_id_filter:
                sap_ids = [x.strip().lower() for x in sap_id_filter.split(",")]
                mask &= df["SAP ID"].astype(str).str.lower().isin(sap_ids)
            if "NAME" in df.columns and name_filter:
                mask &= df["NAME"].str.lower().str.contains(name_filter.lower(), na=False)
            if "Contact No." in df.columns and contact_filter:
                mask &= df["Contact No."].astype(str).str.lower().str.contains(contact_filter.lower(), na=False)
            if "NMIMS Email ID" in df.columns and email_filter:
                mask &= df["NMIMS Email ID"].str.lower().str.contains(email_filter.lower(), na=False)
            if "MIP Company" in df.columns and mip_filter:
                mask &= df["MIP Company"].isin(mip_filter)
            
            # Display filtered data
            filtered_df = df[mask]
            
            # Add password protection for contact numbers
            show_contacts = False
            if 'Contact No.' in filtered_df.columns:
                st.write("### Contact Number Protection")
                show_contacts = check_password()
            
            # Create display dataframe
            display_df = filtered_df.copy()
            if 'Contact No.' in display_df.columns:
                if not show_contacts:
                    # Show masked contact numbers if password not entered/incorrect
                    display_df['Contact No.'] = display_df['Contact No.'].apply(mask_contact_number)
            
            # Display the data
            st.write("### Data View")
            st.write(f"Showing {len(display_df)} out of {len(df)} total records")
            display_secure_dataframe(display_df)
            
            # Add analytics section for MBA.Tech '26 if there are filtered records
            if len(filtered_df) > 0:
                st.write("---")
                st.write("## Data Analysis")
                
                # Analysis tabs
                tabs = st.tabs([
                    "Overview", 
                    "Advanced Analytics",
                    "Company Relationships"  # New tab for MBA Tech '26
                ])
                
                with tabs[0]:
                    create_combined_distribution_analysis(filtered_df, has_major=False)
                
                with tabs[1]:
                    create_contact_info_analysis(filtered_df)
                
                with tabs[2]:  # New tab content
                    create_company_relationship_analysis(filtered_df)

# Function to get base64 encoded image
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Get base64 encoded image
profile_image_base64 = get_image_base64("ProfileImage.jpg")

# Add footer with animated sphere and LinkedIn link
st.markdown(f"""
    <style>
        @keyframes rotate {{
            0% {{ transform: rotateZ(0deg); }}
            100% {{ transform: rotateZ(360deg); }}
        }}
        
        .sphere-container {{
            position: fixed;
            top: 65px;
            right: 30px;
            width: 45px;
            height: 45px;
            z-index: 9999;
        }}
        
        .sphere {{
            width: 100%;
            height: 100%;
            position: relative;
            animation: rotate 8s linear infinite;
            cursor: pointer;
            transform-origin: center center;
            z-index: 9999;
        }}
        
        .sphere-text {{
            position: absolute;
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: #0e1117;
            border-radius: 50%;
            color: white;
            font-family: 'Poppins', sans-serif;
            font-weight: 600;
            font-size: 9px;
            text-transform: lowercase;
            box-shadow: none;
            transition: all 0.4s ease;
            border: 0.5px solid white;
            letter-spacing: 0.5px;
            z-index: 9999;
        }}
        
        .sphere:hover {{
            animation-play-state: paused;
            box-shadow: 0 4px 25px rgba(255, 255, 255, 0.15);
            transform: scale(1.08) rotateZ(0deg);
        }}
        
        .sphere-text::before {{
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.05));
            border-radius: 50%;
            z-index: -1;
        }}
        
        .tooltip {{
            position: absolute;
            top: 100px;
            right: 0;
            background: #b5aca7;
            color: #000000;
            padding: 12px;
            border-radius: 12px;
            font-size: 12px;
            white-space: nowrap;
            opacity: 0;
            transition: all 0.4s ease;
            pointer-events: none;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            border: 1px solid rgba(0, 0, 0, 0.1);
            transform: translateY(10px);
            backdrop-filter: blur(5px);
            font-family: 'Montserrat', sans-serif;
            display: flex;
            align-items: center;
            gap: 12px;
            width: fit-content;
            min-width: 230px;
            z-index: 9999;
        }}
        
        .tooltip-image {{
            width: 70px;
            height: 70px;
            border-radius: 50%;
            object-fit: cover;
            border: 1px solid #000000;
            flex-shrink: 0;
        }}
        
        .tooltip-content {{
            display: flex;
            flex-direction: column;
            gap: 4px;
            flex: 1;
            min-width: 0;
            padding-right: 5px;
            color: #000000;
        }}
        
        .tooltip-content a {{
            color: #c7322b;
            text-decoration: underline;
            font-weight: 600;
            transition: all 0.3s ease;
            padding: 0 2px;
            border-radius: 3px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            font-size: 14px;
        }}
        
        .tooltip-content a:hover {{
            color: #e63946;
            background: rgba(255, 255, 255, 0.1);
        }}
        
        .sphere-container:hover .tooltip {{
            opacity: 1;
            transform: translateY(0);
        }}
    </style>
    
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&family=Montserrat:wght@400;500;700&display=swap" rel="stylesheet">
    
    <div class="sphere-container">
        <a href="https://www.linkedin.com/in/shivam-baranwal-nmims" target="_blank" style="text-decoration: none;">
            <div class="sphere">
                <div class="sphere-text">ishiv</div>
            </div>
        </a>
        <div class="tooltip">
            <img src="data:image/jpeg;base64,{profile_image_base64}" alt="Shivam" class="tooltip-image">
            <div class="tooltip-content">
                Designed & Developed by <a href="https://www.linkedin.com/in/shivam-baranwal-nmims" target="_blank" rel="noopener noreferrer">Shivam Baranwal</a>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)
