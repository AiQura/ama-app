"""
UI components for link management in the Streamlit application.
"""
import json
import streamlit as st
from typing import Optional

from modules.feedback.feedback_service import FeedbackService
from modules.auth.auth_service import AuthService, User


class FeedbackUI:
    """
    UI components for feedback form.
    """

    def __init__(self, feedback_service: FeedbackService, auth_service: AuthService):
        """
        Initialize the FeedbackUI.

        Args:
            feedback_service: FeedbackService instance
            auth_service: AuthService instance
        """
        self.feedback_service = feedback_service
        self.auth_service = auth_service

    def get_feedback_json(self):
        users = self.auth_service.get_all_user()
        data = {}

        for user in users:
            data[user.email] = {}
            feedback = self.feedback_service.get_user_answer(user.user_id)
            for a in feedback.answers:
                data[user.email][a.question.question] = {}
                data[user.email][a.question.question]['answer'] = a.answer
                data[user.email][a.question.question]['comment'] = a.comment

        return json.dumps(data, indent=4)

    def render_feedback_form(self, current_user: Optional[User] = None, is_admin: bool = False) -> None:
        """
        Render the feedback from interface.

        Args:
            current_user: Currently authenticated user
        """
        st.header("Feedback")
        st.write("You have used two different models One AI and Agents AI, please answer the following questions accordingly")

        if not current_user:
            st.warning("You must be logged in to give feedback.")
            return

        # Refresh links to get the latest data
        feedback = self.feedback_service.get_user_answer(current_user.user_id)

        with st.form("Feedback"):

            for a in feedback.answers:
                a.answer = st.radio(
                    a.question.question,
                    a.question.answers,
                    index=a.get_answer_index(),
                )
                a.comment = st.text_area(
                    "Comment",
                    a.comment,
                    key=a.question.id
                )

            feedback.comment = st.text_area(
                "Please add your general feedback",
                feedback.comment,
            )

            if st.form_submit_button("Submit"):
                if not feedback.can_be_submitted():
                    st.error(f"Please answer all questions first.")
                else:
                    successful = self.feedback_service.upsert_user_answer(
                        feedback)
                    if successful:
                        st.success("Feedback submitted successfully.")
                    else:
                        st.error(f"Failed to submit feedback.")

        if is_admin:
            st.download_button(
                "Export all feedback to JSON",
                self.get_feedback_json(),
                "feedback.json",
                "application/json",
                key='download-json'
            )
