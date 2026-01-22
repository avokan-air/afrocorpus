"""Core corpus management functionality."""

import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class AfroCorpus:
    def __init__(self, filters: Optional[Dict[str, Any]] = None, data_dir: Optional[str] = None):
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(__file__), 'data')
        else:
            self.data_dir = data_dir
        self.documents = []
        if filters is None:
            filters = {}
        self._load_documents(filters)
    
    def _parse_metadata(self, filepath: str) -> Optional[Dict[str, Any]]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            if len(lines) < 7:
                return None
            metadata = {}
            for i in range(5):
                line = lines[i].strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip().lower()] = value.strip()
            if 'country' not in metadata or not metadata['country']:
                metadata['country'] = 'bj'
            content = ''.join(lines[6:]).strip()
            if content.startswith('='*20):
                content = '\n'.join(content.split('\n')[1:]).strip()
            metadata['content'] = content
            metadata['filepath'] = filepath
            return metadata
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None
    
    def _parse_date_filter(self, date_str: str) -> tuple:
        operators = ['>=', '<=', '>', '<', '=']
        operator = None
        date_part = date_str
        for op in operators:
            if date_str.startswith(op):
                operator = op
                date_part = date_str[len(op):].strip()
                break
        if operator is None:
            operator = '='
        try:
            date_obj = datetime.fromisoformat(date_part)
            return operator, date_obj
        except ValueError:
            return None, None
    
    def _matches_filters(self, doc: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        if 'country' in filters:
            if doc.get('country', 'bj').lower() != filters['country'].lower():
                return False
        if 'language' in filters:
            if doc.get('language', '').lower() != filters['language'].lower():
                return False
        if 'url' in filters:
            if filters['url'].lower() not in doc.get('url', '').lower():
                return False
        if 'date' in filters:
            operator, filter_date = self._parse_date_filter(filters['date'])
            if operator is None:
                return False
            try:
                doc_date_str = doc.get('last updated', '')
                if 'T' in doc_date_str:
                    doc_date_str = doc_date_str.split('T')[0]
                doc_date = datetime.fromisoformat(doc_date_str)
                if operator == '>' and not (doc_date > filter_date):
                    return False
                elif operator == '<' and not (doc_date < filter_date):
                    return False
                elif operator == '>=' and not (doc_date >= filter_date):
                    return False
                elif operator == '<=' and not (doc_date <= filter_date):
                    return False
                elif operator == '=' and doc_date.date() != filter_date.date():
                    return False
            except (ValueError, KeyError):
                return False
        content = doc.get('content', '').lower()
        if 'match' in filters:
            match_list = filters['match'] if isinstance(filters['match'], list) else [filters['match']]
            if not any(term.lower() in content for term in match_list):
                return False
        if 'match_all' in filters:
            match_all_list = filters['match_all'] if isinstance(filters['match_all'], list) else [filters['match_all']]
            if not all(term.lower() in content for term in match_all_list):
                return False
        return True
    
    def _load_documents(self, filters: Dict[str, Any]):
        if not os.path.exists(self.data_dir):
            return
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.data_dir, filename)
                doc = self._parse_metadata(filepath)
                if doc and self._matches_filters(doc, filters):
                    self.documents.append(doc)
    
    def contents(self) -> List[str]:
        return [doc.get('content', '') for doc in self.documents]
    
    def add(self, filters: Dict[str, Any]):
        if not os.path.exists(self.data_dir):
            return
        existing_files = {doc['filepath'] for doc in self.documents}
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.data_dir, filename)
                if filepath in existing_files:
                    continue
                doc = self._parse_metadata(filepath)
                if doc and self._matches_filters(doc, filters):
                    self.documents.append(doc)
    
    def __len__(self) -> int:
        return len(self.documents)
    
    def __repr__(self) -> str:
        return f"AfroCorpus(documents={len(self.documents)})"
    
    def __getitem__(self, index: int) -> Dict[str, Any]:
        return self.documents[index]
