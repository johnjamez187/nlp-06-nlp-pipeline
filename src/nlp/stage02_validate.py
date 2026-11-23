"""src/nlp/stage02_validate.py - Validate Stage.

(EDIT YOUR VERSION OF THIS FILE)

Source: Raw HTML string
Sink:   BeautifulSoup object (in memory)

Purpose

  Validates that the expected page structure is present.

Analytical Questions

- What is the top-level structure of the HTML document?
- What elements are present in the document?
- What data types are associated with each field?
- Does the data meet expectations for transformation?

Edit your Python file to:
- inspect the HTML structure for your API,
- validate the presence of required HTML elements,
- confirm the data is usable for your analysis.
"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging

from bs4 import BeautifulSoup

# ============================================================
# Section 2. Define Run Validate Function
# ============================================================


def run_validate(
    html_content: str,
    LOG: logging.Logger,
) -> BeautifulSoup:
    """Inspect and validate HTML structure.

    Args:
        html_content (str): The raw HTML content from the Extract stage.
        LOG (logging.Logger): The logger instance.

    Returns:
        BeautifulSoup: The validated BeautifulSoup object.
    """
    LOG.info("========================")
    LOG.info("STAGE 02: VALIDATE starting...")
    LOG.info("========================")

    # ============================================================
    # INSPECT HTML STRUCTURE
    # ============================================================

    LOG.info("HTML STRUCTURE INSPECTION:")

    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "html.parser")

    # Log the type of the top-level HTML structure.
    LOG.info(f"Top-level type: {type(soup).__name__}")

    # Log the top-level elements in the HTML document
    LOG.info(
        f"Top-level elements: {[element.name for element in soup.find_all(recursive=False)]}"
    )

    # ============================================================
    # VALIDATE EXPECTATIONS
    # ============================================================

    # Validate the Kansas City Chiefs news article
    title = soup.find("h1")
    article = soup.find("article")
    paragraphs = article.find_all("p") if article else []

    LOG.info("VALIDATE: Title found: %s", title is not None)
    LOG.info("VALIDATE: Article found: %s", article is not None)
    LOG.info("VALIDATE: Paragraph count: %s", len(paragraphs))

    missing = []

    if not title:
        missing.append("title")
    if not article:
        missing.append("article")
    if not paragraphs:
        missing.append("article paragraphs")

    if missing:
        raise ValueError(
            f"VALIDATE: Required elements missing: {missing}. "
            "Page structure may have changed."
        )

    LOG.info("VALIDATE: HTML structure is valid.")
    LOG.info("Sink: validated BeautifulSoup object")

    return soup
