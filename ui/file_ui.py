"""
UI components for file management in the Streamlit application.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional

from services.file_service import FileService
from models.file_model import FileModel
from auth.auth_service import User


class FileUI:
    """
    UI components for file management.
    """

    def __init__(self, file_service: FileService):
        """
        Initialize the FileUI.

        Args:
            file_service: FileService instance
        """
        self.file_service = file_service

    def render_upload_section(self, current_user: Optional[User] = None) -> None:
        """
        Render the file upload section.
        
        Args:
            current_user: Currently authenticated user
        """
        st.header("File Upload")
        
        if not current_user:
            st.warning("You must be logged in to upload files.")
            return
        
        uploaded_files = st.file_uploader("Upload files (clear with ✕ button)", accept_multiple_files=True, help="To upload a new version of a file that was previously deleted, first clear this uploader by clicking the ✕ button.")
        
        # Add an option to replace existing files
        replace_existing = st.checkbox("Replace existing files with the same name", value=False)
        
        if uploaded_files:
            # Track if any files were successfully uploaded
            files_uploaded = False
            
            # Process each uploaded file
            for uploaded_file in uploaded_files:
                # Get existing files to check for duplicates
                existing_files = self.file_service.get_user_files(current_user.user_id)
                duplicate = any(f.name == uploaded_file.name for f in existing_files)
                
                # Handle duplicates based on user preference
                if duplicate and not replace_existing:
                    st.warning(f"File '{uploaded_file.name}' already exists. Select 'Replace existing files' option to overwrite.")
                    continue
                elif duplicate and replace_existing:
                    # Delete existing file with the same name
                    for existing_file in existing_files:
                        if existing_file.name == uploaded_file.name:
                            self.file_service.delete_file(existing_file.id)
                            st.info(f"Replacing existing file: {uploaded_file.name}")
                            break
                
                # Add file to service
                file_model = self.file_service.add_file(
                    file=uploaded_file.getbuffer(),  # This returns a memoryview
                    filename=uploaded_file.name,
                    file_type=uploaded_file.type,
                    user_id=current_user.user_id
                )
                
                if file_model:
                    st.success(f"Uploaded: {uploaded_file.name}")
                    files_uploaded = True
                else:
                    st.error(f"Failed to upload: {uploaded_file.name}")
            
            # Only rerun once all files are processed
            if files_uploaded:
                # Using a form submit button instead of rerun() to avoid uploading the same files again
                with st.form(key="clear_uploads_form"):
                    st.text("Clear file uploader to upload more files")
                    if st.form_submit_button("Clear and continue"):
                        st.rerun()

    def render_file_management(self, current_user: Optional[User] = None) -> None:
        """
        Render the file management interface.
        
        Args:
            current_user: Currently authenticated user
        """
        st.header("Manage Uploaded Files")
        
        if not current_user:
            st.warning("You must be logged in to manage files.")
            return
        
        # Refresh file list to get the latest data
        files = self.file_service.get_user_files(current_user.user_id)
        
        if not files:
            st.info("No files uploaded yet.")
            return
        
        # Display files in a table - ensure uniqueness by using a dictionary with name as key
        unique_files = {}
        for file in files:
            # If we have multiple files with the same name, keep the most recent one
            if file.name not in unique_files or file.uploaded_at > unique_files[file.name].uploaded_at:
                unique_files[file.name] = file
        
        # Convert to list for display
        files_data = []
        for file in unique_files.values():
            files_data.append({
                "ID": file.id,
                "Name": file.name,
                "Size": f"{file.size_in_kb:.2f} KB",
                "Type": file.type,
                "Uploaded": file.uploaded_at
            })
        
        df = pd.DataFrame(files_data)
        st.dataframe(df)
        
        # File deletion
        st.subheader("Delete Files")
        
        # Create columns for file deletion
        col1, col2 = st.columns([3, 1])
        
        with col1:
            file_ids = [file.id for file in unique_files.values()]
            file_names = [f"{file.name} ({file.uploaded_at})" for file in unique_files.values()]
            
            if file_ids:
                selected_index = st.selectbox(
                    "Select a file to delete",
                    options=range(len(file_ids)),
                    format_func=lambda i: file_names[i]
                )
        
        with col2:
            if file_ids and st.button("Delete File", use_container_width=True):
                file_id = file_ids[selected_index]
                file_name = unique_files[list(unique_files.keys())[selected_index]].name
                
                if self.file_service.delete_file(file_id):
                    st.success(f"File '{file_name}' deleted successfully!")
                    
                    # Add note about the file uploader
                    st.info("Note: If you uploaded this file using the sidebar uploader, you may need to clear it by clicking the 'X' button there before uploading a new version.")
                    
                    # Create a button to refresh the page
                    if st.button("Refresh file list"):
                        st.rerun()
                else:
                    st.error("Failed to delete file.")

    def render_file_selector(self, current_user: Optional[User] = None, label: str = "Select files") -> List[FileModel]:
        """
        Render a file selector component.

        Args:
            current_user: Currently authenticated user
            label: Label for the selector

        Returns:
            List[FileModel]: List of selected files
        """
        st.subheader(label)

        if not current_user:
            st.warning("You must be logged in to select files.")
            return []

        files = self.file_service.get_user_files(current_user.user_id)
        selected_files = []

        if not files:
            st.info("No files available. Upload files from the sidebar.")
            return selected_files

        # Create a dictionary to store unique files by name
        unique_files = {}
        for file in files:
            # If we have multiple files with the same name, keep the most recent one
            if file.name not in unique_files or file.uploaded_at > unique_files[file.name].uploaded_at:
                unique_files[file.name] = file

        # Display checkboxes for unique files
        for file in unique_files.values():
            if st.checkbox(f"{file.name} ({file.uploaded_at})", key=f"file_{file.id}"):
                selected_files.append(file)

        return selected_files
