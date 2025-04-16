import os
import traceback
import streamlit as st

from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter

from modules.file.file_model import FileModel
from modules.link.link_model import LinkModel
from utils.ai_utils import check_api_key, get_retriever_id, get_chroma_client
from utils.documents import get_documents_from_files, get_documents_from_links


def vectorize(files: list[FileModel] | None = None,
                         links: list[LinkModel] | None = None,
                         force_reload: bool = False) -> bool:
    """
    Initialize or load the vector store for retrieval based on provided files and links

    Args:
        files: List of file models to include (optional)
        links: List of link models to include (optional)
        force_reload: If True, reload the vector store even if it exists

    Returns:
        A unique id to retrieve the vector
    """
    if not check_api_key():
        st.warning("⚠️ OpenAI API key required for vector store operations")
        return None

    # Generate a unique ID for this combination of files and links
    retriever_id = get_retriever_id(files or [], links or [])

    # Set up storage location
    collection_name = f"rag-chroma-{retriever_id}"
    chroma_dir = os.path.join("./.chroma", retriever_id)

    # Check if we need to build the index
    if force_reload or not os.path.exists(chroma_dir):
        print(f"Building vector store for ID {retriever_id}...")

        try:
            documents = []

            # Get documents from files if provided
            if files:
                file_docs = get_documents_from_files(files)
                documents.extend(file_docs)

            # Get documents from links if provided
            if links:
                link_docs = get_documents_from_links(links)
                documents.extend(link_docs)

            # If no files or links provided, use default URLs
            if not documents:
                print("No files or links provided, please provide a files to start")

            # Cast Document to string
            str_documents = [doc.page_content for doc in documents]

            # Split documents into chunks

            character_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", ". ", " ", ""],
                chunk_size=1000,
                chunk_overlap=0
            )
            character_split_texts = character_splitter.split_text(
                '\n\n'.join(str_documents))


            token_splitter = SentenceTransformersTokenTextSplitter(
                chunk_overlap=0, tokens_per_chunk=256)

            token_split_texts = []
            for text in character_split_texts:
                token_split_texts += token_splitter.split_text(text)

            embedding_function = SentenceTransformerEmbeddingFunction()

            chroma_client = get_chroma_client()
            chroma_collection = chroma_client.create_collection(collection_name, embedding_function=embedding_function)

            ids = [str(i) for i in range(len(token_split_texts))]

            chroma_collection.add(ids=ids, documents=token_split_texts)

            return True

        except Exception as e:
            print(f"Error building vector store: {e}")
            print(traceback.format_exc())
            st.error(f"Error building vector store: {e}")
            return False
    else:
        print(f"Loading existing vector store for ID {retriever_id}...")
        return True
