"""
UI components for AI queries in the Streamlit application.
"""
import streamlit as st
from typing import List, Dict, Any, Optional

from services.ai_service import AIService
from ui.file_ui import FileUI
from ui.link_ui import LinkUI
from auth.auth_service import User
from langgraph_integration.ingestion import initialize_retriever


class QueryUI:
    """
    UI components for AI queries.
    """
    
    def __init__(self, ai_service: AIService, file_ui: FileUI, link_ui: LinkUI):
        """
        Initialize the QueryUI.
        
        Args:
            ai_service: AIService instance
            file_ui: FileUI instance
            link_ui: LinkUI instance
        """
        self.ai_service = ai_service
        self.file_ui = file_ui
        self.link_ui = link_ui
    
    def render_query_section(self, current_user: Optional[User] = None) -> None:
        """
        Render the query input section.
        
        Args:
            current_user: Currently authenticated user
        """
        st.header("Ask a Question")
        
        if not current_user:
            st.warning("You must be logged in to ask questions.")
            return
        
        # Query input
        query = st.text_area("Enter your query", height=100)
        
        # Get all user files directly from database
        user_files = self.file_ui.file_service.get_user_files(current_user.user_id)
        
        if user_files:
            st.subheader("Select files to include in your query")
            
            # Group files by name and get the most recent version
            file_dict = {}
            for file in user_files:
                if file.name not in file_dict or file.uploaded_at > file_dict[file.name].uploaded_at:
                    file_dict[file.name] = file
            
            # Create a mapping of display names to file objects
            file_options = {}
            for file in file_dict.values():
                display_name = f"{file.name}"
                file_options[display_name] = file
            
            # Use st.multiselect for file selection
            if file_options:
                file_display_names = list(file_options.keys())
                selected_file_names = st.multiselect(
                    "Choose files to analyze",
                    options=file_display_names
                )
                
                # Convert selected names to file objects
                selected_files = [file_options[name] for name in selected_file_names]
            else:
                selected_files = []
                st.info("No files available. Upload files from the sidebar.")
        else:
            selected_files = []
            st.info("No files available. Upload files from the sidebar.")
        
        # Get all user links
        user_links = self.link_ui.link_service.get_user_links(current_user.user_id)
        
        if user_links:
            st.subheader("Select links to include in your query")
            
            # Create a mapping of display names to link objects
            link_options = {}
            for link in user_links:
                display_text = f"{link.url}"
                if link.description:
                    display_text += f" - {link.description}"
                link_options[display_text] = link
            
            # Use st.multiselect for link selection
            if link_options:
                link_display_names = list(link_options.keys())
                selected_link_names = st.multiselect(
                    "Choose links to reference",
                    options=link_display_names
                )
                
                # Convert selected names to link objects
                selected_links = [link_options[name] for name in selected_link_names]
            else:
                selected_links = []
                st.info("No links available. Add links from the sidebar.")
        else:
            selected_links = []
            st.info("No links available. Add links from the sidebar.")
        
        # Vector Store Settings for normal AI
        with st.expander("Vector Store Settings", expanded=False):
            build_index = st.button("Build Index from Selected Files & Links",key="normal ai")
            
            if build_index:
                if not selected_files and not selected_links:
                    st.warning("Please select at least one file or link to build the index.")
                else:
                    with st.spinner("Building vector store from selected resources..."):
                        try:
                            retriever = initialize_retriever(selected_files, selected_links, force_reload=True)
                            if retriever:
                                st.success("Vector store initialized successfully!")
                            else:
                                st.error("Failed to initialize vector store. Check API keys.")
                        except Exception as e:
                            st.error(f"Error initializing vector store: {e}")
        
        # Submit query
        if st.button("Submit Query") and query:
            # Show a spinner while "processing"
            with st.spinner("Processing your query..."):
                # Call the AI service
                result = self.ai_service.query_ai(
                    query=query,
                    user_id=current_user.user_id,
                    files=selected_files,
                    links=selected_links
                )
            
            # Display thinking process
            st.subheader("AI Reasoning Process")
            for step in result["thinking"]:
                with st.expander(f"Step: {step['step']}", expanded=True):
                    st.write(step["content"])
            
            # Display final response
            st.subheader("AI Response")
            st.write(result["response"])
    
    def render_history_section(self, current_user: Optional[User] = None) -> None:
        """
        Render the conversation history section.
        
        Args:
            current_user: Currently authenticated user
        """
        if not current_user:
            return
        
        history = self.ai_service.get_user_history(current_user.user_id)
        
        if not history:
            return
        
        st.header("Conversation History")
        
        for i, item in enumerate(history):
            with st.expander(f"Query: {item['query']} ({item['timestamp']})", expanded=i==0):
                st.write("**Files used:**")
                if item['selected_files']:
                    for file in item['selected_files']:
                        st.write(f"- {file['name']}")
                else:
                    st.write("- None")
                
                st.write("**Links used:**")
                if item['selected_links']:
                    for link in item['selected_links']:
                        st.write(f"- {link['url']}")
                else:
                    st.write("- None")
                
                st.write("**AI Response:**")
                st.write(item['response'])
                
                if st.button("Show reasoning", key=f"reasoning_{i}"):
                    for step in item['thinking']:
                        st.write(f"**{step['step']}:**")
                        st.write(step['content'])
        
        # Add button to clear history
        if st.button("Clear Conversation History"):
            if self.ai_service.clear_user_history(current_user.user_id):
                st.success("Conversation history cleared!")
                st.rerun()
            else:
                st.error("Failed to clear conversation history.")

