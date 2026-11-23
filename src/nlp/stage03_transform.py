"""stage03_transform.py.

(EDIT YOUR VERSION OF THIS FILE)

Source: validated BeautifulSoup object
Sink:   analysis-ready Pandas DataFrame

NOTE: We use Pandas for consistency with Module 5.
You may use Polars or another library if you prefer.
The pipeline pattern is identical; only the DataFrame API differs.

======================================================================
THE ANALYST WORKFLOW: Transform is not a single step
======================================================================

In a real NLP project, Transform is an iterative loop, not a
linear sequence of operations.

The loop looks like this:

  inspect → clean → inspect → engineer → inspect → clean → repeat

We need to inspect the data to know what cleaning is needed.
We inspect the cleaner data and begin to engineer additional features.
We inspect again to see how the cleaning worked and do more as needed.

This loop continues until the data is analysis-ready,
meaning a model or analyst could use the data without being misled
by noise, inconsistency, or missing signal.

This transform module is the SETTLED VERSION of that loop.
It captures decisions that survived inspection.
It does not show the full iterative process.
You should run it, inspect the logged output at each substage,
and ask yourself:

  - Does this look cleaner than the previous step?
  - Is there still noise I should remove?
  - Am I losing signal I want to keep?
  - What derived features would help a model or analyst?

The answers often suggest more work and that increases value.
That's our workflow in action.

======================================================================
MODERN LLM Tools
======================================================================

Modern LLM tools are powerful, but only as good as the data provided.

`Garbage in, garbage out` is not a cliche.
It's why good data analysts are still very much needed.

A valuable analyst is one who understands:
  - why text needs cleaning before analysis
  - what signal looks like vs what noise looks like
  - how to inspect, iterate, and improve data quality
  - how to document those decisions so they are reproducible

The goal in this stage is to develop the judgment to know when a DataFrame
is ready for use, and to professionally document why choices were made.

Sound judgment is critical for an analyst.

======================================================================
THIS STAGE
======================================================================

This stage runs substages, each logged separately:

  Extract fields from the validated HTML into a raw DataFrame.
       Inspect: does the raw data look right?

  Clean and normalize the text fields.
       Inspect: is the text cleaner? Did we lose anything we needed?

  Engineer derived features (tokens, word count, frequency).
       Inspect: do the derived fields add signal for downstream analysis?

The final DataFrame is the settled result of these three passes.

======================================================================
PURPOSE AND ANALYTICAL QUESTIONS
======================================================================

Purpose

  Transform validated HTML into a clean, analysis-ready DataFrame.

Analytical Questions

  - What does the raw extracted text look like before cleaning?
  - What noise is present and how should it be removed?
  - What derived features would support NLP analysis?
  - How does the cleaned text differ from the raw text?
  - Is the DataFrame genuinely ready for downstream use?

Edit your Python file to:
  - inspect your own extracted text carefully
  - apply cleaning steps appropriate to the data
  - engineer features that support the analytical goals
  - document every decision with a comment explaining why
"""

# ============================================================
# Section 1. Setup and Imports
# ============================================================

import logging

from bs4 import BeautifulSoup, Tag
import pandas as pd
import spacy

# Load the small spaCy English trained pipeline (en_core_web_sm).
# It provides tokenization, stopword lists, and linguistic annotations.
# Verify "en-core-web-sm" is included with the project dependencies (see pyproject.toml).
nlp = spacy.load("en_core_web_sm")

# ============================================================
# Section 2. Define Helper Functions
# ============================================================


def _get_text(element: Tag | None, strip_prefix: str = "", separator: str = "") -> str:
    """Return element text or 'unknown' if element is None.

    Args:
        element (Tag | None): A BeautifulSoup Tag or None.
        strip_prefix (str): Text prefix to remove from the result.
        separator (str): Separator for get_text(); empty string by default.

    Returns:
        str: Extracted and cleaned text, or 'unknown' if element is None.
    """
    if element is None:
        return "unknown"
    text = element.get_text(separator=separator, strip=True)
    return text.replace(strip_prefix, "").strip() if strip_prefix else text


