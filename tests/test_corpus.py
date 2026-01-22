"""Unit tests for AfroCorpus."""

import unittest
import os
import tempfile
import shutil
from afrocorpus import AfroCorpus

class TestAfroCorpus(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        with open(os.path.join(self.test_dir, 'test1.txt'), 'w') as f:
            f.write("""URL: https://example.com/1
Filename: test1.txt
Language: fr
Last Updated: 2026-01-15T10:00:00
Country: bj
===
Test article about talon and yayi.""")
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_load_all(self):
        corpus = AfroCorpus(data_dir=self.test_dir)
        self.assertEqual(len(corpus), 1)
    
    def test_contents(self):
        corpus = AfroCorpus(data_dir=self.test_dir)
        self.assertEqual(len(corpus.contents()), 1)

if __name__ == '__main__':
    unittest.main()
