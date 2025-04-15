"""
Link model for representing external links in the application.
"""
from dataclasses import dataclass

@dataclass
class FeedbackQuestionModel:
    """
    Model representing a feedback question
    """
    id: str
    question: str
    answers: list[str]

@dataclass
class FeedbackUserAnswerModel:
    """
    Model representing a user answer for a single question
    """
    question: FeedbackQuestionModel
    answer: str


    def get_answer_index(self) -> int | None:
        """
            Returns the index of the answer
        """
        try:
            return self.question.answers.index(self.answer)
        except Exception:
            return None

@dataclass
class FeedbackModel:
    """
    Model representing a user feedback submission
    """
    id: str
    user_id: str
    answers: list[FeedbackUserAnswerModel]
    comment: str
    created_at: str | None = None

    def can_be_submitted(self):
        if self.comment is None or self.comment == "":
            return False

        for a in self.answers:
            if a.answer is None or a.answer == "":
                return False

        return True
