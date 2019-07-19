"""
Author: Federico Sevilla III
Email:  jijo@free.net.ph
Date:   2002-01-30

ChangeLog:
    + Tue Jul 02 08:35:23 PHT 2002
      - update #! line
      - update email address
    + Wed Feb 13 11:45:16 PHT 2002
      - commit Eric Pareja's improved loop for isPrime()

"""

def isPrime(x):
    '''isPrime(int x) --> boolean
    isPrime(x) checks if a given number x is prime. It follows the following
    decision tree:
        if x is 1 it is a special case (ie: not prime),
        if x is either 2 or 3, it is prime,
        if x is even, it is not prime.
        if x is not one of these obvious cases:
            check if x is divisible by the numbers in the range from 3 to
            floor(sqrt(x)).
    '''       

    import math

    if (x == 1):                    # Special case, neither prime nor composite
        return None
    elif ((x == 2) or (x == 3)):
        return x
    elif ((x % 2) == 0):
        return None
    else:
        flag = 0
        i = 3
        while 1:
            if (x % i) == 0:
                return 0
            elif (i * i) > x:
                return 1
            i += 2
