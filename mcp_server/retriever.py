"""
Document retriever using ChromaDB as an in-memory vector store.
Loads knowledge base documents, chunks them by section, and provides semantic search.
"""

import os
import re

import chromadb

from logger import get_logger
from mcp_server.models import RetrievedSnippet

logger = get_logger("MCP.Retriever")


class DocumentRetriever:
    """
    Loads markdown documents from the knowledge base directory,
    splits them into section-level chunks, and stores them in ChromaDB
    for semantic similarity search.
    """

    def __init__(self, knowledge_base_dir: str) -> None:
        """
        Initialize the retriever: load documents, chunk them, and index in ChromaDB.

        Args:
            knowledge_base_dir: Path to the directory containing .md files.
        """
        self.knowledge_base_dir = knowledge_base_dir

        # Create an in-memory ChromaDB client (no persistence needed)
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(
            name="knowledge_base",
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )

        self._load_and_index_documents()

    def _load_and_index_documents(self) -> None:
        """Load all .md files, split into sections, and add to ChromaDB."""
        md_files = sorted(
            f
            for f in os.listdir(self.knowledge_base_dir)
            if f.endswith(".md")
        )

        if not md_files:
            logger.warning("No .md files found in %s", self.knowledge_base_dir)
            return

        documents: list[str] = []
        metadatas: list[dict[str, str]] = []
        ids: list[str] = []
        chunk_id = 0

        for filename in md_files:
            filepath = os.path.join(self.knowledge_base_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = self._split_into_sections(content, filename)
            logger.info(
                "Loaded '%s': %d section(s) extracted", filename, len(chunks)
            )

            for section_title, section_text in chunks:
                # Skip very short chunks (likely just a heading with no content)
                if len(section_text.strip()) < 30:
                    continue

                documents.append(section_text.strip())
                metadatas.append({"source": filename, "section": section_title})
                ids.append(f"chunk_{chunk_id}")
                chunk_id += 1

        if documents:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
            )
            logger.info(
                "Indexed %d chunks from %d documents into ChromaDB",
                len(documents),
                len(md_files),
            )

    def _split_into_sections(
        self, content: str, filename: str
    ) -> list[tuple[str, str]]:
        """
        Split a markdown document into (section_title, section_text) chunks.
        Splits on ## headings. The content before the first ## is grouped under
        the document's # title or 'Introduction'.

        Args:
            content: Full markdown content of the document.
            filename: Name of the source file (for fallback title).

        Returns:
            List of (section_title, section_text) tuples.
        """
        chunks: list[tuple[str, str]] = []

        # Extract the document title (# heading) if present
        title_match = re.match(r"^#\s+(.+)$", content, re.MULTILINE)
        doc_title = title_match.group(1).strip() if title_match else filename

        # Split on ## headings
        sections = re.split(r"(?=^##\s+)", content, flags=re.MULTILINE)

        for section in sections:
            section = section.strip()
            if not section:
                continue

            # Check if this section starts with a ## heading
            heading_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
            if heading_match:
                section_title = heading_match.group(1).strip()
                # Get the text after the heading line
                section_text = section[heading_match.end() :].strip()
            else:
                section_title = doc_title
                # Remove the # title line if present
                section_text = re.sub(
                    r"^#\s+.+$", "", section, count=1, flags=re.MULTILINE
                ).strip()

            if section_text:
                chunks.append((section_title, section_text))

        return chunks

    def query(self, query_text: str, top_k: int = 3) -> list[RetrievedSnippet]:
        """
        Search the knowledge base for snippets relevant to the query.

        Args:
            query_text: The search query string.
            top_k: Number of top results to return.

        Returns:
            List of RetrievedSnippet objects ordered by relevance.
        """
        results = self.collection.query(
            query_texts=[query_text],
            n_results=min(top_k, self.collection.count()),
        )

        snippets: list[RetrievedSnippet] = []

        if results and results["documents"] and results["documents"][0]:
            for i, doc_text in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                distance = (
                    results["distances"][0][i] if results["distances"] else 1.0
                )

                # ChromaDB cosine distance is in [0, 2].
                # Convert to a relevance score in [0, 1]: score = 1 - (distance / 2)
                relevance_score = round(max(0.0, 1.0 - (distance / 2.0)), 4)

                snippets.append(
                    RetrievedSnippet(
                        text=doc_text,
                        source=metadata.get("source", "unknown"),
                        section=metadata.get("section", "unknown"),
                        relevance_score=relevance_score,
                    )
                )

        logger.info(
            "Query '%s' returned %d snippet(s)", query_text[:80], len(snippets)
        )
        return snippets
