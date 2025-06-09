# MBA.Tech Batch Data Viewer

A Streamlit application for viewing and analyzing MBA.Tech batch data.

## Features

- Secure authentication system
- Batch-wise data analysis
- Subject enrollment analysis
- Major-Company relationship analysis
- Contact information analysis
- Advanced analytics and visualizations

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-repo-url>
cd <repo-name>
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Place your Excel files in the project directory:
   - `MBA.Tech 25.xlsx`
   - `MBA.Tech 26.xlsx`

4. Create the database:
```bash
python create_database.py
```

5. Run the application:
```bash
streamlit run app.py
```

## File Structure

- `app.py`: Main Streamlit application
- `create_database.py`: Script to create SQLite database from Excel files
- `requirements.txt`: Python package dependencies
- `runtime.txt`: Python version specification
- `.streamlit/config.toml`: Streamlit configuration

## Security Notes

- Excel files containing student data are not committed to the repository
- The application uses a SQLite database for data storage
- Authentication is required to access the application
- Contact information is masked for privacy

## Deployment

The application can be deployed on Streamlit Cloud:

1. Push your code to a private GitHub repository
2. Create a new app on Streamlit Cloud
3. Connect to your GitHub repository
4. Set the main file path to `app.py`
5. Add any required secrets in the Streamlit Cloud dashboard

## Development

- Python 3.10 or higher is required
- Use virtual environment for development
- Follow PEP 8 style guide
- Test changes locally before deploying

## License

Private - All rights reserved 