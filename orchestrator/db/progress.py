"""
Progress tracking database interface.

This module provides database operations for tracking user progress,
problem statistics, and analytics data using SQLite.
"""

import json
import sqlite3
import time
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

from orchestrator.utils.limits import ExecutionResult


@dataclass
class AttemptRecord:
    """Record of a solution attempt."""
    slug: str
    lang: str
    status: str
    timestamp: Optional[int] = None
    time_ms: Optional[int] = None
    memory_mb: Optional[int] = None
    test_cases_passed: int = 0
    test_cases_total: int = 0
    commit_sha: Optional[str] = None
    notes: Optional[str] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = int(time.time())


@dataclass
class ProblemMeta:
    """Problem metadata and statistics."""
    slug: str
    title: Optional[str] = None
    difficulty: Optional[str] = None
    tags: Optional[str] = None
    first_seen: Optional[int] = None
    last_attempted: Optional[int] = None
    solved_count: int = 0
    total_attempts: int = 0
    best_time_ms: Optional[int] = None
    best_memory_mb: Optional[int] = None
    last_status: Optional[str] = None
    languages_solved: Optional[str] = None


@dataclass
class DailyStats:
    """Daily statistics."""
    date: str
    problems_attempted: int = 0
    problems_solved: int = 0
    total_time_ms: int = 0
    languages_used: Optional[str] = None
    difficulty_breakdown: Optional[str] = None


