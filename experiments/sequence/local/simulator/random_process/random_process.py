from typing import Generator

"""The functions in this module return a generator that yields boolean values,
drawn from some stochastic process.
Example:

    process = ar1()
    draw = next(process)
"""
RandomProcess = Generator[bool, None, None]