def _clean_text(text: str, nlp_model: spacy.language.Language) -> str:
    """Clean and normalize a text string for NLP analysis.

    Args:
        text (str): Raw text string to clean.
        nlp_model: Loaded spaCy pipeline.

    Returns:
        str: Cleaned text string.
    """
    # Step 1: Lowercase.
    # WHY: "The" and "the" are the same word for analysis purposes.
    # TRADEOFF: Proper nouns lose their case signal.
    text = text.lower()

    # Step 2: Clean text by removing stopwords, punctuation, and extra whitespace using spaCy.
    # WHY: Removing stopwords and punctuation reduces noise and focuses on meaningful content.
    # TRADEOFF: Some stopwords matter in certain contexts (e.g., "not").
    # TRADEOFF: Removing punctuation loses sentence boundary information.
    # TRADEOFF: Hyphenated terms lose their compound meaning as a unit.
    # Hyphenated terms like red-teaming are split by spaCy into red, -, teaming,
    # and the hyphen is then dropped, so no fused tokens are produced.
    doc = nlp_model(text)

    text = " ".join(
        token.text
        for token in doc
        if not (token.is_stop or token.is_punct or token.is_space)
        and token.is_ascii
        and token.text.isalnum()
    )

    return text


# ============================================================
# Section 3. Define Run Transform Function
# ============================================================


