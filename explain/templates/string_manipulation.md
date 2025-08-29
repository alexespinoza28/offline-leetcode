---\npatterns: ['string', 'substring', 'palindrome', 'reverse']\ncomplexity: O(n)\ndifficulty: easy\ntags: ['string', 'manipulation']\n---\n\n# String Manipulation Solution

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
- Pattern matching algorithms can optimize substring operations