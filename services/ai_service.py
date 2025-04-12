"""
Service for handling AI query operations in the application.
"""
import time
import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime

from config.config import AUTH_DB_PATH
from langgraph_integration.new_graph import get_client, retrieve_documents
from models.file_model import FileModel
from models.link_model import LinkModel
from auth.auth_service import User


class AIService:
    """
    Service for handling AI queries and conversation history.
    """

    def __init__(self):
        """Initialize the AIService."""
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize the database tables for conversation history."""
        conn = sqlite3.connect(AUTH_DB_PATH)
        cursor = conn.cursor()

        # Create conversations table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            thinking TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
        ''')

        # Create conversation_files table for many-to-many relationship
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_files (
            conversation_id TEXT NOT NULL,
            file_id TEXT NOT NULL,
            PRIMARY KEY (conversation_id, file_id),
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id),
            FOREIGN KEY (file_id) REFERENCES files (file_id)
        )
        ''')

        # Create conversation_links table for many-to-many relationship
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_links (
            conversation_id TEXT NOT NULL,
            link_id TEXT NOT NULL,
            PRIMARY KEY (conversation_id, link_id),
            FOREIGN KEY (conversation_id) REFERENCES conversations (conversation_id),
            FOREIGN KEY (link_id) REFERENCES links (link_id)
        )
        ''')

        conn.commit()
        conn.close()

    def query_ai(self, query: str, user_id: str, files: Optional[List[FileModel]] = None,
                 links: Optional[List[LinkModel]] = None) -> Dict[str, Any]:
        """
        Process a query with the AI.

        Args:
            query: The user's query
            user_id: ID of the user making the query
            files: List of associated files
            links: List of associated links

        Returns:
            Dict: Result with thinking steps and response
        """
        # In a real implementation, this would call an external AI service or API
        # For now, we'll simulate the AI response

        thinking_steps = []

        openai_client = get_client()
        model = "chatgpt-4o-latest"

        retrieved_documents = retrieve_documents(query, files, links)
        information = "\n\n".join(retrieved_documents)

        ai_response = openai_client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": f"""Question: {query}

Information from document:
{information}
                """
            }],
            temperature=0.1,  # Add some creativity while keeping responses focused
            # Adjust based on your needs (Max tokens for gtp-3.5 is 4096)
            max_tokens=10000
        )
        response = ai_response.choices[0].message.content

        # # Step 1: Understanding the query
        # thinking_steps.append({
        #     "step": "Understanding the query",
        #     "content": f"Analyzing the query: '{query}'"
        # })
        # time.sleep(0.5)  # Simulate processing time

        # # Step 2: Analyzing available resources
        # resources_analysis = "Examining available resources:\n"
        # if files:
        #     resources_analysis += f"- {len(files)} files available for analysis\n"
        #     for file in files:
        #         resources_analysis += f"  - {file.name} ({file.size_in_kb:.2f} KB)\n"
        # else:
        #     resources_analysis += "- No files provided\n"

        # if links:
        #     resources_analysis += f"- {len(links)} links available for reference\n"
        #     for link in links:
        #         resources_analysis += f"  - {link.url}"
        #         if link.description:
        #             resources_analysis += f" - {link.description}"
        #         resources_analysis += "\n"
        # else:
        #     resources_analysis += "- No links provided\n"

        # thinking_steps.append({
        #     "step": "Resource Analysis",
        #     "content": resources_analysis
        # })
        # time.sleep(0.5)  # Simulate processing time

        # # Step 3: Research phase
        # thinking_steps.append({
        #     "step": "Research",
        #     "content": "Searching knowledge base for relevant information..."
        # })
        # time.sleep(0.5)  # Simulate processing time

        # # Step 4: Formulating response
        # thinking_steps.append({
        #     "step": "Formulating Response",
        #     "content": "Combining query analysis with resource information to generate a comprehensive response."
        # })
        # time.sleep(0.5)  # Simulate processing time

        # # Final response
        # response = f"Based on your query: '{query}', I've analyzed the available resources and found that..."

        # if "weather" in query.lower():
        #     response += " The current weather patterns suggest mild temperatures with a chance of rain later today."
        # elif "data" in query.lower() and files:
        #     response += " The data files you've uploaded contain valuable information that could be further analyzed with statistical methods."
        # elif "recommend" in query.lower():
        #     response += " Based on your previous queries and interests, I would recommend exploring more about machine learning algorithms."
        # else:
        #     response += " This is a general response as your query was broad. Please provide more specifics for a more tailored answer."

        # if links:
        #     response += f" I've also referenced the links you've provided, particularly {links[0].url}, which offers additional context."

        result = {
            "thinking": thinking_steps,
            "response": response
        }

        # Add to history
        self.add_to_history(query, user_id, files, links, result)

        return result

    def simple_query_ai(self, query: str, files: Optional[List[FileModel]] = None,
                        links: Optional[List[LinkModel]] = None) -> Dict[str, Any]:
        """
        Process a query with the AI.

        Args:
            query: The user's query
            user_id: ID of the user making the query
            files: List of associated files
            links: List of associated links

        Returns:
            Dict: Result with thinking steps and response
        """
        # In a real implementation, this would call an external AI service or API
        # For now, we'll simulate the AI response

        thinking_steps = []

        openai_client = get_client()
        model = "chatgpt-4o-latest"

        retrieved_documents = retrieve_documents(query, files, links)
        information = "\n\n".join(retrieved_documents)

        ai_response = openai_client.chat.completions.create(
            model=model,
            messages=[{
                "role": "user",
                "content": f"""Question: {query}

