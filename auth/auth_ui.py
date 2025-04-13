"""
UI components for authentication in the Streamlit application.
"""
import streamlit as st
from typing import Optional

from auth.auth_service import AuthService, User

SESSION_STATE_KEY = "authenticated_user"
SESSION_ID_KEY = "session_id"


class AuthUI:
    """UI components for authentication."""

    def __init__(self, auth_service: AuthService):
        """
        Initialize the AuthUI.

        Args:
            auth_service: AuthService instance
        """
        self.auth_service = auth_service

    def is_authenticated(self) -> bool:
        """
        Check if the user is authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        # Check if user is in session state
        if SESSION_STATE_KEY in st.session_state:
            return True

        # Check if session ID is in session state
        if SESSION_ID_KEY in st.session_state:
            session_id = st.session_state[SESSION_ID_KEY]
            user = self.auth_service.validate_session(session_id)

            if user:
                # Store user in session state
                st.session_state[SESSION_STATE_KEY] = user
                return True

        return False

    def get_current_user(self) -> Optional[User]:
        """
        Get the current authenticated user.

        Returns:
            Optional[User]: The current user or None if not authenticated
        """
        if self.is_authenticated():
            return st.session_state[SESSION_STATE_KEY]
        return None

    def render_login_page(self) -> None:
        """Render the login page."""
        st.title("Login to Artificial Maintenance Agent")

        # Create columns for layout
        col1, col2 = st.columns([1, 1])

        with col1:
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")

            if st.button("Login"):
                if email and password:
                    user = self.auth_service.authenticate(email, password)

                    if user:
                        # Create session
                        session_id = self.auth_service.create_session(user)

                        if session_id:
                            # Store in session state
                            st.session_state[SESSION_STATE_KEY] = user
                            st.session_state[SESSION_ID_KEY] = session_id
                            st.rerun()
                        else:
                            st.error(
                                "Failed to create session. Please try again.")
                    else:
                        st.error("Invalid email or password. Please try again.")
                else:
                    st.error("Please enter your email and password.")

        with col2:
            st.markdown("""
            ### Welcome
            Please enter your credentials to login to the AMA.
            """)

    def render_logout_button(self) -> None:
        """Render the logout button."""
        if st.sidebar.button("Logout"):
            # Delete session
            if SESSION_ID_KEY in st.session_state:
                self.auth_service.delete_session(
                    st.session_state[SESSION_ID_KEY])

            # Clear session state
            if SESSION_STATE_KEY in st.session_state:
                del st.session_state[SESSION_STATE_KEY]

            if SESSION_ID_KEY in st.session_state:
                del st.session_state[SESSION_ID_KEY]

            st.rerun()

    def render_user_info(self) -> None:
        """Render user information."""
        user = self.get_current_user()

        if user:
            st.sidebar.markdown(f"### Welcome, {user.name or user.email}")
            st.sidebar.markdown(f"**Email:** {user.email}")
