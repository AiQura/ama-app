# 🤖 AMA App (Ask Me Anything In Maintenance) 🦾

A Streamlit-powered application that allows users to upload files, add external links, and ask questions to receive AI-powered responses with transparent reasoning.

## ✨ Features

- **File Management**: 📁 Upload, view, and delete files with persistent storage
- **Link Management**: 🔗 Add, view, and delete external links for reference
- **AI Queries**: 🧠 Ask questions about your content and see the reasoning process behind the answers
- **Persistent Storage**: 💾 All data is saved and available across sessions
- **Transparent AI**: 🔍 See how the AI reaches its conclusions step by step
- **Web Search**: 🤖 Perform autonomous web search on related spare parts for the related equipment

## 🗂️ Project Structure

```
streamlit_ai_app/
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
```

## 🚀 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AiQura/ama-app.git
   cd ama-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   streamlit run app.py
   ```

## 📘 How to Use

### 📁 Uploading Files
- Use the sidebar to upload files
- Files are saved to disk and can be viewed in the "Manage Files" tab

### 🔗 Adding Links
- Add external URLs from the sidebar
- Links are saved and can be viewed in the "Manage Links" tab

### 🧠 Asking Questions
- Go to the "Ask AI" tab
- Enter your query in the text area
- Select relevant files and links to include in your query
- Submit your query and view the AI's reasoning process and response

### 🔄 Managing Resources
- Use the "Manage Files" and "Manage Links" tabs to view and delete resources

## ⚙️ Implementation Notes

- The application uses Streamlit for building the user interface
- All data is stored locally in JSON files and uploaded files are saved to the `uploaded_files` directory
- The AI reasoning process can be customized to integrate with various AI APIs
- The project is structured to be modular and extensible

## 🛠️ Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🔐 License

This project is PRIVATE USE ONLY. No part of this application may be reproduced, distributed, or used by third parties. All rights reserved.

This software is provided for personal and internal use only. No license is granted for commercial or public use of this software. Any unauthorized use, reproduction, or distribution is strictly prohibited.

## 🙏 Acknowledgments

- This application was built using [Streamlit](https://streamlit.io/)
- Architecture follows a modular design pattern for easier maintenance and extension