Information from document:
{information}
                """
            }],
            temperature=0.1,  # Add some creativity while keeping responses focused
            # Adjust based on your needs (Max tokens for gtp-3.5 is 4096)
            max_tokens=10000
        )
        response = ai_response.choices[0].message.content

        return {
            "question": query,
            "answer": response,
            "events": thinking_steps
        }

    def add_to_history(self, query: str, user_id: str, files: Optional[List[FileModel]],
                       links: Optional[List[LinkModel]], result: Dict[str, Any]) -> str:
        """
        Add a query to the conversation history.

        Args:
            query: The user's query
            user_id: ID of the user making the query
            files: List of associated files
            links: List of associated links
            result: The AI's result

        Returns:
            str: The conversation ID
        """
        try:
            # Generate a unique ID for the conversation
            import uuid
            conversation_id = str(uuid.uuid4())

            # Convert thinking steps to JSON string
            thinking_json = json.dumps(result["thinking"])

            # Current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Save to database
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Insert conversation
            cursor.execute(
                """
                INSERT INTO conversations
                (conversation_id, user_id, query, response, thinking, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (conversation_id, user_id, query,
                 result["response"], thinking_json, timestamp)
            )

            # Insert file associations
            if files:
                for file in files:
                    cursor.execute(
                        """
                        INSERT INTO conversation_files
                        (conversation_id, file_id)
                        VALUES (?, ?)
                        """,
                        (conversation_id, file.id)
                    )

            # Insert link associations
            if links:
                for link in links:
                    cursor.execute(
                        """
                        INSERT INTO conversation_links
                        (conversation_id, link_id)
                        VALUES (?, ?)
                        """,
                        (conversation_id, link.id)
                    )

            conn.commit()
            conn.close()

            return conversation_id
        except Exception as e:
            print(f"Error adding to history: {e}")
            return ""

    def get_user_history(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Get the conversation history for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            List: Conversation history
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            conn.row_factory = sqlite3.Row  # Enable row_factory to get column names
            cursor = conn.cursor()

            # Get conversations
            cursor.execute(
                """
                SELECT conversation_id, query, response, thinking, timestamp
                FROM conversations
                WHERE user_id = ?
                ORDER BY timestamp DESC
                """,
                (user_id,)
            )

            conversations = []
            for row in cursor.fetchall():
                conversation_id = row['conversation_id']

                # Get associated files
                cursor.execute(
                    """
                    SELECT f.file_id, f.name, f.path, f.size, f.type, f.uploaded_at
                    FROM files f
                    JOIN conversation_files cf ON f.file_id = cf.file_id
                    WHERE cf.conversation_id = ?
                    """,
                    (conversation_id,)
                )

                files = []
                for file_row in cursor.fetchall():
                    files.append({
                        'id': file_row['file_id'],
                        'name': file_row['name'],
                        'path': file_row['path'],
                        'size': file_row['size'],
                        'type': file_row['type'],
                        'uploaded_at': file_row['uploaded_at']
                    })

                # Get associated links
                cursor.execute(
                    """
                    SELECT l.link_id, l.url, l.description, l.added_at
                    FROM links l
                    JOIN conversation_links cl ON l.link_id = cl.link_id
                    WHERE cl.conversation_id = ?
                    """,
                    (conversation_id,)
                )

                links = []
                for link_row in cursor.fetchall():
                    links.append({
                        'id': link_row['link_id'],
                        'url': link_row['url'],
                        'description': link_row['description'],
                        'added_at': link_row['added_at']
                    })

                # Parse thinking JSON
                thinking = json.loads(row['thinking'])

                conversations.append({
                    'conversation_id': conversation_id,
                    'query': row['query'],
                    'response': row['response'],
                    'thinking': thinking,
                    'timestamp': row['timestamp'],
                    'selected_files': files,
                    'selected_links': links
                })

            conn.close()

            return conversations
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []

    def get_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history for all users.

        Returns:
            List: Conversation history
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            conn.row_factory = sqlite3.Row  # Enable row_factory to get column names
            cursor = conn.cursor()

            # Get conversations
            cursor.execute(
                """
                SELECT conversation_id, user_id, query, response, thinking, timestamp
                FROM conversations
                ORDER BY timestamp DESC
                """
            )

            conversations = []
            for row in cursor.fetchall():
                conversation_id = row['conversation_id']

                # Get associated files
                cursor.execute(
                    """
                    SELECT f.file_id, f.name, f.path, f.size, f.type, f.uploaded_at
                    FROM files f
                    JOIN conversation_files cf ON f.file_id = cf.file_id
                    WHERE cf.conversation_id = ?
                    """,
                    (conversation_id,)
                )

                files = []
                for file_row in cursor.fetchall():
                    files.append({
                        'id': file_row['file_id'],
                        'name': file_row['name'],
                        'path': file_row['path'],
                        'size': file_row['size'],
                        'type': file_row['type'],
                        'uploaded_at': file_row['uploaded_at']
                    })

                # Get associated links
                cursor.execute(
                    """
                    SELECT l.link_id, l.url, l.description, l.added_at
                    FROM links l
                    JOIN conversation_links cl ON l.link_id = cl.link_id
                    WHERE cl.conversation_id = ?
                    """,
                    (conversation_id,)
                )

                links = []
                for link_row in cursor.fetchall():
                    links.append({
                        'id': link_row['link_id'],
                        'url': link_row['url'],
                        'description': link_row['description'],
                        'added_at': link_row['added_at']
                    })

                # Parse thinking JSON
                thinking = json.loads(row['thinking'])

                conversations.append({
                    'conversation_id': conversation_id,
                    'user_id': row['user_id'],
                    'query': row['query'],
                    'response': row['response'],
                    'thinking': thinking,
                    'timestamp': row['timestamp'],
                    'selected_files': files,
                    'selected_links': links
                })

            conn.close()

            return conversations
        except Exception as e:
            print(f"Error getting history: {e}")
            return []

    def clear_user_history(self, user_id: str) -> bool:
        """
        Clear the conversation history for a specific user.

        Args:
            user_id: ID of the user

        Returns:
            bool: True if successful
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Get conversation IDs for this user
            cursor.execute(
                "SELECT conversation_id FROM conversations WHERE user_id = ?",
                (user_id,)
            )

            conversation_ids = [row[0] for row in cursor.fetchall()]

            # Delete associated files and links
            for conversation_id in conversation_ids:
                cursor.execute(
                    "DELETE FROM conversation_files WHERE conversation_id = ?",
                    (conversation_id,)
                )
                cursor.execute(
                    "DELETE FROM conversation_links WHERE conversation_id = ?",
                    (conversation_id,)
                )

            # Delete conversations
            cursor.execute(
                "DELETE FROM conversations WHERE user_id = ?",
                (user_id,)
            )

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error clearing user history: {e}")
            return False

    def clear_history(self) -> bool:
        """
        Clear the conversation history for all users.

        Returns:
            bool: True if successful
        """
        try:
            conn = sqlite3.connect(AUTH_DB_PATH)
            cursor = conn.cursor()

            # Delete all conversations and their associations
            cursor.execute("DELETE FROM conversation_files")
            cursor.execute("DELETE FROM conversation_links")
            cursor.execute("DELETE FROM conversations")

            conn.commit()
            conn.close()

            return True
        except Exception as e:
            print(f"Error clearing history: {e}")
            return False
