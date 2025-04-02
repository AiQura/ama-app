"""
Main entry point for the Streamlit AMA application.
"""
from auth.auth_ui import AuthUI
from auth.auth_service import AuthService
from ui.langgraph_ui import LangGraphUI
from ui.query_ui import QueryUI
from ui.link_ui import LinkUI
from ui.file_ui import FileUI
from services.ai_service import AIService
from services.link_service import LinkService
from services.file_service import FileService
from config.config import APP_TITLE, APP_ICON, APP_LAYOUT
import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def setup_page_config():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        layout=APP_LAYOUT
    )


def setup_environment_variables():
    """Check for required environment variables."""
    # Check for OpenAI API key
    if "OPENAI_API_KEY" not in os.environ:
        st.sidebar.warning(
            "⚠️ OPENAI_API_KEY not set in environment. Some AI features may not work.")

    # Check for Tavily API key
    if "TAVILY_API_KEY" not in os.environ:
        st.sidebar.warning(
            "⚠️ TAVILY_API_KEY not set in environment. Web search functionality will be limited.")


def main():
    """Main application function."""
    setup_page_config()

    # Initialize services
    auth_service = AuthService()
    file_service = FileService()
    link_service = LinkService()
    ai_service = AIService()

    # Initialize UI components
    auth_ui = AuthUI(auth_service)
    file_ui = FileUI(file_service)
    link_ui = LinkUI(link_service)
    query_ui = QueryUI(ai_service, file_ui, link_ui)
    langgraph_ui = LangGraphUI(file_service, link_service)

    # Check if user is authenticated
    if not auth_ui.is_authenticated():
        # Show login page
        auth_ui.render_login_page()
        return

    # Get current user
    current_user = auth_ui.get_current_user()

    # Setup environment variables
    setup_environment_variables()

    # Main page title
    st.title("AMA")
    st.write("Upload files, add links, and ask questions to get AI-powered answers with transparent reasoning.")

    # Sidebar for user info, logout, file upload, and link management
    with st.sidebar:
        # Show user info and logout button
        auth_ui.render_user_info()
        auth_ui.render_logout_button()

        # File upload section
        st.header("Upload Files")
        if current_user:
            with st.form(key="file_upload_form"):
                uploaded_files = st.file_uploader("Upload files", accept_multiple_files=True,
                                                  help="First upload files here, then use 'Submit' to process them")
                replace_existing = st.checkbox(
                    "Replace existing files", value=False)
                submit_button = st.form_submit_button("Upload Selected Files")

                if submit_button and uploaded_files:
                    for uploaded_file in uploaded_files:
                        # Get existing files to check for duplicates
                        existing_files = file_service.get_user_files(
                            current_user.user_id)
                        duplicate = any(
                            f.name == uploaded_file.name for f in existing_files)

                        # Handle duplicates based on user preference
                        if duplicate and not replace_existing:
                            st.warning(
                                f"File '{uploaded_file.name}' already exists. Select 'Replace existing files' option to overwrite.")
                            continue
                        elif duplicate and replace_existing:
                            # Delete existing file with the same name
                            for existing_file in existing_files:
                                if existing_file.name == uploaded_file.name:
                                    file_service.delete_file(existing_file.id)
                                    st.info(
                                        f"Replacing existing file: {uploaded_file.name}")
                                    break

                        # Add file to service
                        file_model = file_service.add_file(
                            file=uploaded_file.getbuffer(),
                            filename=uploaded_file.name,
                            file_type=uploaded_file.type,
                            user_id=current_user.user_id
                        )

                        if file_model:
                            st.success(f"Uploaded: {uploaded_file.name}")
                        else:
                            st.error(f"Failed to upload: {uploaded_file.name}")
        else:
            st.warning("Please log in to upload files")

        # Show link management
        st.header("Add Links")
        link_ui.render_add_link_section(current_user)

    # Tabs for different sections
    tab1, tab2, tab3, tab4 = st.tabs(
        ["Ask AI", "Manage Files", "Manage Links", "LangGraph RAG"])

    with tab1:
        query_ui.render_query_section(current_user)
        query_ui.render_history_section(current_user)

    with tab2:
        file_ui.render_file_management(current_user)

    with tab3:
        link_ui.render_link_management(current_user)

    with tab4:
        langgraph_ui.render_langgraph_section(current_user)

    # Footer
    st.markdown("---")
    st.caption("AMA © 2025")


if __name__ == "__main__":
    main()
