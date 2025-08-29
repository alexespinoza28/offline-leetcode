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
        
        for line in yaml_text.split('\\n'):
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
                'content': '''# Two Pointers Array Solution

## Algorithm Overview
This solution uses the **two-pointer technique** to efficiently solve the problem. The two-pointer approach is particularly effective for array problems where we need to find pairs or subarrays that satisfy certain conditions.

### Key Concepts:
- **Left Pointer**: Starts at the beginning of the array
- **Right Pointer**: Starts at the end of the array
- **Convergence**: Pointers move toward each other based on conditions

## Time Complexity
**O(n)** - We traverse the array at most once with both pointers.

## Space Complexity
**O(1)** - Only using constant extra space for the pointers.

## Step-by-Step Approach

1. **Initialize Pointers**
   - Set `left = 0` (start of array)
   - Set `right = n-1` (end of array)

2. **Main Loop**
   - While `left < right`:
     - Calculate current sum/condition
     - If condition is met, return result
     - If sum is too small, move `left` pointer right
     - If sum is too large, move `right` pointer left

3. **Handle Edge Cases**
   - Empty array
   - Single element
   - No valid solution

## Example Walkthrough
```
Array: [2, 7, 11, 15], Target: 9

Step 1: left=0, right=3 → arr[0] + arr[3] = 2 + 15 = 17 > 9
        Move right pointer left
Step 2: left=0, right=2 → arr[0] + arr[2] = 2 + 11 = 13 > 9
        Move right pointer left  
Step 3: left=0, right=1 → arr[0] + arr[1] = 2 + 7 = 9 ✓
        Found solution!
```

## Key Insights
- The two-pointer technique works best on **sorted arrays**
- It eliminates the need for nested loops, reducing time complexity
- The decision to move which pointer depends on the problem's specific conditions
- This approach is optimal for problems involving pairs or subarrays'''
            },
            
            'string_manipulation': {
                'metadata': {
                    'patterns': ['string', 'substring', 'palindrome', 'reverse'],
                    'complexity': 'O(n)',
                    'difficulty': 'easy',
                    'tags': ['string', 'manipulation']
                },
                'content': '''# String Manipulation Solution

## Algorithm Overview
This solution processes the string using **character-by-character manipulation**. String problems often involve pattern recognition, character frequency analysis, or structural transformations.

### Key Concepts:
- **Character Access**: Direct indexing or iteration
- **String Building**: Constructing result strings efficiently
- **Pattern Recognition**: Identifying substrings or character patterns

## Time Complexity
**O(n)** - Single pass through the string where n is the string length.

## Space Complexity
**O(1)** to **O(n)** - Depends on whether we modify in-place or create new strings.

## Step-by-Step Approach

1. **Input Validation**
   - Check for empty or null strings
   - Handle edge cases (single character, etc.)

2. **Character Processing**
   - Iterate through each character
   - Apply transformation logic
   - Track necessary state (counters, flags, etc.)

3. **Result Construction**
   - Build output string or modify in-place
   - Ensure proper formatting

## Common String Techniques

### Two Pointers for Strings
```python
left, right = 0, len(s) - 1
while left < right:
    # Compare or swap characters
    left += 1
    right -= 1
```

### Character Frequency
```python
char_count = {}
for char in string:
    char_count[char] = char_count.get(char, 0) + 1
```

### Sliding Window
```python
window_start = 0
for window_end in range(len(string)):
    # Expand window
    # Contract window if needed
```

## Key Insights
- String immutability in some languages affects space complexity
- Character encoding considerations (ASCII vs Unicode)
- In-place modifications vs creating new strings
- Pattern matching algorithms can optimize substring operations'''
            },
            
            'dynamic_programming': {
                'metadata': {
                    'patterns': ['dp', 'dynamic', 'fibonacci', 'climb', 'optimal'],
                    'complexity': 'O(n²)',
                    'difficulty': 'hard',
                    'tags': ['dynamic-programming', 'optimization']
                },
                'content': '''# Dynamic Programming Solution

## Algorithm Overview
This solution uses **Dynamic Programming (DP)** to solve the problem by breaking it down into overlapping subproblems and storing their solutions to avoid redundant calculations.

### Key Concepts:
- **Optimal Substructure**: Optimal solution contains optimal solutions to subproblems
- **Overlapping Subproblems**: Same subproblems are solved multiple times
- **Memoization**: Store solutions to avoid recomputation

## Time Complexity
**O(n²)** - Typically involves nested loops or recursive calls with memoization.

## Space Complexity
**O(n)** to **O(n²)** - Depends on the DP table size and dimensions.

## DP Approaches

### 1. Top-Down (Memoization)
```python
def solve(n, memo={}):
    if n in memo:
        return memo[n]
    
    # Base cases
    if n <= 1:
        return base_value
    
    # Recursive relation
    memo[n] = solve(n-1, memo) + solve(n-2, memo)
    return memo[n]
```

### 2. Bottom-Up (Tabulation)
```python
def solve(n):
    dp = [0] * (n + 1)
    
    # Base cases
    dp[0] = base_value_0
    dp[1] = base_value_1
    
    # Fill DP table
    for i in range(2, n + 1):
        dp[i] = dp[i-1] + dp[i-2]  # Recurrence relation
    
    return dp[n]
```

## Step-by-Step Approach

1. **Identify the Problem Structure**
   - Can it be broken into smaller subproblems?
   - Do subproblems overlap?
   - Is there optimal substructure?

2. **Define the State**
   - What parameters uniquely identify a subproblem?
   - What does dp[i] represent?

3. **Find the Recurrence Relation**
   - How does dp[i] relate to previous states?
   - What are the base cases?

4. **Choose Implementation**
   - Top-down with memoization
   - Bottom-up with tabulation

5. **Optimize Space (if possible)**
   - Can we reduce space complexity?
   - Do we need the entire DP table?

## Common DP Patterns

### Linear DP
- Fibonacci sequence
- Climbing stairs
- House robber

### 2D DP
- Longest common subsequence
- Edit distance
- Knapsack problems

### State Machine DP
- Best time to buy/sell stock
- State-dependent optimization

## Key Insights
- Start with a recursive solution, then optimize with memoization
- Bottom-up is often more space-efficient
- Look for ways to reduce space complexity (rolling arrays)
- DP problems often have multiple valid approaches'''
            },
            
            'tree_traversal': {
                'metadata': {
                    'patterns': ['tree', 'binary-tree', 'traversal', 'dfs', 'bfs'],
                    'complexity': 'O(n)',
                    'difficulty': 'medium',
                    'tags': ['tree', 'traversal', 'recursion']
                },
                'content': '''# Tree Traversal Solution

## Algorithm Overview
This solution uses **tree traversal** techniques to visit and process nodes in a binary tree. Tree traversal is fundamental to most tree-based algorithms.

### Key Concepts:
- **Depth-First Search (DFS)**: Explore as deep as possible before backtracking
- **Breadth-First Search (BFS)**: Explore level by level
- **Recursive vs Iterative**: Different implementation approaches

## Time Complexity
**O(n)** - We visit each node exactly once, where n is the number of nodes.

## Space Complexity
**O(h)** - Where h is the height of the tree (recursion stack or explicit stack).

## Traversal Types

### DFS Traversals

#### 1. Inorder (Left → Root → Right)
```python
def inorder(root):
    if not root:
        return
    
    inorder(root.left)    # Visit left subtree
    process(root.val)     # Process current node
    inorder(root.right)   # Visit right subtree
```

#### 2. Preorder (Root → Left → Right)
```python
def preorder(root):
    if not root:
        return
    
    process(root.val)     # Process current node
    preorder(root.left)   # Visit left subtree
    preorder(root.right)  # Visit right subtree
```

#### 3. Postorder (Left → Right → Root)
```python
def postorder(root):
    if not root:
        return
    
    postorder(root.left)  # Visit left subtree
    postorder(root.right) # Visit right subtree
    process(root.val)     # Process current node
```

### BFS Traversal (Level Order)
```python
from collections import deque

def level_order(root):
    if not root:
        return
    
    queue = deque([root])
    
    while queue:
        node = queue.popleft()
        process(node.val)
        
        if node.left:
            queue.append(node.left)
        if node.right:
            queue.append(node.right)
```

## When to Use Each Traversal

### Inorder
- Binary Search Trees (gives sorted order)
- Expression trees (infix notation)
- Finding kth smallest element

### Preorder
- Creating a copy of the tree
- Prefix expression evaluation
- Tree serialization

### Postorder
- Deleting nodes safely
- Calculating directory sizes
- Expression tree evaluation

### Level Order
- Finding tree width
- Level-by-level processing
- Finding nodes at specific levels

## Iterative Implementations

### Iterative Inorder
```python
def inorder_iterative(root):
    stack = []
    current = root
    
    while stack or current:
        # Go to leftmost node
        while current:
            stack.append(current)
            current = current.left
        
        # Process node
        current = stack.pop()
        process(current.val)
        
        # Move to right subtree
        current = current.right
```

## Key Insights
- Recursive solutions are often cleaner but use O(h) space
- Iterative solutions can be more memory-efficient
- Choose traversal type based on the problem requirements
- BFS is ideal for level-based problems
- DFS is natural for most tree problems'''
            },
            
            'default': {
                'metadata': {
                    'patterns': ['*'],
                    'complexity': 'O(n)',
                    'difficulty': 'medium',
                    'tags': ['general']
                },
                'content': '''# Solution Explanation

## Algorithm Overview
This solution implements a systematic approach to solve the given problem. The algorithm follows standard programming practices and efficient data structure usage.

## Complexity Analysis
- **Time Complexity**: Depends on the specific algorithm implementation
- **Space Complexity**: Varies based on auxiliary data structures used

## Step-by-Step Approach

1. **Problem Analysis**
   - Understand the input constraints
   - Identify the expected output format
   - Consider edge cases

2. **Algorithm Design**
   - Choose appropriate data structures
   - Design the core logic
   - Plan for edge case handling

3. **Implementation**
   - Write clean, readable code
   - Add necessary error handling
   - Optimize for the given constraints

4. **Testing**
   - Test with provided examples
   - Consider boundary conditions
   - Verify time and space complexity

## Key Considerations
- **Input Validation**: Always validate input parameters
- **Edge Cases**: Handle empty inputs, single elements, etc.
- **Optimization**: Look for opportunities to improve efficiency
- **Code Quality**: Write maintainable and readable code

## Best Practices
- Use meaningful variable names
- Add comments for complex logic
- Follow language-specific conventions
- Consider error handling and robustness'''
            }
        }
        
        # Write default templates to files
        for template_name, template_data in default_templates.items():
            template_file = self.templates_dir / f"{template_name}.md"
            
            # Create front matter
            metadata = template_data['metadata']
            front_matter = "---\\n"
            for key, value in metadata.items():
                if isinstance(value, list):
                    front_matter += f"{key}: {value}\\n"
                else:
                    front_matter += f"{key}: {value}\\n"
            front_matter += "---\\n\\n"
            
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