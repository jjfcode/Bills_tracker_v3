#!/usr/bin/env python3
"""
Data Compression Module for Bills Tracker Application

This module provides comprehensive data compression functionality for:
- SQLite database compression
- Backup file compression
- Export file compression
- Large dataset optimization

Features:
- Multiple compression algorithms (gzip, lzma, zlib)
- Automatic compression level optimization
- Progress tracking for large operations
- Compression ratio analysis
- Automatic decompression for data access
"""

import os
import gzip
import lzma
import zlib
import sqlite3
import shutil
import json
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
import time

# Import progress bar functionality
try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

class DataCompressor:
    """Comprehensive data compression for Bills Tracker application."""
    
    def __init__(self):
        self.compression_stats = {
            'files_compressed': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'compression_ratio': 0.0,
            'time_saved': 0.0
        }
        
        # Compression algorithms and their settings
        self.compression_methods = {
            'gzip': {
                'compresslevel': 9,  # Maximum compression
                'extension': '.gz',
                'description': 'GZIP compression (fast, good compression)'
            },
            'lzma': {
                'preset': 9,  # Maximum compression
                'extension': '.xz',
                'description': 'LZMA compression (slower, best compression)'
            },
            'zlib': {
                'level': 9,  # Maximum compression
                'extension': '.zlib',
                'description': 'ZLIB compression (balanced)'
            }
        }
    
    def compress_file(self, file_path: str, method: str = 'gzip', 
                     delete_original: bool = False) -> Tuple[bool, str, Dict]:
        """
        Compress a single file using specified method.
        
        Args:
            file_path: Path to file to compress
            method: Compression method ('gzip', 'lzma', 'zlib')
            delete_original: Whether to delete original file after compression
            
        Returns:
            Tuple of (success, compressed_file_path, compression_stats)
        """
        if not os.path.exists(file_path):
            return False, "", {"error": "File not found"}
        
        if method not in self.compression_methods:
            return False, "", {"error": f"Unknown compression method: {method}"}
        
        original_size = os.path.getsize(file_path)
        compressed_path = file_path + self.compression_methods[method]['extension']
        
        try:
            start_time = time.time()
            
            if method == 'gzip':
                with open(file_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb', 
                                 compresslevel=self.compression_methods[method]['compresslevel']) as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif method == 'lzma':
                with open(file_path, 'rb') as f_in:
                    with lzma.open(compressed_path, 'wb', 
                                 preset=self.compression_methods[method]['preset']) as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif method == 'zlib':
                with open(file_path, 'rb') as f_in:
                    data = f_in.read()
                    compressed_data = zlib.compress(data, level=self.compression_methods[method]['level'])
                    with open(compressed_path, 'wb') as f_out:
                        f_out.write(compressed_data)
            
            compression_time = time.time() - start_time
            compressed_size = os.path.getsize(compressed_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            stats = {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'compression_time': compression_time,
                'method': method
            }
            
            if delete_original:
                os.remove(file_path)
            
            return True, compressed_path, stats
            
        except Exception as e:
            # Clean up partial file if it exists
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            return False, "", {"error": str(e)}
    
    def decompress_file(self, compressed_file_path: str, 
                       output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Decompress a compressed file.
        
        Args:
            compressed_file_path: Path to compressed file
            output_path: Optional output path (defaults to removing compression extension)
            
        Returns:
            Tuple of (success, decompressed_file_path)
        """
        if not os.path.exists(compressed_file_path):
            return False, ""
        
        # Determine compression method from file extension
        method = None
        for meth, settings in self.compression_methods.items():
            if compressed_file_path.endswith(settings['extension']):
                method = meth
                break
        
        if not method:
            return False, ""
        
        if output_path is None:
            output_path = compressed_file_path[:-len(self.compression_methods[method]['extension'])]
        
        try:
            if method == 'gzip':
                with gzip.open(compressed_file_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif method == 'lzma':
                with lzma.open(compressed_file_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
            
            elif method == 'zlib':
                with open(compressed_file_path, 'rb') as f_in:
                    compressed_data = f_in.read()
                    decompressed_data = zlib.decompress(compressed_data)
                    with open(output_path, 'wb') as f_out:
                        f_out.write(decompressed_data)
            
            return True, output_path
            
        except Exception as e:
            return False, str(e)
    
    def compress_database(self, db_path: str, method: str = 'gzip', 
                         backup_original: bool = True) -> Tuple[bool, str, Dict]:
        """
        Compress SQLite database file.
        
        Args:
            db_path: Path to SQLite database
            method: Compression method
            backup_original: Whether to backup original before compression
            
        Returns:
            Tuple of (success, compressed_path, stats)
        """
        if not os.path.exists(db_path):
            return False, "", {"error": "Database file not found"}
        
        # Create backup if requested
        if backup_original:
            backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            shutil.copy2(db_path, backup_path)
        
        # Compress the database
        success, compressed_path, stats = self.compress_file(db_path, method, delete_original=False)
        
        if success:
            stats['database_compressed'] = True
            stats['backup_created'] = backup_original
        
        return success, compressed_path, stats
    
    def compress_backup_directory(self, backup_dir: str, method: str = 'gzip',
                                delete_originals: bool = False) -> Dict:
        """
        Compress all files in backup directory.
        
        Args:
            backup_dir: Path to backup directory
            method: Compression method
            delete_originals: Whether to delete original files after compression
            
        Returns:
            Dictionary with compression results
        """
        if not os.path.exists(backup_dir):
            return {"error": "Backup directory not found"}
        
        results = {
            'files_processed': 0,
            'files_compressed': 0,
            'errors': [],
            'total_original_size': 0,
            'total_compressed_size': 0
        }
        
        for filename in os.listdir(backup_dir):
            file_path = os.path.join(backup_dir, filename)
            
            # Skip already compressed files
            if any(filename.endswith(ext) for ext in ['.gz', '.xz', '.zlib']):
                continue
            
            # Skip directories
            if os.path.isdir(file_path):
                continue
            
            results['files_processed'] += 1
            
            try:
                success, compressed_path, stats = self.compress_file(
                    file_path, method, delete_originals
                )
                
                if success:
                    results['files_compressed'] += 1
                    results['total_original_size'] += stats['original_size']
                    results['total_compressed_size'] += stats['compressed_size']
                else:
                    results['errors'].append(f"Failed to compress {filename}: {stats.get('error', 'Unknown error')}")
                    
            except Exception as e:
                results['errors'].append(f"Error processing {filename}: {str(e)}")
        
        if results['total_original_size'] > 0:
            results['compression_ratio'] = (
                (1 - results['total_compressed_size'] / results['total_original_size']) * 100
            )
        
        return results
    
    def compress_with_progress(self, file_path: str, method: str = 'gzip',
                              delete_original: bool = False) -> Tuple[bool, str, Dict]:
        """
        Compress file with progress tracking.
        
        Args:
            file_path: Path to file to compress
            method: Compression method
            delete_original: Whether to delete original file
            
        Returns:
            Tuple of (success, compressed_path, stats)
        """
        if not TQDM_AVAILABLE:
            return self.compress_file(file_path, method, delete_original)
        
        if not os.path.exists(file_path):
            return False, "", {"error": "File not found"}
        
        original_size = os.path.getsize(file_path)
        compressed_path = file_path + self.compression_methods[method]['extension']
        
        try:
            start_time = time.time()
            
            with tqdm(total=original_size, unit='B', unit_scale=True, 
                     desc=f"Compressing with {method.upper()}") as pbar:
                
                if method == 'gzip':
                    with open(file_path, 'rb') as f_in:
                        with gzip.open(compressed_path, 'wb', 
                                     compresslevel=self.compression_methods[method]['compresslevel']) as f_out:
                            while True:
                                chunk = f_in.read(8192)
                                if not chunk:
                                    break
                                f_out.write(chunk)
                                pbar.update(len(chunk))
                
                elif method == 'lzma':
                    with open(file_path, 'rb') as f_in:
                        with lzma.open(compressed_path, 'wb', 
                                     preset=self.compression_methods[method]['preset']) as f_out:
                            while True:
                                chunk = f_in.read(8192)
                                if not chunk:
                                    break
                                f_out.write(chunk)
                                pbar.update(len(chunk))
                
                elif method == 'zlib':
                    with open(file_path, 'rb') as f_in:
                        data = f_in.read()
                        pbar.update(len(data))
                        compressed_data = zlib.compress(data, level=self.compression_methods[method]['level'])
                        with open(compressed_path, 'wb') as f_out:
                            f_out.write(compressed_data)
            
            compression_time = time.time() - start_time
            compressed_size = os.path.getsize(compressed_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            stats = {
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': compression_ratio,
                'compression_time': compression_time,
                'method': method
            }
            
            if delete_original:
                os.remove(file_path)
            
            return True, compressed_path, stats
            
        except Exception as e:
            if os.path.exists(compressed_path):
                os.remove(compressed_path)
            return False, "", {"error": str(e)}
    
    def analyze_compression_effectiveness(self, file_path: str) -> Dict:
        """
        Analyze which compression method works best for a file.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            Dictionary with compression analysis results
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        original_size = os.path.getsize(file_path)
        results = {
            'original_size': original_size,
            'methods': {}
        }
        
        for method in self.compression_methods.keys():
            try:
                success, compressed_path, stats = self.compress_file(file_path, method)
                if success:
                    results['methods'][method] = {
                        'compressed_size': stats['compressed_size'],
                        'compression_ratio': stats['compression_ratio'],
                        'compression_time': stats['compression_time']
                    }
                    # Clean up test file
                    os.remove(compressed_path)
                else:
                    results['methods'][method] = {'error': stats.get('error', 'Unknown error')}
            except Exception as e:
                results['methods'][method] = {'error': str(e)}
        
        # Find best method
        best_method = None
        best_ratio = 0
        for method, data in results['methods'].items():
            if 'compression_ratio' in data and data['compression_ratio'] > best_ratio:
                best_ratio = data['compression_ratio']
                best_method = method
        
        results['best_method'] = best_method
        results['best_compression_ratio'] = best_ratio
        
        return results
    
    def get_compression_info(self, file_path: str) -> Dict:
        """
        Get information about a compressed file.
        
        Args:
            file_path: Path to compressed file
            
        Returns:
            Dictionary with compression information
        """
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        file_size = os.path.getsize(file_path)
        
        # Try to determine compression method and get original size
        method = None
        original_size = None
        
        for meth, settings in self.compression_methods.items():
            if file_path.endswith(settings['extension']):
                method = meth
                break
        
        if method:
            try:
                # Try to decompress to get original size
                with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                    success, _ = self.decompress_file(file_path, temp_file.name)
                    if success:
                        original_size = os.path.getsize(temp_file.name)
            except:
                pass
        
        return {
            'file_path': file_path,
            'file_size': file_size,
            'compression_method': method,
            'original_size': original_size,
            'compression_ratio': ((1 - file_size / original_size) * 100) if original_size else None,
            'is_compressed': method is not None
        }
    
    def batch_compress(self, file_paths: List[str], method: str = 'gzip',
                      delete_originals: bool = False) -> Dict:
        """
        Compress multiple files in batch.
        
        Args:
            file_paths: List of file paths to compress
            method: Compression method
            delete_originals: Whether to delete original files
            
        Returns:
            Dictionary with batch compression results
        """
        results = {
            'total_files': len(file_paths),
            'successful': 0,
            'failed': 0,
            'errors': [],
            'total_original_size': 0,
            'total_compressed_size': 0,
            'files': {}
        }
        
        for file_path in file_paths:
            try:
                success, compressed_path, stats = self.compress_file(
                    file_path, method, delete_originals
                )
                
                if success:
                    results['successful'] += 1
                    results['total_original_size'] += stats['original_size']
                    results['total_compressed_size'] += stats['compressed_size']
                    results['files'][file_path] = {
                        'status': 'success',
                        'compressed_path': compressed_path,
                        'stats': stats
                    }
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed to compress {file_path}: {stats.get('error', 'Unknown error')}")
                    results['files'][file_path] = {
                        'status': 'failed',
                        'error': stats.get('error', 'Unknown error')
                    }
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error processing {file_path}: {str(e)}")
                results['files'][file_path] = {
                    'status': 'error',
                    'error': str(e)
                }
        
        if results['total_original_size'] > 0:
            results['overall_compression_ratio'] = (
                (1 - results['total_compressed_size'] / results['total_original_size']) * 100
            )
        
        return results

# Utility functions for easy access
def compress_file(file_path: str, method: str = 'gzip', delete_original: bool = False) -> Tuple[bool, str, Dict]:
    """Quick function to compress a single file."""
    compressor = DataCompressor()
    return compressor.compress_file(file_path, method, delete_original)

def decompress_file(compressed_file_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
    """Quick function to decompress a file."""
    compressor = DataCompressor()
    return compressor.decompress_file(compressed_file_path, output_path)

def analyze_compression(file_path: str) -> Dict:
    """Quick function to analyze compression effectiveness."""
    compressor = DataCompressor()
    return compressor.analyze_compression_effectiveness(file_path)

if __name__ == "__main__":
    # Example usage
    compressor = DataCompressor()
    
    # Test compression
    test_file = "test_data.json"
    if os.path.exists(test_file):
        print(f"Testing compression on {test_file}")
        
        # Analyze best compression method
        analysis = compressor.analyze_compression_effectiveness(test_file)
        print(f"Compression analysis: {analysis}")
        
        # Compress with best method
        if analysis.get('best_method'):
            success, compressed_path, stats = compressor.compress_file(
                test_file, analysis['best_method']
            )
            if success:
                print(f"Successfully compressed to {compressed_path}")
                print(f"Compression stats: {stats}")
    else:
        print("No test file found. Create a test_data.json file to test compression.") 