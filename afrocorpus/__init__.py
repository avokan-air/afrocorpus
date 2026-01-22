"""
AfroCorpus - A Python package for managing and querying African text corpora.
"""

from .corpus import AfroCorpus

__version__ = "0.1.1"
__author__ = "Ola ABOUBAKAR"
__email__ = "ola@avokan.com"

__all__ = ["AfroCorpus"]

# Display helpful message on import
import os
_data_dir = os.path.join(os.path.dirname(__file__), 'data')
_txt_files = [f for f in os.listdir(_data_dir) if f.endswith('.txt')] if os.path.exists(_data_dir) else []

if not _txt_files:
    print("=" * 60)
    print("Welcome to AfroCorpus! (by Avokan AIR)")
    print("=" * 60)
    print("No corpus data found. To download the corpus data, run:")
    print()
    print("    from afrocorpus import AfroCorpus")
    print("    AfroCorpus.download_data()")
    print()
    print("The corpus data will be automatically downloaded from")
    print("our repositories (with automatic fallback to backup URLs).")
    print("=" * 60)
