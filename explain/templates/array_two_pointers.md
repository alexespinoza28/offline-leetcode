---\npatterns: ['two-sum', 'three-sum', 'two-pointers', 'array']\ncomplexity: O(n)\ndifficulty: medium\ntags: ['array', 'two-pointers']\n---\n\n# Two Pointers Array Solution

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
- This approach is optimal for problems involving pairs or subarrays