class ProgressDB:
    """Database interface for progress tracking."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the progress database.
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            db_path = Path(__file__).parent / "progress.sqlite"
        
        self.db_path = db_path
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Create database and tables if they don't exist."""
        schema_path = Path(__file__).parent / "schema.sql"
        
        with self._get_connection() as conn:
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                conn.executescript(schema_sql)
            else:
                # Fallback minimal schema if schema.sql not found
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        slug TEXT NOT NULL,
                        lang TEXT NOT NULL,
                        timestamp INTEGER NOT NULL,
                        status TEXT NOT NULL,
                        time_ms INTEGER,
                        memory_mb INTEGER,
                        test_cases_passed INTEGER DEFAULT 0,
                        test_cases_total INTEGER DEFAULT 0,
                        commit_sha TEXT,
                        notes TEXT
                    )
                """)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS problems_meta (
                        slug TEXT PRIMARY KEY,
                        title TEXT,
                        difficulty TEXT,
                        tags TEXT,
                        first_seen INTEGER,
                        last_attempted INTEGER,
                        solved_count INTEGER DEFAULT 0,
                        total_attempts INTEGER DEFAULT 0,
                        best_time_ms INTEGER,
                        best_memory_mb INTEGER,
                        last_status TEXT,
                        languages_solved TEXT
                    )
                """)
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def record_attempt(self, attempt: AttemptRecord) -> int:
        """
        Record a solution attempt.
        
        Args:
            attempt: AttemptRecord to store
            
        Returns:
            ID of the inserted record
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO attempts (
                    slug, lang, timestamp, status, time_ms, memory_mb,
                    test_cases_passed, test_cases_total, commit_sha, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attempt.slug, attempt.lang, attempt.timestamp, attempt.status,
                attempt.time_ms, attempt.memory_mb, attempt.test_cases_passed,
                attempt.test_cases_total, attempt.commit_sha, attempt.notes
            ))
            return cursor.lastrowid
    
    def record_execution_result(self, slug: str, lang: str, result: ExecutionResult,
                              test_cases_passed: int = 0, test_cases_total: int = 0,
                              commit_sha: Optional[str] = None) -> int:
        """
        Record an execution result as an attempt.
        
        Args:
            slug: Problem slug
            lang: Programming language
            result: ExecutionResult from code execution
            test_cases_passed: Number of test cases passed
            test_cases_total: Total number of test cases
            commit_sha: Optional Git commit SHA
            
        Returns:
            ID of the inserted record
        """
        attempt = AttemptRecord(
            slug=slug,
            lang=lang,
            status=result.status,
            time_ms=result.time_ms,
            memory_mb=result.memory_mb,
            test_cases_passed=test_cases_passed,
            test_cases_total=test_cases_total,
            commit_sha=commit_sha
        )
        return self.record_attempt(attempt)
    
    def get_attempts(self, slug: Optional[str] = None, lang: Optional[str] = None,
                    limit: int = 100, offset: int = 0) -> List[AttemptRecord]:
        """
        Get attempt records with optional filtering.
        
        Args:
            slug: Filter by problem slug
            lang: Filter by language
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of AttemptRecord objects
        """
        query = "SELECT * FROM attempts WHERE 1=1"
        params = []
        
        if slug:
            query += " AND slug = ?"
            params.append(slug)
        
        if lang:
            query += " AND lang = ?"
            params.append(lang)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            return [
                AttemptRecord(
                    id=row['id'],
                    slug=row['slug'],
                    lang=row['lang'],
                    timestamp=row['timestamp'],
                    status=row['status'],
                    time_ms=row['time_ms'],
                    memory_mb=row['memory_mb'],
                    test_cases_passed=row['test_cases_passed'],
                    test_cases_total=row['test_cases_total'],
                    commit_sha=row['commit_sha'],
                    notes=row['notes']
                )
                for row in rows
            ]
    
    def get_problem_meta(self, slug: str) -> Optional[ProblemMeta]:
        """
        Get problem metadata.
        
        Args:
            slug: Problem slug
            
        Returns:
            ProblemMeta object or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM problems_meta WHERE slug = ?",
                (slug,)
            )
            row = cursor.fetchone()
            
            if row:
                return ProblemMeta(
                    slug=row['slug'],
                    title=row['title'],
                    difficulty=row['difficulty'],
                    tags=row['tags'],
                    first_seen=row['first_seen'],
                    last_attempted=row['last_attempted'],
                    solved_count=row['solved_count'],
                    total_attempts=row['total_attempts'],
                    best_time_ms=row['best_time_ms'],
                    best_memory_mb=row['best_memory_mb'],
                    last_status=row['last_status'],
                    languages_solved=row['languages_solved']
                )
            return None
    
    def get_all_problems_meta(self) -> List[ProblemMeta]:
        """
        Get metadata for all problems.
        
        Returns:
            List of ProblemMeta objects
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM problems_meta ORDER BY last_attempted DESC"
            )
            rows = cursor.fetchall()
            
            return [
                ProblemMeta(
                    slug=row['slug'],
                    title=row['title'],
                    difficulty=row['difficulty'],
                    tags=row['tags'],
                    first_seen=row['first_seen'],
                    last_attempted=row['last_attempted'],
                    solved_count=row['solved_count'],
                    total_attempts=row['total_attempts'],
                    best_time_ms=row['best_time_ms'],
                    best_memory_mb=row['best_memory_mb'],
                    last_status=row['last_status'],
                    languages_solved=row['languages_solved']
                )
                for row in rows
            ]
    
    def update_problem_meta(self, slug: str, **kwargs):
        """
        Update problem metadata.
        
        Args:
            slug: Problem slug
            **kwargs: Fields to update
        """
        if not kwargs:
            return
        
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for key, value in kwargs.items():
            if key in ['title', 'difficulty', 'tags', 'languages_solved']:
                set_clauses.append(f"{key} = ?")
                params.append(value)
        
        if set_clauses:
            set_clauses.append("updated_at = ?")
            params.append(int(time.time()))
            params.append(slug)
            
            query = f"UPDATE problems_meta SET {', '.join(set_clauses)} WHERE slug = ?"
            
            with self._get_connection() as conn:
                conn.execute(query, params)
    
    def get_daily_stats(self, days: int = 30) -> List[DailyStats]:
        """
        Get daily statistics for the last N days.
        
        Args:
            days: Number of days to retrieve
            
        Returns:
            List of DailyStats objects
        """
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM statistics 
                WHERE date >= date('now', '-{} days')
                ORDER BY date DESC
            """.format(days))
            rows = cursor.fetchall()
            
            return [
                DailyStats(
                    date=row['date'],
                    problems_attempted=row['problems_attempted'],
                    problems_solved=row['problems_solved'],
                    total_time_ms=row['total_time_ms'],
                    languages_used=row['languages_used'],
                    difficulty_breakdown=row['difficulty_breakdown']
                )
                for row in rows
            ]
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        Get overall statistics summary.
        
        Returns:
            Dictionary with summary statistics
        """
        with self._get_connection() as conn:
            # Total problems attempted and solved
            cursor = conn.execute("""
                SELECT 
                    COUNT(DISTINCT slug) as problems_attempted,
                    COUNT(DISTINCT CASE WHEN solved_count > 0 THEN slug END) as problems_solved
                FROM problems_meta
            """)
            problem_stats = cursor.fetchone()
            
            # Total attempts and success rate
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_attempts,
                    COUNT(CASE WHEN status = 'OK' THEN 1 END) as successful_attempts
                FROM attempts
            """)
            attempt_stats = cursor.fetchone()
            
            # Language breakdown
            cursor = conn.execute("""
                SELECT lang, COUNT(*) as count
                FROM attempts
                GROUP BY lang
                ORDER BY count DESC
            """)
            language_stats = {row['lang']: row['count'] for row in cursor.fetchall()}
            
            # Recent activity (last 7 days)
            cursor = conn.execute("""
                SELECT COUNT(*) as recent_attempts
                FROM attempts
                WHERE timestamp >= strftime('%s', 'now', '-7 days')
            """)
            recent_activity = cursor.fetchone()
            
            success_rate = 0
            if attempt_stats['total_attempts'] > 0:
                success_rate = (attempt_stats['successful_attempts'] / attempt_stats['total_attempts']) * 100
            
            return {
                'problems_attempted': problem_stats['problems_attempted'],
                'problems_solved': problem_stats['problems_solved'],
                'total_attempts': attempt_stats['total_attempts'],
                'successful_attempts': attempt_stats['successful_attempts'],
                'success_rate': round(success_rate, 2),
                'language_breakdown': language_stats,
                'recent_attempts_7d': recent_activity['recent_attempts']
            }
    
    def get_user_setting(self, key: str, default: Any = None) -> Any:
        """
        Get user setting value.
        
        Args:
            key: Setting key
            default: Default value if setting not found
            
        Returns:
            Setting value or default
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT value FROM user_settings WHERE key = ?",
                (key,)
            )
            row = cursor.fetchone()
            
            if row:
                try:
                    # Try to parse as JSON first
                    return json.loads(row['value'])
                except (json.JSONDecodeError, TypeError):
                    # Return as string if not valid JSON
                    return row['value']
            
            return default
    
    def set_user_setting(self, key: str, value: Any):
        """
        Set user setting value.
        
        Args:
            key: Setting key
            value: Setting value (will be JSON-encoded if not string)
        """
        if isinstance(value, str):
            value_str = value
        else:
            value_str = json.dumps(value)
        
        with self._get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO user_settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, value_str, int(time.time())))
    
    def cleanup_old_data(self, days_to_keep: int = 365):
        """
        Clean up old data to prevent database from growing too large.
        
        Args:
            days_to_keep: Number of days of data to keep
        """
        cutoff_timestamp = int(time.time()) - (days_to_keep * 24 * 60 * 60)
        
        with self._get_connection() as conn:
            # Delete old attempts
            cursor = conn.execute(
                "DELETE FROM attempts WHERE timestamp < ?",
                (cutoff_timestamp,)
            )
            attempts_deleted = cursor.rowcount
            
            # Delete old daily statistics
            cursor = conn.execute(
                "DELETE FROM statistics WHERE date < date('now', '-{} days')".format(days_to_keep)
            )
            stats_deleted = cursor.rowcount
            
            # Vacuum database to reclaim space
            conn.execute("VACUUM")
            
            return {
                'attempts_deleted': attempts_deleted,
                'stats_deleted': stats_deleted
            }