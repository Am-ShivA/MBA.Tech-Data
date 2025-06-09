# MBA.Tech Data Viewer

A Streamlit application for viewing and analyzing MBA.Tech student data.

## Setup Instructions

1. **Local Development**:
   - Keep your Excel files (`MBA.Tech 23.xlsx`, `MBA.Tech 24.xlsx`, `MBA.Tech 25.xlsx`) on your local computer
   - Run `create_database.py` to create the SQLite database:
     ```bash
     python create_database.py
     ```
   - This will create `mba_tech_data.db` containing all your data

2. **Running Locally**:
   - Install requirements:
     ```bash
     pip install -r requirements.txt
     ```
   - Run the Streamlit app:
     ```bash
     streamlit run app.py
     ```

3. **Deployment to Streamlit Cloud**:
   - The `mba_tech_data.db` file is included in the repository
   - Excel files are not included for security
   - Deploy to Streamlit Cloud using Python 3.10

## Security Notes

- Excel files are kept local and not uploaded to GitHub
- Data is stored in SQLite database format
- The database file is included in the repository for deployment
- Users can only access the data through the Streamlit interface

## Files

- `app.py`: Main Streamlit application
- `create_database.py`: Script to create SQLite database from Excel files
- `mba_tech_data.db`: SQLite database containing all data
- `requirements.txt`: Python package dependencies
- `.streamlit/config.toml`: Streamlit configuration
- `.gitignore`: Git ignore rules (excludes Excel files)

## Features

- Secure authentication system
- Interactive data visualization
- Advanced analytics and insights
- Contact information protection
- Cross-tabulation analysis
- Subject and company relationship analysis

## Deployment

This application is deployed on Streamlit Community Cloud. To access the deployed version, please contact the administrator.

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/Am-ShivA/MBA.Tech-Data.git
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Security

- The application implements multiple layers of security:
  - Password protection for data access
  - Contact information masking
  - Download prevention
  - Right-click and keyboard shortcut disabling

## Data Protection

- Contact numbers are masked by default
- Data export functionality is disabled
- Screenshot prevention measures are implemented

## Author

Developed by [Shivam Baranwal](https://www.linkedin.com/in/shivam-baranwal-nmims) 