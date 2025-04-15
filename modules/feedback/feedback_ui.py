"""
UI components for link management in the Streamlit application.
"""
import pandas as pd
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

    def get_feedback_csv(self):
        users = self.auth_service.get_all_user()
        questions = self.feedback_service.get_all_questions()
        df = pd.DataFrame(index=[u.email for u in users], columns=[q.question for q in questions])

        for user in users:
            feedback = self.feedback_service.get_user_answer(user.user_id)
            df.at[user.email, "comment"] = feedback.comment
            for a in feedback.answers:
                df.at[user.email, a.question.question] = a.answer

        return df.to_csv().encode('utf-8')


    def render_feedback_form(self, current_user: Optional[User] = None, is_admin: bool = False) -> None:
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

        if is_admin:
            st.download_button(
                "Export all feedback to CSV",
                self.get_feedback_csv(),
                "feedback.csv",
                "text/csv",
                key='download-csv'
                )







