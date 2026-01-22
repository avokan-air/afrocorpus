# AfroCorpus

A Python package for managing and querying African text corpora with flexible metadata-based filtering.

## Features

- Load and manage text corpora with metadata
- Flexible filtering by country, language, URL, date, and content
- Easy extraction of text content
- Dynamic corpus expansion with the `add()` method
- Content matching with `match` and `match_all` options
- Automatic corpus data download with possibility to iupdate data with more data being added periodically without upgrading the package itself

## Installation

```bash
pip install afrocorpus
```

Or from source:

```bash
git clone https://github.com/avokan-air/afrocorpus.git
cd afrocorpus
pip install -e .
```

## Downloading Corpus Data

After installation, download the corpus data files:

```python
from afrocorpus import AfroCorpus

# Download corpus data (tries primary URL, falls back to backups if needed)
AfroCorpus.download_data()
```

The download function automatically:
- Tries the primary Google Drive URL first
- Falls back to backup URLs if primary fails
- Extracts .txt files to the data directory
- Shows progress and confirmation messages

**To re-download and overwrite existing data:**

```python
AfroCorpus.download_data(force=True)
```

## Quick Start

```python
from afrocorpus import AfroCorpus

# First time: download the data
AfroCorpus.download_data()

# Load all documents
corpus = AfroCorpus()
print(f"Loaded {len(corpus)} documents")

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

# Add more documents with additional filters
corpus.add({"url": "nouvelletribune", "match_all": ["talon", "yayi"]})
```

## Using Your Own Data

If you have your own corpus files locally:

```python
corpus = AfroCorpus(
    filters={"language": "fr"},
    data_dir="/path/to/your/data"
)
```

## File Format

Text files should follow this format:

```
URL: https://example.com/article
Filename: article.txt
Language: fr
Last Updated: 2026-01-15T10:00:00.000000
Country: bj
================================================================================
Your article content goes here...
```

Lines 1-5 contain metadata, line 6 is an optional separator, and line 7+ contains the actual content.

## Filter Options

| Filter | Description | Example |
|--------|-------------|---------|
| `country` | Country code (defaults to "bj") | `{"country": "bj"}` |
| `language` | Language code | `{"language": "fr"}` |
| `url` | URL substring match | `{"url": "wikipedia"}` |
| `date` | Date with operators (>, <, >=, <=, =) | `{"date": ">2026-01-01"}` |
| `match` | At least one term must appear | `{"match": ["term1", "term2"]}` |
| `match_all` | All terms must appear | `{"match_all": ["term1", "term2"]}` |

## Advanced Usage

### Chaining Filters

```python
# Start with French documents from Benin
corpus = AfroCorpus({"country": "bj", "language": "fr"})

# Add English documents from Nigeria
corpus.add({"country": "ng", "language": "en"})

# Add any documents containing specific keywords
corpus.add({"match": ["economy", "politique"]})
```

### Accessing Individual Documents

```python
corpus = AfroCorpus()

# Get total number of documents
print(len(corpus))

# Access first document
first_doc = corpus[0]
print(first_doc['url'])
print(first_doc['language'])
print(first_doc['content'][:100])

# Iterate through all documents
for doc in corpus.documents:
    print(f"{doc['filename']}: {doc['language']}")
```

## Development

### Running Tests

```bash
python -m pytest tests/
# or
python -m unittest discover tests
```

### Building the Package

```bash
python -m build
```

### Publishing to PyPI

```bash
python -m twine upload dist/*
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Troubleshooting

### Download Issues

If `download_data()` fails:
- Check your internet connection
- The function will automatically try backup URLs
- Use `force=True` to re-download: `AfroCorpus.download_data(force=True)`

### No Documents Found

If your corpus loads but has 0 documents:
- Check that your filters aren't too restrictive
- Verify the metadata format in your .txt files matches the expected format
- Try loading without filters: `AfroCorpus()`

## License

MIT License - see LICENSE file for details.

## Author

Ola ABOUBAKAR (ola@avokan.com)

## Citation

If you use AfroCorpus in your research, please cite:

```bibtex
@software{afrocorpus2026,
  author = {Ola ABOUBAKAR},
  title = {AfroCorpus: A Python Package for African Text Corpora},
  year = {2026},
  url = {https://github.com/avokan-air/afrocorpus}
}
```
