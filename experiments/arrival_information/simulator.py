# Given simulation parameters (model, param1, ..., paramN) for
#   - loss
#   - reordering
#   - duplication
# take an iterable of n bit chunks and reorder the chunks according
# to the model

# Hint: define a uniform interface for policy functions and chain them
# to get complex policies.
# Thus, the simulator takes a `List[PolicyFn]`
# where `PolicyFn = Callable[[Iterable[BitChunk]],Iterable[BitChunk]]`

# TODO: Create a test setup first!
