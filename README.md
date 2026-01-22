# AfroCorpus

A Python package for managing and querying African text corpora with flexible metadata-based filtering.

## Features

- 📚 Load and manage text corpora with metadata
- 🔍 Flexible filtering by country, language, URL, date, and content
- 📊 Easy extraction of text content
- 🔄 Dynamic corpus expansion with the `add()` method
- 🎯 Content matching with `match` and `match_all` options

## Installation

```bash
pip install afrocorpus
```

Or from source:

```bash
git clone https://github.com/avokanbj/afrocorpus.git
cd afrocorpus
pip install -e .
```

## Quick Start

```python
from afrocorpus import AfroCorpus

# Load all documents
corpus = AfroCorpus()

# Load with filters
corpus = AfroCorpus({
    "country": "bj",
    "language": "fr",
    "url": "wikipedia",
    "date": ">2026-01-01"
})

# Get contents
texts = corpus.contents()
full_text = " ".join(texts)

# Add more documents
corpus.add({"url": "nouvelletribune", "match_all": ["talon", "yayi"]})
```

## License

MIT License

## Author

Ola ABOUBAKAR (ola@avokan.com)
