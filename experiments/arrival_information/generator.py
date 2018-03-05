# Given
#   - generator function (e.g. PI or PRG),
#   - seed (e.g.  IP address) and offset),
#   - offset,
#   - n (bits in chunks)
# `generator` generates a predictable pseudorandom sequence that we can query
# with an iterable that yields n bit chunks.

# Hint: Use partial application to get generate_pi!