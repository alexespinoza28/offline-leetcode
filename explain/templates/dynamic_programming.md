---\npatterns: ['dp', 'dynamic', 'fibonacci', 'climb', 'optimal']\ncomplexity: O(n²)\ndifficulty: hard\ntags: ['dynamic-programming', 'optimization']\n---\n\n# Dynamic Programming Solution

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
- DP problems often have multiple valid approaches