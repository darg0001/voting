import constants

import random

"""
Use a pseudo random number generator to get a random bit vector of length n
"""
def random_bit_vector(n):
  return [random.randint(0, 1) for _ in range(n)]

"""
Generates a random bit vector with exactly number_of_ones ones
"""
def random_bit_vector_proportion(n, number_of_ones):
  output = [1] * number_of_ones + [0] * (n - number_of_ones)
  random.shuffle(output)
  return output

def boolean_vector_to_bit_vector(boolean_vector):
  return [1 if boolean else 0 for boolean in boolean_vector]

def boolean_vector_to_bit_string(boolean_vector):
  bit_string = ""
  for boolean in boolean_vector:
    if boolean:
      bit_string += "1"
    else:
      bit_string += "0"
  return bit_string

"""
Converts a vector of bits to an integer
"""
def bit_vector_to_int(bit_vector):
  output = 0
  for bit in bit_vector:
    output = (output << 1) | bit
  return output

"""
Toy encoding scheme for mapping small integer values to
a boolean vector more appropriate for use in cryptographic algorithms
"""
def encode_int(n):
  assert(n < constants.ENCODED_VOTE_SIZE)
  return [True if i % n == 0 else False for i in range(1, constants.ENCODED_VOTE_SIZE+ 1)]

"""
Uses Justesen codes to map (encode) bit vectors
of size m to bit vectors of size q = 2^m

Currently uses a dummy implementation, eventually
to be replaced with Justesen code
"""
def error_checking_encode(bit_vector):
  chunk_size = (2**len(bit_vector)) / len(bit_vector)
  code = []
  for bit in bit_vector:
    chunk = [1] * chunk_size if bit == 1 else [0] * chunk_size
    code += chunk
  return code

"""
Decodes codes created by error_checking_encode
"""
def error_checking_decode(bit_vector):
  chunk_size = len(bit_vector) / constants.ENCODED_VOTE_SIZE
  decoded = []
  for i in range(0, len(bit_vector), chunk_size):
    decoded[i] = bit_vector[i]
  return decoded

"""
Constructs the key to be XOR'ed with the vote during commitment
"""
def get_commit_key(seed, bit_vector):
  q = len(bit_vector) / 2
  one_indices = []
  for i in range(len(bit_vector)):
    if bit_vector[i] == 1:
      one_indices.append(i)
  random.seed(bit_vector_to_int(seed))
  seeded_sequence = random_bit_vector(q * 2)
  key = [0] * q
  for i in range(q):
    key[i] = seeded_sequence[one_indices[i]]
  return key

def commit_to_bits(encoded_vote, key):
  assert(len(encoded_vote) == len(key))
  return [encoded_vote[i] ^ key[i] for i in range(len(encoded_vote))]

if __name__ == "__main__":
  main()
