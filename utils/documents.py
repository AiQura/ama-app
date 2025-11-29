
import os
from langchain_core.documents import Document
from langchain_community.document_loaders import WebBaseLoader, PyPDFLoader, TextLoader, CSVLoader

from modules.file.file_model import FileModel
from modules.link.link_model import LinkModel

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


def get_documents_from_files(files: list[FileModel]) -> list[Document]:
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


def get_documents_from_links(links: list[LinkModel]) -> list[Document]:
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
