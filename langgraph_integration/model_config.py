"""
Central configuration for AI models used in the LangGraph RAG system.
"""
from langchain_openai import ChatOpenAI

# Default model configurations
DEFAULT_MODEL_NAME = "gpt-4o"  # Change this to "gpt-4" or any other model you want to use
DEFAULT_TEMPERATURE = 0

# Create model instances
def get_default_model():
    """Get the default model instance with standard settings"""
    return ChatOpenAI(
        model=DEFAULT_MODEL_NAME,
        temperature=DEFAULT_TEMPERATURE
    )

def get_structured_output_model():
    """Get a model instance configured for structured outputs"""
    return ChatOpenAI(
        model=DEFAULT_MODEL_NAME,
        temperature=DEFAULT_TEMPERATURE
    )

# You can add more specialized model configurations here if needed
# For example:
#
# def get_creative_model():
#     """Get a model instance with higher temperature for creative tasks"""
#     return ChatOpenAI(
#         model=DEFAULT_MODEL_NAME,
#         temperature=0.7
#     )