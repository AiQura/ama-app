Streamlit AMA


A Streamlit application that allows users to upload files, add links, and receive AI-powered responses with transparent reasoning.
Features

File Management: Upload, view, and delete files with persistent storage
Link Management: Add, view, and delete external links
AI Queries: Ask questions and see the reasoning process behind the answers
Persistent Storage: All data is saved and available across sessions
Transparent AI: See how the AI reaches its conclusions step by step

Project Structure
Copystreamlit_ai_app/
│
├── app.py                  # Main entry point for the application
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
│
├── config/                 # Configuration files
│   └── config.py           # App configuration settings
│
├── models/                 # Data models
│   ├── __init__.py
│   ├── file_model.py       # File handling logic
│   └── link_model.py       # Link handling logic
│
├── services/               # Business logic
│   ├── __init__.py
│   ├── ai_service.py       # AI query processing
│   ├── file_service.py     # File management
│   └── link_service.py     # Link management
│
├── ui/                     # UI components
│   ├── __init__.py
│   ├── file_ui.py          # File management UI
│   ├── link_ui.py          # Link management UI
│   └── query_ui.py         # Query UI
│
├── utils/                  # Utility functions
│   ├── __init__.py
│   └── storage.py          # Persistent storage utilities
│
└── tests/                  # Unit tests
    ├── __init__.py
    ├── conftest.py         # Test configurations
    ├── test_file_model.py
    ├── test_link_model.py
    ├── test_ai_service.py
    ├── test_file_service.py
    └── test_link_service.py
Installation

Clone the repository:

bashCopygit clone https://github.com/yourusername/streamlit-ai-app.git
cd streamlit-ai-app

Install dependencies:

bashCopypip install -r requirements.txt

Run the application:

bashCopystreamlit run app.py
How to Use

Uploading Files:

Use the sidebar to upload files
Files are saved to disk and can be viewed in the "Manage Files" tab


Adding Links:

Add external URLs from the sidebar
Links are saved and can be viewed in the "Manage Links" tab


Asking Questions:

Go to the "Ask AI" tab
Enter your query in the text area
Select relevant files and links to include in your query
Submit your query and view the AI's reasoning process and response


Managing Resources:

Use the "Manage Files" and "Manage Links" tabs to view and delete resources



Implementation Notes

The AI reasoning is currently simulated for demonstration purposes
In a production environment, you would replace the query_ai method in AIService with calls to an actual AI API
All data is stored locally in JSON files and uploaded files are saved to the uploaded_files directory

License
MIT
