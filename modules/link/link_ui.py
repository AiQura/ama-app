"""
UI components for link management in the Streamlit application.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional

from modules.link.link_service import LinkService
from modules.link.link_model import LinkModel
from modules.auth.auth_service import User


class LinkUI:
    """
    UI components for link management.
    """

    def __init__(self, link_service: LinkService):
        """
        Initialize the LinkUI.

        Args:
            link_service: LinkService instance
        """
        self.link_service = link_service

    def render_add_link_section(self, current_user: Optional[User] = None) -> None:
        """
        Render the section for adding new links.

        Args:
            current_user: Currently authenticated user
        """
        st.header("Link Management")

        if not current_user:
            st.warning("You must be logged in to add links.")
            return

        # Add new link
        new_link = st.text_input("Add a new link (URL)")
        link_description = st.text_input("Link description (optional)")

        if st.button("Add Link") and new_link:
            link_model = self.link_service.add_link(
                url=new_link,
                description=link_description,
                user_id=current_user.user_id
            )

            if link_model:
                st.success(f"Added link: {new_link}")
                st.rerun()
            else:
                st.error(
                    "Please enter a valid URL starting with http:// or https://")

    def render_link_management(self, current_user: Optional[User] = None) -> None:
        """
        Render the link management interface.

        Args:
            current_user: Currently authenticated user
        """
        st.header("Manage Links")

        if not current_user:
            st.warning("You must be logged in to manage links.")
            return

        # Refresh links to get the latest data
        links = self.link_service.get_user_links(current_user.user_id)

        if not links:
            st.info("No links added yet.")
            return

        # Display links in a table
        links_data = []
        for link in links:
            links_data.append({
                "ID": link.id,
                "URL": link.url,
                "Description": link.description,
                "Added": link.added_at
            })

        df = pd.DataFrame(links_data)
        st.dataframe(df)

        # Link deletion
        st.subheader("Delete Links")

        # Create columns for link deletion
        col1, col2 = st.columns([3, 1])

        with col1:
            link_ids = [link.id for link in links]
            link_names = [f"{link.url} ({link.added_at})" for link in links]

            if link_ids:
                selected_index = st.selectbox(
                    "Select a link to delete",
                    options=range(len(link_ids)),
                    format_func=lambda i: link_names[i]
                )

        with col2:
            if link_ids and st.button("Delete Link", use_container_width=True):
                link_id = link_ids[selected_index]
                link_url = links[selected_index].url

                if self.link_service.delete_link(link_id):
                    st.success(f"Link '{link_url}' deleted successfully!")

                    # Create a button to refresh the page
                    if st.button("Refresh link list"):
                        st.rerun()
                else:
                    st.error("Failed to delete link.")

    def render_link_selector(self, current_user: Optional[User] = None, label: str = "Select links") -> List[LinkModel]:
        """
        Render a link selector component.

        Args:
            current_user: Currently authenticated user
            label: Label for the selector

        Returns:
            List[LinkModel]: List of selected links
        """
        st.subheader(label)

        if not current_user:
            st.warning("You must be logged in to select links.")
            return []

        links = self.link_service.get_user_links(current_user.user_id)
        selected_links = []

        if not links:
            st.info("No links available. Add links from the sidebar.")
            return selected_links

        for link in links:
            desc = f" - {link.description}" if link.description else ""
            if st.checkbox(f"{link.url}{desc}", key=f"link_{link.id}"):
                selected_links.append(link)

        return selected_links
