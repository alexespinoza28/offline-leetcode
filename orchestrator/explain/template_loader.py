#!/usr/bin/env python3
"""
Template loader for explanation system.

This module handles loading and managing explanation templates with
pattern-based template selection and variable substitution.
"""

import os
import re
import json
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class TemplateLoader:
    """
    Loads and manages explanation templates with pattern matching.
    
    Supports:
    - Pattern-based template selection
    - Variable substitution
    - Template inheritance
    - Markdown template rendering
    """
    
    def __init__(self, templates_dir: str = "explain/templates"):
        """
        Initialize template loader. 
        
        Args:
            templates_dir: Directory containing explanation templates
        """
        self.templates_dir = Path(templates_dir)
        self.templates_cache = {}
        self.pattern_cache = {}
        self._load_templates()
    
    def _load_templates(self):
        """Load all templates from the templates directory."""
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            self._create_default_templates()
            return
        
        # Load template files
        for template_file in self.templates_dir.glob("*.md"):
            template_name = template_file.stem
            try:
                content = template_file.read_text(encoding='utf-8')
                metadata, template_content = self._parse_template(content)
                
                self.templates_cache[template_name] = {
                    'content': template_content,
                    'metadata': metadata,
                    'file_path': template_file
                }
                
                # Cache patterns for quick lookup
                patterns = metadata.get('patterns', [])
                for pattern in patterns:
                    if pattern not in self.pattern_cache:
                        self.pattern_cache[pattern] = []
                    self.pattern_cache[pattern].append(template_name)
                
                logger.debug(f"Loaded template: {template_name}")
                
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
    
    def _parse_template(self, content: str) -> Tuple[Dict[str, Any], str]:
        """
        Parse template file with front matter metadata.
        
        Args:
            content: Raw template content
            
        Returns:
            Tuple of (metadata, template_content)
        """
        # Check for YAML front matter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                try:
                    # Simple YAML-like parsing for metadata
                    metadata_text = parts[1].strip()
                    metadata = self._parse_simple_yaml(metadata_text)
                    template_content = parts[2].strip()
                    return metadata, template_content
                except Exception as e:
                    logger.warning(f"Failed to parse template metadata: {e}")
        
        # No front matter, return empty metadata
        return {}, content.strip()
    
    def _parse_simple_yaml(self, yaml_text: str) -> Dict[str, Any]:
        """
        Simple YAML parser for template metadata.
        
        Args:
            yaml_text: YAML content
            
        Returns:
            Parsed metadata dictionary
        """
        metadata = {}
        
        for line in yaml_text.split('\n'):
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle lists
                if value.startswith('[') and value.endswith(']'):
                    # Simple list parsing
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
    
    def _create_default_templates(self):
        """Create default templates if none exist."""
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        
        default_templates = {
            'array_two_pointers': {
                'metadata': {
                    'patterns': ['two-sum', 'three-sum', 'two-pointers', 'array'],
                    'complexity': 'O(n)',
                    'difficulty': 'medium',
                    'tags': ['array', 'two-pointers']
                },
                'content': '# Two Pointers Array Solution\n\n## Algorithm Overview\nThis solution uses the **two-pointer technique** to efficiently solve the problem. The two-pointer approach is particularly effective for array problems where we need to find pairs or subarrays that satisfy certain conditions.\n\n### Key Concepts:\n- **Left Pointer**: Starts at the beginning of the array\n- **Right Pointer**: Starts at the end of the array\n- **Convergence**: Pointers move toward each other based on conditions\n\n## Time Complexity\n**O(n)** - We traverse the array at most once with both pointers.\n\n## Space Complexity\n**O(1)** - Only using constant extra space for the pointers.\n\n## Step-by-Step Approach\n\n1. **Initialize Pointers**\n   - Set `left = 0` (start of array)\n   - Set `right = n-1` (end of array)\n\n2. **Main Loop**\n   - While `left < right`:\n     - Calculate current sum/condition\n     - If condition is met, return result\n     - If sum is too small, move `left` pointer right\n     - If sum is too large, move `right` pointer left\n\n3. **Handle Edge Cases**\n   - Empty array\n   - Single element\n   - No valid solution\n\n## Example Walkthrough\n```\nArray: [2, 7, 11, 15], Target: 9\n\nStep 1: left=0, right=3 → arr[0] + arr[3] = 2 + 15 = 17 > 9\n        Move right pointer left\nStep 2: left=0, right=2 → arr[0] + arr[2] = 2 + 11 = 13 > 9\n        Move right pointer left  \nStep 3: left=0, right=1 → arr[0] + arr[1] = 2 + 7 = 9 ✓\n        Found solution!\n```\n\n## Key Insights\n- The two-pointer technique works best on **sorted arrays**\n- It eliminates the need for nested loops, reducing time complexity\n- The decision to move which pointer depends on the problem\'s specific conditions\n- This approach is optimal for problems involving pairs or subarrays'
            },
            
            'string_manipulation': {
                'metadata': {
                    'patterns': ['string', 'substring', 'palindrome', 'reverse'],
                    'complexity': 'O(n)',
                    'difficulty': 'easy',
                    'tags': ['string', 'manipulation']
                },
                'content': '# String Manipulation Solution\n\n## Algorithm Overview\nThis solution processes the string using **character-by-character manipulation**. String problems often involve pattern recognition, character frequency analysis, or structural transformations.\n\n### Key Concepts:\n- **Character Access**: Direct indexing or iteration\n- **String Building**: Constructing result strings efficiently\n- **Pattern Recognition**: Identifying substrings or character patterns\n\n## Time Complexity\n**O(n)** - Single pass through the string where n is the string length.\n\n## Space Complexity\n**O(1)** to **O(n)** - Depends on whether we modify in-place or create new strings.\n\n## Step-by-Step Approach\n\n1. **Input Validation**\n   - Check for empty or null strings\n   - Handle edge cases (single character, etc.)\n\n2. **Character Processing**\n   - Iterate through each character\n   - Apply transformation logic\n   - Track necessary state (counters, flags, etc.)\n\n3. **Result Construction**\n   - Build output string or modify in-place\n   - Ensure proper formatting\n\n## Common String Techniques\n\n### Two Pointers for Strings\n```python\nleft, right = 0, len(s) - 1\nwhile left < right:\n    # Compare or swap characters\n    left += 1\n    right -= 1\n```\n\n### Character Frequency\n```python\nchar_count = {}\nfor char in string:\n    char_count[char] = char_count.get(char, 0) + 1\n```\n\n### Sliding Window\n```python\nwindow_start = 0\nfor window_end in range(len(string)):\n    # Expand window\n    # Contract window if needed\n```\n\n## Key Insights\n- String immutability in some languages affects space complexity\n- Character encoding considerations (ASCII vs Unicode)\n- In-place modifications vs creating new strings\n- Pattern matching algorithms can optimize substring operations'
            },
            
            'dynamic_programming': {
                'metadata': {
                    'patterns': ['dp', 'dynamic', 'fibonacci', 'climb', 'optimal'],
                    'complexity': 'O(n²)',
                    'difficulty': 'hard',
                    'tags': ['dynamic-programming', 'optimization']
                },
                'content': '# Dynamic Programming Solution\n\n## Algorithm Overview\nThis solution uses **Dynamic Programming (DP)** to solve the problem by breaking it down into overlapping subproblems and storing their solutions to avoid redundant calculations.\n\n### Key Concepts:\n- **Optimal Substructure**: Optimal solution contains optimal solutions to subproblems\n- **Overlapping Subproblems**: Same subproblems are solved multiple times\n- **Memoization**: Store solutions to avoid recomputation\n\n## Time Complexity\n**O(n²)** - Typically involves nested loops or recursive calls with memoization.\n\n## Space Complexity\n**O(n)** to **O(n²)** - Depends on the DP table size and dimensions.\n\n## DP Approaches\n\n### 1. Top-Down (Memoization)\n```python\ndef solve(n, memo={}):\n    if n in memo:\n        return memo[n]\n    \n    # Base cases\n    if n <= 1:\n        return base_value\n    \n    # Recursive relation\n    memo[n] = solve(n-1, memo) + solve(n-2, memo)\n    return memo[n]\n```\n\n### 2. Bottom-Up (Tabulation)\n```python\ndef solve(n):\n    dp = [0] * (n + 1)\n    \n    # Base cases\n    dp[0] = base_value_0\n    dp[1] = base_value_1\n    \n    # Fill DP table\n    for i in range(2, n + 1):\n        dp[i] = dp[i-1] + dp[i-2]  # Recurrence relation\n    \n    return dp[n]\n```\n\n## Step-by-Step Approach\n\n1. **Identify the Problem Structure**\n   - Can it be broken into smaller subproblems?\n   - Do subproblems overlap?\n   - Is there optimal substructure?\n\n2. **Define the State**\n   - What parameters uniquely identify a subproblem?\n   - What does dp[i] represent?\n\n3. **Find the Recurrence Relation**\n   - How does dp[i] relate to previous states?\n   - What are the base cases?\n\n4. **Choose Implementation**\n   - Top-down with memoization\n   - Bottom-up with tabulation\n\n5. **Optimize Space (if possible)**\n   - Can we reduce space complexity?\n   - Do we need the entire DP table?\n\n## Common DP Patterns\n\n### Linear DP\n- Fibonacci sequence\n- Climbing stairs\n- House robber\n\n### 2D DP\n- Longest common subsequence\n- Edit distance\n- Knapsack problems\n\n### State Machine DP\n- Best time to buy/sell stock\n- State-dependent optimization\n\n## Key Insights\n- Start with a recursive solution, then optimize with memoization\n- Bottom-up is often more space-efficient\n- Look for ways to reduce space complexity (rolling arrays)\n- DP problems often have multiple valid approaches'
            },
            
            'tree_traversal': {
                'metadata': {
                    'patterns': ['tree', 'binary-tree', 'traversal', 'dfs', 'bfs'],
                    'complexity': 'O(n)',
                    'difficulty': 'medium',
                    'tags': ['tree', 'traversal', 'recursion']
                },
                'content': '# Tree Traversal Solution\n\n## Algorithm Overview\nThis solution uses **tree traversal** techniques to visit and process nodes in a binary tree. Tree traversal is fundamental to most tree-based algorithms.\n\n### Key Concepts:\n- **Depth-First Search (DFS)**: Explore as deep as possible before backtracking\n- **Breadth-First Search (BFS)**: Explore level by level\n- **Recursive vs Iterative**: Different implementation approaches\n\n## Time Complexity\n**O(n)** - We visit each node exactly once, where n is the number of nodes.\n\n## Space Complexity\n**O(h)** - Where h is the height of the tree (recursion stack or explicit stack).\n\n## Traversal Types\n\n### DFS Traversals\n\n#### 1. Inorder (Left → Root → Right)\n```python\ndef inorder(root):\n    if not root:\n        return\n    \n    inorder(root.left)    # Visit left subtree\n    process(root.val)     # Process current node\n    inorder(root.right)   # Visit right subtree\n```\n\n#### 2. Preorder (Root → Left → Right)\n```python\ndef preorder(root):\n    if not root:\n        return\n    \n    process(root.val)     # Process current node\n    preorder(root.left)   # Visit left subtree\n    preorder(root.right)  # Visit right subtree\n```\n\n#### 3. Postorder (Left → Right → Root)\n```python\ndef postorder(root):\n    if not root:\n        return\n    \n    postorder(root.left)  # Visit left subtree\n    postorder(root.right) # Visit right subtree\n    process(root.val)     # Process current node\n```\n\n### BFS Traversal (Level Order)\n```python\nfrom collections import deque\n\ndef level_order(root):\n    if not root:\n        return\n    \n    queue = deque([root])\n    \n    while queue:\n        node = queue.popleft()\n        process(node.val)\n        \n        if node.left:\n            queue.append(node.left)\n        if node.right:\n            queue.append(node.right)\n```\n\n## When to Use Each Traversal\n\n### Inorder\n- Binary Search Trees (gives sorted order)\n- Expression trees (infix notation)\n- Finding kth smallest element\n\n### Preorder\n- Creating a copy of the tree\n- Prefix expression evaluation\n- Tree serialization\n\n### Postorder\n- Deleting nodes safely\n- Calculating directory sizes\n- Expression tree evaluation\n\n### Level Order\n- Finding tree width\n- Level-by-level processing\n- Finding nodes at specific levels\n\n## Iterative Implementations\n\n### Iterative Inorder\n```python\ndef inorder_iterative(root):\n    stack = []\n    current = root\n    \n    while stack or current:\n        # Go to leftmost node\n        while current:\n            stack.append(current)\n            current = current.left\n        \n        # Process node\n        current = stack.pop()\n        process(current.val)\n        \n        # Move to right subtree\n        current = current.right\n```\n\n## Key Insights\n- Recursive solutions are often cleaner but use O(h) space\n- Iterative solutions can be more memory-efficient\n- Choose traversal type based on the problem requirements\n- BFS is ideal for level-based problems\n- DFS is natural for most tree problems'
            },
            
            'default': {
                'metadata': {
                    'patterns': ['*'],
                    'complexity': 'O(n)',
                    'difficulty': 'medium',
                    'tags': ['general']
                },
                'content': '# Solution Explanation\n\n## Algorithm Overview\nThis solution implements a systematic approach to solve the given problem. The algorithm follows standard programming practices and efficient data structure usage.\n\n## Complexity Analysis\n- **Time Complexity**: Depends on the specific algorithm implementation\n- **Space Complexity**: Varies based on auxiliary data structures used\n\n## Step-by-Step Approach\n\n1. **Problem Analysis**\n   - Understand the input constraints\n   - Identify the expected output format\n   - Consider edge cases\n\n2. **Algorithm Design**\n   - Choose appropriate data structures\n   - Design the core logic\n   - Plan for edge case handling\n\n3. **Implementation**\n   - Write clean, readable code\n   - Add necessary error handling\n   - Optimize for the given constraints\n\n4. **Testing**\n   - Test with provided examples\n   - Consider boundary conditions\n   - Verify time and space complexity\n\n## Key Considerations\n- **Input Validation**: Always validate input parameters\n- **Edge Cases**: Handle empty inputs, single elements, etc.\n- **Optimization**: Look for opportunities to improve efficiency\n- **Code Quality**: Write maintainable and readable code\n\n## Best Practices\n- Use meaningful variable names\n- Add comments for complex logic\n- Follow language-specific conventions\n- Consider error handling and robustness'
            }
        }
        
        # Write default templates to files
        for template_name, template_data in default_templates.items():
            template_file = self.templates_dir / f"{template_name}.md"
            
            # Create front matter
            metadata = template_data['metadata']
            front_matter = "---"
            for key, value in metadata.items():
                if isinstance(value, list):
                    front_matter += f"{key}: {value}"
                else:
                    front_matter += f"{key}: {value}"
            front_matter += "---"
            
            # Write template file
            full_content = front_matter + template_data['content']
            template_file.write_text(full_content, encoding='utf-8')
            
            logger.info(f"Created default template: {template_name}")
        
        # Reload templates after creating defaults
        self._load_templates()
    
    def find_template(self, problem_slug: str, tags: List[str] = None, 
                     difficulty: str = None) -> Optional[str]:
        """
        Find the best matching template for a problem.
        
        Args:
            problem_slug: Problem identifier
            tags: Problem tags
            difficulty: Problem difficulty level
            
        Returns:
            Template name or None if no match found
        """
        slug_lower = problem_slug.lower()
        
        # Score templates based on pattern matching
        template_scores = {}
        
        for template_name, template_data in self.templates_cache.items():
            score = 0
            metadata = template_data['metadata']
            patterns = metadata.get('patterns', [])
            
            # Check pattern matching
            for pattern in patterns:
                if pattern == '*':  # Wildcard pattern
                    score += 1
                elif pattern.lower() in slug_lower:
                    score += 10  # High score for slug match
                elif tags and any(pattern.lower() in tag.lower() for tag in tags):
                    score += 5   # Medium score for tag match
            
            # Bonus for difficulty match
            if difficulty and metadata.get('difficulty') == difficulty.lower():
                score += 2
            
            if score > 0:
                template_scores[template_name] = score
        
        # Return template with highest score
        if template_scores:
            best_template = max(template_scores.items(), key=lambda x: x[1])
            logger.debug(f"Selected template '{best_template[0]}' with score {best_template[1]} for problem '{problem_slug}'")
            return best_template[0]
        
        # Fallback to default template
        return 'default' if 'default' in self.templates_cache else None
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render template with variable substitution.
        
        Args:
            template_name: Name of template to render
            variables: Variables for substitution
            
        Returns:
            Rendered template content
        """
        if template_name not in self.templates_cache:
            logger.error(f"Template not found: {template_name}")
            return f"Template '{template_name}' not found."
        
        template_data = self.templates_cache[template_name]
        content = template_data['content']
        
        # Simple variable substitution
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, str(var_value))
        
        return content
    
    def get_template_metadata(self, template_name: str) -> Dict[str, Any]:
        """
        Get metadata for a template.
        
        Args:
            template_name: Name of template
            
        Returns:
            Template metadata dictionary
        """
        if template_name in self.templates_cache:
            return self.templates_cache[template_name]['metadata'].copy()
        return {}
    
    def list_templates(self) -> List[str]:
        """Get list of available template names."""
        return list(self.templates_cache.keys())
    
    def reload_templates(self):
        """Reload all templates from disk."""
        self.templates_cache.clear()
        self.pattern_cache.clear()
        self._load_templates()
        logger.info("Templates reloaded")
