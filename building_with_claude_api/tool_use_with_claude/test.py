import math
from main import calculate_pi_to_5_digits


def test_calculate_pi_to_5_digits():
    """Test the calculate_pi_to_5_digits function."""
    
    # Calculate pi using our function
    calculated_pi = calculate_pi_to_5_digits()
    
    # Expected value of pi to 5 decimal places: 3.14159...
    expected_pi = 3.14159
    
    # Python's math.pi for reference
    actual_pi = math.pi
    
    print("=" * 50)
    print("Testing calculate_pi_to_5_digits()")
    print("=" * 50)
    print(f"Calculated pi:     {calculated_pi}")
    print(f"Expected pi:       {expected_pi}...")
    print(f"math.pi (actual):  {actual_pi}")
    print()
    
    # Check if calculated value is close to the expected value (within 5 decimal places)
    # Round to 5 decimal places for comparison
    calculated_rounded = round(calculated_pi, 5)
    expected_rounded = round(actual_pi, 5)
    
    print(f"Calculated (rounded to 5 decimals): {calculated_rounded}")
    print(f"Actual (rounded to 5 decimals):     {expected_rounded}")
    print()
    
    # Test assertions
    try:
        assert round(calculated_pi, 5) == round(actual_pi, 5), \
            f"Calculated pi {calculated_pi} does not match expected value"
        print("✓ Test PASSED: Pi calculated correctly to 5 decimal places!")
        return True
    except AssertionError as e:
        print(f"✗ Test FAILED: {e}")
        return False


if __name__ == "__main__":
    test_calculate_pi_to_5_digits()
