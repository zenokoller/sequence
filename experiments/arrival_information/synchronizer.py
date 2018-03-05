# Given
#   - generator function (e.g. PI or PRG)
#   - seed (e.g.  IP address)
#   - n (bits in chunks)
#   - an iterable that yields n-bit chunks
# the synchronizer outputs List[(offsets, probability)]
# tuples for each packet.

# Hint: Use partial application to get synchronize_pi!