def run_transform(
    soup: BeautifulSoup,
    LOG: logging.Logger,
) -> pd.DataFrame:
    """Transform HTML into a clean, analysis-ready DataFrame.

    Args:
        soup (BeautifulSoup): Validated BeautifulSoup object.
        LOG (logging.Logger): The logger instance.

    Returns:
        pd.DataFrame: The transformed and analysis-ready dataset.
    """
    LOG.info("========================")
    LOG.info("STAGE 03: TRANSFORM starting...")
    LOG.info("========================")

    LOG.info("Extracting metadata from HTML")
    LOG.info(
        "We must manually inspect the HTML structure to identify the fields we want to extract."
    )
    LOG.info(
        "For this Kansas City Chiefs news article, we can extract:"
        "\n- Article headline from <h1>"
        "\n- Article text from paragraphs inside <article>"
        "\n- Article URL from the canonical link"
        "\n- Word counts and NLP statistics from the article text"
    )
    LOG.info("Replace any missing content with `unknown` to ensure all are strings.")

    LOG.info("========================")
    LOG.info("PHASE 3.1: Extract raw fields from HTML")
    LOG.info("========================")

    # Extract fields using the same approach as Module 5.
    # Code is refactored to use the internal function _get_text() helper.

    LOG.info("Inspect: does the raw data look right?")
    LOG.info("Look at the logged output. Does anything look surprising?")
    LOG.info("That is the first signal that cleaning is needed.")
    LOG.info("========================")

    LOG.info("------------------------")
    LOG.info("Project specific: Extract title, authors, abstract")
    LOG.info("------------------------")

    # ============================================================
    # Kansas City Chiefs News Article Extraction
    # Author: John James
    # Date: 2026-11
    # ============================================================

    # Extract the headline from the main article
    article_tag: Tag | None = soup.find("article")
    title_tag: Tag | None = article_tag.find("h1") if article_tag else None

    title: str = _get_text(title_tag)
    LOG.info(f"Extracted headline: {title}")

    # Extract the main article content
    article_tag: Tag | None = soup.find("article")
    paragraph_tags = article_tag.find_all("p") if article_tag else []

    # Combine all article paragraphs into one text document
    article_raw: str = " ".join(
        paragraph.get_text(" ", strip=True) for paragraph in paragraph_tags
    )

    LOG.info(f"Extracted article text: {article_raw[:150]}...")
    LOG.info(f"Extracted paragraph count: {len(paragraph_tags)}")

    # Extract the article's canonical URL
    canonical_tag = soup.find("link", rel="canonical")

    article_url: str = (
        str(canonical_tag.get("href", "unknown")) if canonical_tag else "unknown"
    )

    LOG.info(f"Extracted article URL: {article_url}")

    LOG.info("========================")
    LOG.info("PHASE 3.2: Clean and normalize text fields")
    LOG.info("========================")

    # Clean the Kansas City Chiefs article text.
    # Remove stopwords, punctuation, and unnecessary whitespace
    # while preserving meaningful football-related vocabulary.

    LOG.info("Inspect: compare article_raw to article_clean in the log.")
    LOG.info("Did we remove anything we should have kept?")
    LOG.info("Is there still noise that cleaning missed?")
    LOG.info("========================")

    article_clean: str = _clean_text(article_raw, nlp) if article_raw else ""

    # Log before and after to inspect the cleaning results
    LOG.info(f"  article (raw):   {article_raw[:120]}...")
    LOG.info(f"  article (clean): {article_clean[:120]}...")
    LOG.info(
        f"  characters removed: {len(article_raw) - len(article_clean)} "
        f"({100 * (1 - len(article_clean) / max(len(article_raw), 1)):.1f}%)"
    )

    LOG.info("========================")
    LOG.info("PHASE 3.3: Engineer derived features")
    LOG.info("========================")

    # Engineer features for Kansas City Chiefs news analysis.
    # Author: John James
    # Date: 2026-11
    #
    # article_word_count: words in the original article.
    # token_count: words remaining after NLP cleaning.
    # unique_token_count: number of distinct cleaned words.
    # type_token_ratio: vocabulary diversity.
    # paragraph_count: number of paragraphs in the article.

    LOG.info("Inspect: do these derived fields look meaningful?")
    LOG.info("Would any additional features help the analysis?")
    LOG.info("========================")

    # Count words in the original article
    article_word_count: int = len(article_raw.split())
    LOG.info(f"  article_word_count: {article_word_count}")

    # Count article paragraphs
    paragraph_count: int = len(paragraph_tags)
    LOG.info(f"  paragraph_count:    {paragraph_count}")

    # Tokenize the cleaned article text
    tokens: list[str] = article_clean.split()
    token_count: int = len(tokens)
    LOG.info(f"  token_count:        {token_count}")

    # Count unique cleaned tokens
    unique_token_count: int = len(set(tokens))
    LOG.info(f"  unique_token_count: {unique_token_count}")

    # Calculate vocabulary diversity
    type_token_ratio: float = (
        round(unique_token_count / token_count, 4) if token_count > 0 else 0.0
    )

    LOG.info(f"  type_token_ratio:   {type_token_ratio}")
    LOG.info(f"  first 10 tokens:    {tokens[:10]}")

    LOG.info("========================")
    LOG.info("PHASE 3.4: Build record and create DataFrame")
    LOG.info("========================")

    # Build the Kansas City Chiefs article dataset
    record = {
        "article_url": article_url,
        "title": title,
        "article_raw": article_raw,
        "article_clean": article_clean,
        "tokens": " ".join(tokens),
        "article_word_count": article_word_count,
        "paragraph_count": paragraph_count,
        "token_count": token_count,
        "unique_token_count": unique_token_count,
        "type_token_ratio": type_token_ratio,
    }

    # Create the Pandas DataFrame
    df = pd.DataFrame([record])

    LOG.info(f"Created DataFrame with {len(df)} row and {len(df.columns)} columns")
    LOG.info(f"Columns: {list(df.columns)}")

    LOG.info("DataFrame Details")
    LOG.info(f"  Title: {title}")
    LOG.info(f"  Article URL: {article_url}")
    LOG.info(f"  Article word count: {record['article_word_count']}")
    LOG.info(f"  Paragraph count: {record['paragraph_count']}")
    LOG.info(f"  Token count (clean): {record['token_count']}")
    LOG.info(f"  Unique token count: {record['unique_token_count']}")
    LOG.info(f"  Type-token ratio: {record['type_token_ratio']}")

    LOG.info(
        "  DF preview:\n%s",
        df[
            [
                "title",
                "article_word_count",
                "paragraph_count",
                "token_count",
                "type_token_ratio",
            ]
        ].head(),
    )

    LOG.info("Sink: Pandas DataFrame created")
    LOG.info("Transformation complete.")

    # Return the transformed DataFrame for use in the Load stage.
    return df
