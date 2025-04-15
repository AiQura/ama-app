"""
UI components for link management in the Streamlit application.
"""
import streamlit as st
from typing import Optional

from modules.feedback.feedback_model import FeedbackUserAnswerModel
from modules.feedback.feedback_service import FeedbackService
from modules.auth.auth_service import User


class FeedbackUI:
    """
    UI components for feedback form.
    """

    def __init__(self, feedback_service: FeedbackService):
        """
        Initialize the FeedbackUI.

        Args:
            feedback_service: FeedbackService instance
        """
        self.feedback_service = feedback_service


    def render_feedback_form(self, current_user: Optional[User] = None) -> None:
        """
        Render the feedback from interface.

        Args:
            current_user: Currently authenticated user
        """
        st.header("Feedback")

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

            feedback.comment = st.text_area(
                "Please add your comments",
                feedback.comment,
            )

            if st.form_submit_button("Submit"):
                if not feedback.can_be_submitted():
                    st.error(f"Please answer all questions first.")
                else:
                    successful = self.feedback_service.upsert_user_answer(feedback)
                    if successful:
                        st.success("Feedback submitted successfully.")
                    else:
                        st.error(f"Failed to submit feedback.")





