"""Offline smoke test for the Kansas City Chiefs NLP pipeline."""

import logging
from types import SimpleNamespace

import matplotlib
import pandas as pd
import requests

from nlp.stage01_extract import run_extract
from nlp.stage02_validate import run_validate
from nlp.stage03_transform import run_transform
from nlp.stage04_analyze import run_analyze
from nlp.stage05_load import run_load

# Sample Chiefs-style article for offline testing.
# No live internet connection is required.
HTML = """<html>
<head>
<link rel="canonical"
href="https://www.chiefs.com/news/chiefs-test-article">
</head>
<body>
<h1>Kansas City Chiefs Official Team Website</h1>
<article>
<h1>Chiefs Defeat Chargers, 22-6, to Move to 5-0 on the Season</h1>
<p>The Kansas City Chiefs defeated the Los Angeles Chargers.</p>
<p>The Chiefs defense played well throughout the game.</p>
<p>Kansas City secured another victory with strong defensive play.</p>
</article>
</body>
</html>
"""


def test_nlp_stages_write_features_figures_and_csv(monkeypatch, tmp_path):
    """Test the Chiefs NLP pipeline with a fixed HTML sample."""

    def fake_get(url, *, headers, timeout):
        assert url == "https://example.test/chiefs"
        assert "User-Agent" in headers
        assert timeout == 30
        return SimpleNamespace(text=HTML, raise_for_status=lambda: None)

    matplotlib.use("Agg")
    monkeypatch.setattr(requests, "get", fake_get)

    log = logging.getLogger(__name__)
    raw_path = tmp_path / "chiefs_raw.html"
    csv_path = tmp_path / "chiefs_processed.csv"
    output_dir = tmp_path / "processed"

    # Extract, validate, and transform.
    html = run_extract(
        "https://example.test/chiefs",
        {"User-Agent": "pytest"},
        raw_path,
        log,
    )

    df = run_transform(run_validate(html, log), log)

    # Analyze and load.
    run_analyze(df, LOG=log, output_dir=output_dir, top_n=5)
    run_load(df, csv_path, log)

    # Verify raw HTML and processed CSV.
    assert raw_path.read_text(encoding="utf-8") == HTML
    assert csv_path.stat().st_size > 0

    saved = pd.read_csv(csv_path)

    # Verify Chiefs article fields.
    assert saved.loc[0, "title"] == (
        "Chiefs Defeat Chargers, 22-6, to Move to 5-0 on the Season"
    )
    assert saved.loc[0, "paragraph_count"] == 3
    assert saved.loc[0, "article_word_count"] > 0
    assert saved.loc[0, "token_count"] > 0
    assert saved.loc[0, "unique_token_count"] > 0
    assert 0 < saved.loc[0, "type_token_ratio"] <= 1

    # Verify both Chiefs visualizations were generated.
    assert (output_dir / "chiefs_top_tokens.png").stat().st_size > 0
    assert (output_dir / "chiefs_wordcloud.png").stat().st_size > 0
