import os
import streamlit as st
from typing import List, Optional, Any

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
from langchain_core.vectorstores.base import VectorStoreRetriever
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, TextLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings
from models.file_model import FileModel
from models.link_model import LinkModel

# Check for environment variables
def check_api_key():
    """Check if OpenAI API key is available"""
    return "OPENAI_API_KEY" in os.environ


# Global retriever instance and ID
retriever = None
current_retriever_id = None


def _get_file_loader(file_path: str, file_type: str):
    """Get the appropriate loader for a file based on its type"""
    file_extension = file_path.split(
        '.')[-1].lower() if '.' in file_path else ''

    if file_extension == 'pdf' or 'pdf' in file_type.lower():
        return PyPDFLoader(file_path)
    elif file_extension == 'csv' or 'csv' in file_type.lower():
        return CSVLoader(file_path)
    else:
        # Default to text loader for other types
        return TextLoader(file_path)


def _get_documents_from_files(files: List[FileModel]) -> List[Document]:
    """Load documents from file models"""
    documents = []

    for file in files:
        try:
            # Check if file exists
            if not os.path.exists(file.path):
                print(f"File not found: {file.path}")
                continue

            # Load documents based on file type
            loader = _get_file_loader(file.path, file.type)
            file_docs = loader.load()
            documents.extend(file_docs)
            print(f"Loaded {len(file_docs)} documents from {file.name}")
        except Exception as e:
            print(f"Error loading file {file.name}: {e}")

    return documents


def _get_documents_from_links(links: List[LinkModel]) -> List[Document]:
    """Load documents from link models"""
    documents = []

    for link in links:
        try:
            # Load documents from the URL
            loader = WebBaseLoader(link.url)
            link_docs = loader.load()

            # Add link description to metadata if available
            if link.description:
                for doc in link_docs:
                    doc.metadata['description'] = link.description

            documents.extend(link_docs)
            print(f"Loaded {len(link_docs)} documents from link: {link.url}")
        except Exception as e:
            print(f"Error loading link {link.url}: {e}")
            # Create a simple document with the URL in case of loading error
            fallback_doc = Document(
                page_content=f"Link: {link.url}\nDescription: {link.description}",
                metadata={"source": link.url, "error": str(e)}
            )
            documents.append(fallback_doc)

    return documents


def _get_retriever_id(files: List[FileModel], links: List[LinkModel]) -> str:
    """Generate a unique ID for a set of files and links"""
    # Sort and combine file IDs and link IDs
    file_ids = sorted([file.id for file in files]) if files else []
    link_ids = sorted([link.id for link in links]) if links else []

    # Generate an ID by joining all file and link IDs
    # Max is 63 Charected, we add "rag-chroma-" at the start
    retriever_id = ("_".join(file_ids + link_ids))[:52]

    # If no files or links, use "default"
    if not retriever_id:
        retriever_id = "default"

    return retriever_id


def initialize_retriever(files: Optional[List[FileModel]] = None,
                         links: Optional[List[LinkModel]] = None,
                         force_reload: bool = False) -> Optional[Any]:
    """
    Initialize or load the vector store for retrieval based on provided files and links

    Args:
        files: List of file models to include (optional)
        links: List of link models to include (optional)
        force_reload: If True, reload the vector store even if it exists

    Returns:
        A retriever instance or None if API key not available
    """
    global current_retriever_id

    if not check_api_key():
        st.warning("⚠️ OpenAI API key required for vector store operations")
        return None

    # Generate a unique ID for this combination of files and links
    retriever_id = _get_retriever_id(files or [], links or [])

    # Set up storage location
    collection_name = f"rag-chroma-{retriever_id}"
    chroma_dir = os.path.join("./.chroma", retriever_id)

    # Check if we need to build the index
    if force_reload or not os.path.exists(chroma_dir) or retriever_id != current_retriever_id:
        print(f"Building vector store for ID {retriever_id}...")

        try:
            documents = []

            # Get documents from files if provided
            if files:
                file_docs = _get_documents_from_files(files)
                documents.extend(file_docs)

            # Get documents from links if provided
            if links:
                link_docs = _get_documents_from_links(links)
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
                print((text))
                token_split_texts += token_splitter.split_text(text)

            doc_splits = token_split_texts

            if not doc_splits:
                print("No document chunks produced. Check your files/links.")
                return None

            # Create vector store - persistence is handled automatically when persist_directory is provided
            vectorstore = Chroma.from_texts(
                texts=doc_splits,
                collection_name=collection_name,
                embedding=OpenAIEmbeddings(),
                persist_directory=chroma_dir,
            )

            print(
                f"Vector store built successfully with {len(doc_splits)} chunks")

            # Create and return retriever
            retriever_instance = vectorstore.as_retriever(
                search_kwargs={"k": 4}
            )

            # Update current retriever ID
            current_retriever_id = retriever_id

            return retriever_instance

        except Exception as e:
            print(f"Error building vector store: {e}")
            st.error(f"Error building vector store: {e}")
            return None
    else:
        print(f"Loading existing vector store for ID {retriever_id}...")

        try:
            # Load existing vector store
            vectorstore = Chroma(
                collection_name=collection_name,
                persist_directory=chroma_dir,
                embedding_function=OpenAIEmbeddings(),
            )

            # Update current retriever ID
            current_retriever_id = retriever_id

            return vectorstore.as_retriever(
                search_kwargs={"k": 4}
            )
        except Exception as e:
            print(f"Error loading vector store: {e}")
            st.error(f"Error loading vector store: {e}")
            return None


def get_retriever(files: Optional[List[FileModel]] = None,
                  links: Optional[List[LinkModel]] = None) -> VectorStoreRetriever:
    """
    Get or initialize the retriever with specified files and links

    Args:
        files: List of file models to include (optional)
        links: List of link models to include (optional)
    """
    global retriever, current_retriever_id

    # Generate retriever ID for these files and links
    retriever_id = _get_retriever_id(files or [], links or [])

    # If no retriever exists or the retriever ID has changed, initialize a new one
    if retriever is None or retriever_id != current_retriever_id:
        retriever = initialize_retriever(files, links)

    return retriever
