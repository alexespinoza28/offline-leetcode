#!/usr/bin/env python3
"""
Community explanation loader for integrating user-contributed explanations.

This module handles loading and managing community-contributed explanation.md files
with priority system that favors community explanations over templates.
"""

import os
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class CommunityExplanationLoader:
    """
    Loads and manages community-contributed explanations.
    
    Supports:
    - explanation.md file detection and loading
    - Priority system favoring community explanations
    - Metadata extraction from explanation files
    - Fallback to template system when no community explanation exists
    """
    
    def __init__(self, problems_dir: str = "problems"):
        """
        Initialize community explanation loader.
        
        Args:
            problems_dir: Directory containing problem directories with explanation.md files
        """
        self.problems_dir = Path(problems_dir)
        self.explanation_cache = {}
        self.metadata_cache = {}
    
    def find_community_explanation(self, problem_slug: str) -> Optional[Path]:
        """
        Find community explanation file for a problem.
        
        Args:
            problem_slug: Problem identifier
            
        Returns:
            Path to explanation.md file or None if not found
        """
        # Check multiple possible locations
        possible_paths = [
            self.problems_dir / problem_slug / "explanation.md",
            self.problems_dir / problem_slug / "explanations" / "explanation.md",
            self.problems_dir / problem_slug / "community" / "explanation.md",
            self.problems_dir / problem_slug / "docs" / "explanation.md",
        ]
        
        for path in possible_paths:
            if path.exists() and path.is_file():
                logger.debug(f"Found community explanation: {path}")
                return path
        
        logger.debug(f"No community explanation found for problem: {problem_slug}")
        return None
    
    def load_community_explanation(self, problem_slug: str) -> Optional[Dict[str, Any]]:
        """
        Load community explanation content and metadata.
        
        Args:
            problem_slug: Problem identifier
            
        Returns:
            Dictionary with explanation content and metadata, or None if not found
        """
        # Check cache first
        if problem_slug in self.explanation_cache:
            return self.explanation_cache[problem_slug]
        
        explanation_file = self.find_community_explanation(problem_slug)
        if not explanation_file:
            return None
        
        try:
            content = explanation_file.read_text(encoding='utf-8')
            metadata, explanation_content = self._parse_explanation_file(content)
            
            explanation_data = {
                'content': explanation_content,
                'metadata': metadata,
                'file_path': explanation_file,
                'last_modified': explanation_file.stat().st_mtime,
                'source': 'community'
            }
            
            # Cache the result
            self.explanation_cache[problem_slug] = explanation_data
            
            logger.info(f"Loaded community explanation for {problem_slug}")
            return explanation_data
            
        except Exception as e:
            logger.error(f"Failed to load community explanation for {problem_slug}: {e}")
            return None
    
    def _parse_explanation_file(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse explanation file with optional front matter metadata.
        
        Args:
            content: Raw explanation file content
            
        Returns:
            Tuple of (metadata, explanation_content)
        """
        # Check for YAML front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    metadata_text = parts[1].strip()
                    metadata = self._parse_yaml_metadata(metadata_text)
                    explanation_content = parts[2].strip()
                    return metadata, explanation_content
                except Exception as e:
                    logger.warning(f"Failed to parse explanation metadata: {e}")
        
        # No front matter, extract metadata from content
        metadata = self._extract_metadata_from_content(content)
        return metadata, content.strip()
    
    def _parse_yaml_metadata(self, yaml_text: str) -> Dict[str, Any]:
        """
        Simple YAML parser for explanation metadata.
        
        Args:
            yaml_text: YAML content
            
        Returns:
            Parsed metadata dictionary
        """
        metadata = {}
        
        for line in yaml_text.split('\\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle lists
                if value.startswith('[') and value.endswith(']'):
                    items = value[1:-1].split(',')
                    metadata[key] = [item.strip().strip('"').strip("'") for item in items]
                # Handle booleans
                elif value.lower() in ['true', 'false']:
                    metadata[key] = value.lower() == 'true'
                # Handle numbers
                elif value.isdigit():
                    metadata[key] = int(value)
                # Handle strings
                else:
                    metadata[key] = value.strip('"').strip("'")
        
        return metadata
    
    def _extract_metadata_from_content(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata from explanation content using heuristics.
        
        Args:
            content: Explanation content
            
        Returns:
            Extracted metadata dictionary
        """
        metadata = {
            'source': 'community',
            'has_code_examples': False,
            'has_complexity_analysis': False,
            'has_step_by_step': False,
            'estimated_reading_time': 0
        }
        
        content_lower = content.lower()
        
        # Check for code examples
        if '```' in content or 'def ' in content or 'class ' in content:
            metadata['has_code_examples'] = True
        
        # Check for complexity analysis
        if any(term in content_lower for term in ['o(', 'time complexity', 'space complexity', 'big o']):
            metadata['has_complexity_analysis'] = True
        
        # Check for step-by-step explanation
        if any(term in content_lower for term in ['step 1', 'step-by-step', 'algorithm:', 'approach:']):
            metadata['has_step_by_step'] = True
        
        # Estimate reading time (average 200 words per minute)
        word_count = len(content.split())
        metadata['estimated_reading_time'] = max(1, word_count // 200)
        metadata['word_count'] = word_count
        
        return metadata
    
    def get_explanation_priority(self, problem_slug: str) -> int:
        """
        Get priority score for community explanation.
        
        Args:
            problem_slug: Problem identifier
            
        Returns:
            Priority score (higher is better)
        """
        explanation_data = self.load_community_explanation(problem_slug)
        if not explanation_data:
            return 0
        
        priority = 100  # Base priority for community explanations
        metadata = explanation_data['metadata']
        
        # Bonus for comprehensive explanations
        if metadata.get('has_code_examples'):
            priority += 20
        if metadata.get('has_complexity_analysis'):
            priority += 15
        if metadata.get('has_step_by_step'):
            priority += 10
        
        # Bonus for longer, more detailed explanations
        word_count = metadata.get('word_count', 0)
        if word_count > 500:
            priority += 10
        elif word_count > 200:
            priority += 5
        
        return priority
    
    def list_problems_with_explanations(self) -> List[str]:
        """
        Get list of problems that have community explanations.
        
        Returns:
            List of problem slugs with community explanations
        """
        problems_with_explanations = []
        
        if not self.problems_dir.exists():
            return problems_with_explanations
        
        for problem_dir in self.problems_dir.iterdir():
            if problem_dir.is_dir():
                problem_slug = problem_dir.name
                if self.find_community_explanation(problem_slug):
                    problems_with_explanations.append(problem_slug)
        
        return sorted(problems_with_explanations)
    
    def get_explanation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about community explanations.
        
        Returns:
            Dictionary with explanation statistics
        """
        problems_with_explanations = self.list_problems_with_explanations()
        
        stats = {
            'total_problems_with_explanations': len(problems_with_explanations),
            'problems': problems_with_explanations,
            'explanation_details': {}
        }
        
        # Get detailed stats for each explanation
        for problem_slug in problems_with_explanations:
            explanation_data = self.load_community_explanation(problem_slug)
            if explanation_data:
                metadata = explanation_data['metadata']
                stats['explanation_details'][problem_slug] = {
                    'word_count': metadata.get('word_count', 0),
                    'reading_time': metadata.get('estimated_reading_time', 0),
                    'has_code_examples': metadata.get('has_code_examples', False),
                    'has_complexity_analysis': metadata.get('has_complexity_analysis', False),
                    'has_step_by_step': metadata.get('has_step_by_step', False),
                    'priority': self.get_explanation_priority(problem_slug)
                }
        
        return stats
    
    def create_explanation_template(self, problem_slug: str, 
                                  problem_title: str = None) -> str:
        """
        Create a template explanation.md file for a problem.
        
        Args:
            problem_slug: Problem identifier
            problem_title: Optional problem title
            
        Returns:
            Template content for explanation.md
        """
        title = problem_title or problem_slug.replace('-', ' ').title()
        
        template = f'''---
title: {title}
difficulty: medium
tags: [algorithm]
author: community
created: {self._get_current_date()}
has_code_examples: true
has_complexity_analysis: true
has_step_by_step: true
---

# {title} - Solution Explanation

## Problem Understanding

[Describe what the problem is asking for in your own words]

## Approach

[Explain the high-level approach to solving this problem]

### Algorithm Steps

1. [Step 1 description]
2. [Step 2 description]
3. [Step 3 description]

## Implementation

```python
def solution():
    # Your solution implementation here
    pass
```

## Complexity Analysis

- **Time Complexity**: O(?) - [Explain why]
- **Space Complexity**: O(?) - [Explain why]

## Example Walkthrough

[Walk through an example step by step]

## Key Insights

- [Key insight 1]
- [Key insight 2]
- [Key insight 3]

## Alternative Approaches

[Discuss other ways to solve this problem]

## Common Pitfalls

- [Common mistake 1]
- [Common mistake 2]

## Related Problems

- [Related problem 1]
- [Related problem 2]
'''
        
        return template
    
    def _get_current_date(self) -> str:
        """Get current date in YYYY-MM-DD format."""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d')
    
    def clear_cache(self):
        """Clear the explanation cache."""
        self.explanation_cache.clear()
        self.metadata_cache.clear()
        logger.info("Community explanation cache cleared")
    
    def reload_explanation(self, problem_slug: str) -> Optional[Dict[str, Any]]:
        """
        Reload explanation from disk, bypassing cache.
        
        Args:
            problem_slug: Problem identifier
            
        Returns:
            Reloaded explanation data or None
        """
        # Remove from cache
        if problem_slug in self.explanation_cache:
            del self.explanation_cache[problem_slug]
        
        # Load fresh from disk
        return self.load_community_explanation(problem_slug)