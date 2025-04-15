"""
Service for managing feedback questions in the application.
"""
import uuid
import json
from datetime import datetime
import streamlit as st

from modules.feedback.feedback_model import FeedbackModel, FeedbackQuestionModel, FeedbackUserAnswerModel
from utils.db_conenciton import db_conenciton


class FeedbackService:
    """
    Service for managing link operations.
    """

    def __init__(self):
        """Initialize the LinkService."""
        self._initialize_db()
        self._initialize_predefined_questions()

    def _initialize_db(self) -> None:
        """Initialize the database tables for link storage."""
        with db_conenciton() as cursor:
        # Create tables
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                question_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                answers TEXT NOT NULL
            )
            ''')
            cursor.execute('ALTER TABLE questions ENABLE ROW LEVEL SECURITY;')


            cursor.execute('''
            CREATE TABLE IF NOT EXISTS answers (
                answer_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                answers TEXT NOT NULL,
                comment TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            ''')
            cursor.execute('ALTER TABLE answers ENABLE ROW LEVEL SECURITY;')

    def _initialize_predefined_questions(self) -> None:
        """Initialize predefined users in the database."""
        # Load predefined users from config
        for user_data in st.secrets.feedback["PREDEFINED_QUESTIONS"]:
            question = user_data['question']
            answers = user_data['answers']

            # Check if user already exists
            with db_conenciton() as cursor:
                cursor.execute("SELECT question FROM questions WHERE question = %s", (question,))
                exists = cursor.fetchone()

            if not exists:
                # Add user to database
                self.create_question(question, answers)

    def get_all_questions(self) -> list[FeedbackQuestionModel]:
        """
        Get all questions.

        Returns:
            List[FeedbackQuestionModel]: List of all question models
        """
        try:
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    SELECT question_id, question, answers
                    FROM questions
                    """
                )

                rows = cursor.fetchall()

            questions: list[FeedbackQuestionModel] = []
            for row in rows:
                question_id, question, answers = row

                questions.append(FeedbackQuestionModel(
                    id=question_id,
                    question=question,
                    answers=json.loads(answers),
                ))

            return questions
        except Exception as e:
            print(f"Error getting all questions: {e}")
            return []

    def delete_question(self, question_id: str) -> bool:
        """
        Delete a question and all its alnswers.

        Args:
            question_id: ID of the question

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with db_conenciton() as cursor:
                cursor.execute("DELETE FROM questions WHERE question_id = %s", (question_id,))

            return True
        except Exception as e:
            print(f"Error deleting link: {e}")
            return False


    def create_question(self, question: str, answers: list[str]) -> FeedbackQuestionModel:
        """
        Create a new question

        Args:
            question: The question
            answers: A list of all possible answers

        Returns:
            FeedbackQuestionModel: The added question model
        """
        try:
            # Create a new link model
            question_id = str(uuid.uuid4())

            question_model = FeedbackQuestionModel(
                id=question_id,
                question=question,
                answers=answers,
            )

            # Add to database
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    INSERT INTO questions
                    (question_id, question, answers)
                    VALUES (%s, %s, %s)
                    """,
                    (question_id, question, json.dumps(answers))
                )

            return question_model
        except Exception as e:
            print(f"Error adding question: {e}")
            return None

    def get_user_answer(self, user_id: str) -> FeedbackModel:
        """
        Get user feedback.

        Args:
            user_id: ID of the user

        Returns:
            FeedbackModel: User feedback
        """
        questions = self.get_all_questions()
        try:
            with db_conenciton() as cursor:
                cursor.execute(
                    """
                    SELECT answer_id, user_id, answers, comment, created_at
                    FROM answers
                    WHERE user_id = %s
                    """,
                    (user_id,)
                )

                feedback = cursor.fetchone()


            if feedback:
                answer_id, user_id, answers, comment, created_at = feedback
                answers = json.loads(answers)

                return FeedbackModel(
                    id=answer_id,
                    user_id=user_id,
                    comment=comment,
                    created_at=created_at,
                    answers=[FeedbackUserAnswerModel(question=question, answer=answers[question.id]) for question in questions]
                )
            else:
                return FeedbackModel(
                    id=str(uuid.uuid4()),
                    user_id=user_id,
                    comment="",
                    created_at=None,
                    answers=[FeedbackUserAnswerModel(question=question, answer="") for question in questions]
                )
        except Exception as e:
            print(f"Error getting user feedback: {e}")
            return FeedbackModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                comment="",
                created_at=None,
                answers=[FeedbackUserAnswerModel(question=question, answer="") for question in questions]
            )

    def answer_exists(self, answer_id: str) -> bool:
        try:
            with db_conenciton() as cursor:
                # Find session and check if it's expired
                cursor.execute(
                    """
                    SELECT answer_id
                    FROM answers
                    WHERE answer_id = %s
                    """,
                    (answer_id,)
                )

                data = cursor.fetchone()

            if data:
                return True

            return False
        except Exception as e:
            print(f"Error fetching answer: {e}")
            return None


    def upsert_user_answer(self, feedback: FeedbackModel) -> bool:
        answer_exists = self.answer_exists(feedback.id)

        feedback.created_at = datetime.now().isoformat()

        answers = {}
        for a in feedback.answers:
            answers[a.question.id] = a.answer

        try:
            with db_conenciton() as cursor:
                if answer_exists:
                    # Update record
                    cursor.execute(
                        """
                        UPDATE answers
                        SET user_id = %s,
                            answers = %s,
                            comment = %s,
                            created_at = %s
                        WHERE answer_id = %s
                        """,
                        (feedback.user_id, json.dumps(answers), feedback.comment, feedback.created_at, feedback.id)
                    )
                else:
                    # Insert record
                    cursor.execute(
                        "INSERT INTO answers (answer_id, user_id, answers, comment, created_at) VALUES (%s, %s, %s, %s, %s)",
                        (feedback.id, feedback.user_id, json.dumps(answers), feedback.comment, feedback.created_at)
                    )
            return True
        except Exception as e:
            print(f"Error upserting answer: {e}")
            return False



