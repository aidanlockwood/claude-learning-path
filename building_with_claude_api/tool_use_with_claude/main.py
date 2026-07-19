def greeting():
    print('Hi There')


def calculate_pi_to_5_digits():
    """
    Calculate pi to the 5th digit using Machin's formula.
    Machin's formula: pi/4 = 4*arctan(1/5) - arctan(1/239)
    
    Returns:
        float: Pi calculated to approximately 5 decimal places (3.14159...)
    """
    from decimal import Decimal, getcontext
    
    # Set precision high enough to calculate 5 digits after decimal point
    getcontext().prec = 50
    
    def arctan(x, num_terms=100):
        """Calculate arctan using Taylor series expansion."""
        x = Decimal(x)
        power = x
        result = power
        for n in range(1, num_terms):
            power *= -x * x
            result += power / (2 * n + 1)
        return result
    
    # Machin's formula: pi/4 = 4*arctan(1/5) - arctan(1/239)
    pi = 4 * (4 * arctan(Decimal(1) / Decimal(5)) - arctan(Decimal(1) / Decimal(239)))
    
    return float(pi)