---\npatterns: ['tree', 'binary-tree', 'traversal', 'dfs', 'bfs']\ncomplexity: O(n)\ndifficulty: medium\ntags: ['tree', 'traversal', 'recursion']\n---\n\n# Tree Traversal Solution

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
- DFS is natural for most tree problems