### Okareo Interview Solution

# A six-sided dice is thrown repeatedly with results recorded as int[]. 
# Each time we can only see three sides - top, front, right (bottom, left, back are hidden). 

# The visible sides are recorded in the order top, front, right. So for example [1,2,3] is top = 1, front = 2, and right = 3. Each side could be a number 1 to 50.

# Multiple throws are recorded as [ [1,2,3], [1,3,6], [1,25,45]...]

# We need to check that these historical throws data is consistent with respect to a single six-sided dice. 

# Write a method consistent(throws list[list[int]]) → int. 
# The method returns 1 based index of the first entry in throws history that is inconsistent with respect to previous ones. If all the historical data is consistent the method should return 0.

# Examples / Test Cases (PLEASE see next page)

#[[1,2,3], [26,3,2]] Returns 0

# First throw 26 is on the bottom, second throw 26 is on top.


# [[1,2,3], [4,5,6], [2,3,1], [7,8,9]]  Returns 4

# [7,8,9] can’t happen because that would be more than 6 different labels


# [[1,2,1], [3,4,5]] Returns 1

# First throw two sides are labeled as 1.



def consistent(throws: list[list[int]]) -> int:
    """
    Check if dice throws are consistent with a single six-sided die.
    
    Args:
        throws: List of throws, each throw is [top, front, right]
    
    Returns:
        1-based index of first inconsistent throw, or 0 if all consistent
    """
    if not throws:
        return 0
    
    # Track all unique labels we've seen
    all_labels = set()

    # Track the dice configuration
    ordered_throws = dict()  # Track ordered throws
    
    def process_orientation(top, front, right):
        """Check if the orientation (top, front) is consistent with the right face."""
        if (top, front) in ordered_throws:
            if ordered_throws[(top, front)] != right:
                return False
            return True
        else:
            ordered_throws[(top, front)] = right
            return True
    
    # Iterate through each throw and check for consistency
    for i, throw in enumerate(throws):
        # Check if the throw has exactly 3 values
        if not isinstance(throw, list) or len(throw) != 3:
            return i + 1
        
        # Check for duplicate faces in same throw
        if len(set(throw)) != 3:
            return i + 1

        # Check if we have too many unique labels (more than 6)
        all_labels.update(set(throw))
        if len(all_labels) > 6:
            return i + 1

        # Unpack the throw
        top, front, right = throw

        # Check orientation is consistent with previous throws by reorienting cube
        # We can check the following orientations
        # (top, front) -> right
        # (front, right) -> top
        # (right, top) -> front
        # If any of these orientations are inconsistent, return the index
        # of the throw that caused the inconsistency.
        if not process_orientation(top, front, right) or \
           not process_orientation(front, right, top) or \
           not process_orientation(right, top, front):
            return i + 1
    
    # If we reach here, all throws are consistent
    return 0

# Test cases

def test_consistency():
    test_cases = [
        # Basic test cases

        # Valid Orientation flipped but all sides are consistent with dice structure
        ([[1,2,3], [26,3,2]], 0, "Valid orientation flip"),

        # Invalid More than 6 unique labels used by the 4th throw
        ([[1,2,3], [4,5,6], [2,3,1], [7,8,9]], 4, "Too many unique labels"),

        # Invalid Same label used more than once in a single throw
        ([[1,2,1], [3,4,5]], 1, "Duplicate face in single throw"),

        # Edge cases

        # Valid Single throw, cannot conflict
        ([[1,2,3]], 0, "Single throw"),

        # Valid No throws at all
        ([], 0, "Empty input"),

        # Invalid Second throw is an empty list
        ([[1,2,3], [], [4,5,6]], 2, "Empty throw"),

        # Invalid Second throw has only 2 values
        ([[1,2,3], [4,5], [6,7,8]], 2, "Incomplete throw"),

        # Invalid Second throw has 4 values (too many)
        ([[1,2,3], [4,5,6,7]], 2, "Too many values in throw"),

        # Orientation consistency tests

        # Valid Different faces seen in different configurations, still consistent
        ([[1,2,3], [4,5,6]], 0, "Valid cube flip"),

        # Invalid Once orientation is established, [1,2,5] contradicts it
        ([[1,2,3], [4,5,6], [1,2,5]], 3, "Invalid orientation"),

        # Invalid [2,6,1] breaks the orientation established in the first throw
        ([[1,2,3], [2,6,1], [3,1,2]], 2, "Complex valid rotations"),

        # Valid Repeated same orientation seen again — fine
        ([[1,2,3], [5,6,4], [1,2,3]], 0, "Repeated orientation"),

        ## Opposite face consistency tests

        # Invalid Face 1 appears twice in the same throw
        ([[1,2,3], [1,2,1]], 2, "Face appears as both visible and hidden"),

        # Valid Opposite faces assigned consistently across throws
        ([[1,2,3], [4,5,6], [2,3,1], [5,6,4]], 0, "Consistent opposite relationships"),

        # Invalid Conflicts with established opposite relationships
        ([[1,2,3], [4,5,6], [1,5,3]], 3, "Violating opposite relationships"),

        ## Boundary tests

        # Invalid 7th unique label introduced in 3rd throw
        ([[1,2,3], [4,5,6], [7,1,2]], 3, "7 unique labels"),

        # Invalid All three values in the same throw are identical
        ([[1,1,1]], 1, "All same numbers"),

        # Valid Numbers reused across throws but total unique labels ≤ 6
        ([[1,2,3], [1,4,5]], 0, "Reusing numbers across throws"),

        ## Additional edge cases

        # Valid Reordered visible faces (doesn't violate orientation yet)
        ([[1,2,3], [2,1,3]], 0, "Valid face reordering"),

        # Valid Same orientation repeated
        ([[1,2,3], [1,2,3]], 0, "Identical consecutive throws"),

        # Valid Alternating between two valid orientations using same labels
        ([[1,2,3], [4,5,6], [1,2,3], [4,5,6]], 0, "Alternating valid patterns"),

        # Invalid Partial overlap with existing orientation breaks consistency
        ([[1,2,3], [4,2,3]], 2, "Partial face overlap"),

        ## Complex cases

        # Valid Rotating cube 180° while using same label on top
        ([[20, 6, 18], [20, 12, 6]], 0, "Rotate 180 degrees"),

        # Invalid Violates earlier seen opposite face pairs at throw 6
        ([[20, 6, 18], [20, 12, 6], [20, 2, 12], [20, 18, 2], [21, 18, 6], [21, 12, 6]], 6, "Complex valid sequence with violation"),

        # Valid Full sequence rotates faces but remains geometrically consistent
        ([[20, 6, 18], [20, 12, 6], [20, 2, 12], [20, 18, 2], [21, 18, 6], [21, 6, 12]], 0, "Complex valid sequence with last throw consistent"),
]
  
    passed = 0
    failed = 0
    
    # Iterate through test cases and check results
    
    for i, (test_input, expected, description) in enumerate(test_cases):
        try:
            result = consistent(test_input)
            assert result == expected, f"Expected {expected}, got {result}"
            print(f"✓ Test {i+1}: {description} - PASSED")
            passed += 1
        except AssertionError as e:
            print(f"✗ Test {i+1}: {description} - FAILED: {e}")
            failed += 1
            break
        except Exception as e:
            print(f"✗ Test {i+1}: {description} - ERROR: {e}")
            failed += 1
    
    print("\n=== Test Summary ===")
    print(f"Total test cases: {len(test_cases)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed == 0:
        print("🎉 All tests passed!")
    else:
        print(f"❌ {failed} test(s) failed")

# Run tests

test_consistency()    