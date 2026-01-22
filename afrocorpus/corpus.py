"""Core corpus management functionality."""

import os
import urllib.request
import zipfile
import shutil
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
    
    @staticmethod
    def download_data(force: bool = False) -> bool:
        """
        Download corpus data from Google Drive and extract to data directory.
        
        The function tries multiple backup URLs automatically if the primary fails.
        
        Args:
            force: If True, download even if data directory already has files
            
        Returns:
            True if download successful, False otherwise
            
        Example:
            >>> AfroCorpus.download_data()
            >>> AfroCorpus.download_data(force=True)  # Re-download
        """
        # Hardcoded Google Drive URLs (primary + backups)
        GDRIVE_URLS = [
            'https://drive.google.com/file/d/1oVI0yKlfeooBI6wkNVU8VHBPA7Ag7H5N/view?usp=sharing',  # Primary
            'https://drive.google.com/file/d/110YmDGorWxHySRnbqkAgUxB3oXIo-PGM/view?usp=sharing',  # Backup 1
            'https://drive.google.com/file/d/1KOE_FSik5bMKBZ991tgIQ29GKxutGlGu/view?usp=sharing',  # Backup 2
        ]
        
        # Get the data directory path
        package_dir = os.path.dirname(__file__)
        data_dir = os.path.join(package_dir, 'data')
        
        # Check if data already exists
        if not force:
            existing_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
            if existing_files:
                print(f"Data directory already contains {len(existing_files)} files.")
                print("Use AfroCorpus.download_data(force=True) to re-download and overwrite.")
                return False
        
        # Try each URL until one works
        for url_idx, gdrive_url in enumerate(GDRIVE_URLS):
            url_label = "Primary URL" if url_idx == 0 else f"Backup URL {url_idx}"
            
            try:
                # Convert Google Drive sharing URL to direct download URL
                if '/file/d/' in gdrive_url:
                    file_id = gdrive_url.split('/file/d/')[1].split('/')[0]
                else:
                    print(f"Error: Invalid Google Drive URL format for {url_label}")
                    continue
                
                download_url = f'https://drive.google.com/uc?export=download&id={file_id}'
                
                print(f"Downloading corpus data from {url_label}...")
                
                # Download the zip file
                zip_path = os.path.join(package_dir, 'corpus_data.zip')
                
                # Handle large files (Google Drive virus scan warning)
                opener = urllib.request.build_opener()
                opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
                urllib.request.install_opener(opener)
                
                # Try to download with confirmation token for large files
                try:
                    urllib.request.urlretrieve(download_url, zip_path)
                except Exception:
                    # Try with confirmation token
                    confirm_url = download_url + '&confirm=t'
                    urllib.request.urlretrieve(confirm_url, zip_path)
                
                # Verify the download
                if not os.path.exists(zip_path) or os.path.getsize(zip_path) < 1000:
                    print(f"Download from {url_label} failed or incomplete, trying next URL...")
                    if os.path.exists(zip_path):
                        os.remove(zip_path)
                    continue
                
                print(f"Download complete. Extracting files...")
                
                # Clear existing .txt files if force=True
                if force:
                    for f in os.listdir(data_dir):
                        if f.endswith('.txt'):
                            os.remove(os.path.join(data_dir, f))
                
                # Extract the zip file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    # Extract only .txt files to the data directory
                    for file in zip_ref.namelist():
                        if file.endswith('.txt'):
                            # Extract to data directory
                            zip_ref.extract(file, data_dir)
                            # If file was in a subdirectory, move it to data root
                            extracted_path = os.path.join(data_dir, file)
                            if os.path.dirname(file):
                                dest_path = os.path.join(data_dir, os.path.basename(file))
                                shutil.move(extracted_path, dest_path)
                                # Clean up empty directories
                                try:
                                    os.removedirs(os.path.join(data_dir, os.path.dirname(file)))
                                except:
                                    pass
                
                # Clean up the zip file
                os.remove(zip_path)
                
                # Count downloaded files
                txt_files = [f for f in os.listdir(data_dir) if f.endswith('.txt')]
                print(f"✓ Successfully downloaded {len(txt_files)} corpus files to {data_dir}")
                
                return True
                
            except Exception as e:
                print(f"Error downloading from {url_label}: {e}")
                if os.path.exists(os.path.join(package_dir, 'corpus_data.zip')):
                    os.remove(os.path.join(package_dir, 'corpus_data.zip'))
                
                # If this was the last URL, show error
                if url_idx == len(GDRIVE_URLS) - 1:
                    print("" + "="*60)
                    print("Failed to download from all available URLs.")
                    print("Please check your internet connection and try again.")
                    print("="*60)
                    return False
                else:
                    print(f"Trying next URL...")
                    continue
        
        return False
