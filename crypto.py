import constants
import logger

import fractions
import hashlib
import random

class CryptoObject(object):

  def __init__(self, prefix):
    self.prefix = prefix
    self.logger = logger.Logger(self.prefix)
    # self.logger.enable_debug_mode()

  @staticmethod
  def random_bit_vector(size):
    return [random.randint(0, 1) for _ in range(size)]

  @staticmethod
  def random_bit_vector_proportion(size, number_of_ones):
    bit_vector = [1] * number_of_ones + [0] * (size - number_of_ones)
    random.shuffle(bit_vector)
    return bit_vector

  @staticmethod
  def bit_vector_to_string(bit_vector):
    return ''.join([str(bit) for bit in bit_vector])

  @staticmethod
  def bit_vector_to_int(bit_vector):
    output = 0
    for bit in bit_vector:
      output = (output << 1) | bit
    return output

  """
  Toy encoding scheme for mapping small integer values to
  a boolean vector more appropriate for use in cryptographic algorithms
  """
  @staticmethod
  def encode_int(n):
    assert(n < constants.ENCODED_VOTE_SIZE)
    return [True if i % n == 0 else False for i in range(1, constants.ENCODED_VOTE_SIZE+ 1)]

class SeededCryptoObject(CryptoObject):

  def __init__(self, prefix, seed):
    CryptoObject.__init__(self, prefix)
    self.random = random.Random()
    self.random.seed(seed)

  def random_bit_vector(self, size):
    return [self.random.randint(0, 1) for _ in range(size)]

  def random_bit_vector_proportion(self, size, number_of_ones):
    bit_vector = [1] * number_of_ones + [0] * (size - number_of_ones)
    self.random.shuffle(bit_vector)
    return bit_vector

class FiniteFieldCryptoObject(CryptoObject):

  def __init__(self, prefix, modulus):
    CryptoObject.__init__(self, prefix)
    self.modulus = modulus

  @staticmethod
  def get_inverse_mod(n, modulus):
    n %= modulus
    t, newt, r, newr = (0, 1, modulus, n)
    while newr != 0:
      q = r // newr
      (t, newt) = (newt, t - q * newt)
      (r, newr) = (newr, r - q * newr)
    assert r <= 1
    if t < 0:
      t += modulus
    return t

  def get_inverse(self, n):
    return FiniteFieldCryptoObject.get_inverse_mod(n, self.modulus)

class BitCommit(SeededCryptoObject):

  def __init__(self, seed):
    SeededCryptoObject.__init__(self, constants.BIT_COMMIT_TAG, seed)

  """
  Uses Justesen codes to map (encode) bit vectors
  of size m to bit vectors of size q = 2^m

  Currently uses a dummy implementation, eventually
  to be replaced with Justesen code
  """
  def error_checking_encode(self, bit_vector):
    chunk_size = (2**len(bit_vector)) / len(bit_vector)
    code = []
    for bit in bit_vector:
      chunk = [1] * chunk_size if bit == 1 else [0] * chunk_size
      code += chunk
    self.logger.debug_log("Error checking code: " + str(CryptoObject.bit_vector_to_int(code)))
    return code

  """
  Decodes codes created by error_checking_encode
  """
  def error_checking_decode(self, bit_vector):
    chunk_size = len(bit_vector) / constants.ENCODED_VOTE_SIZE
    decoded = []
    for i in range(0, len(bit_vector), chunk_size):
      decoded[i] = bit_vector[i]
    return decoded

  """
  Constructs the key to be XOR'ed with the bit vector during commitment
  """
  def get_commit_key(self, bit_vector):
    one_indices = []
    for i in range(len(bit_vector)):
      if bit_vector[i] == 1:
        one_indices.append(i)
    seeded_sequence = self.random_bit_vector(len(bit_vector))
    key = [0] * (len(bit_vector) / 2)
    for i in range(len(key)):
      key[i] = seeded_sequence[one_indices[i]]
    self.logger.debug_log("Bit-commitment key: " + str(CryptoObject.bit_vector_to_int(key)))
    return key

  def commit(self, bit_vector, r):
    key = self.get_commit_key(r)
    assert(len(bit_vector) == len(key))
    commitment = [bit_vector[i] ^ key[i] for i in range(len(bit_vector))]
    self.logger.debug_log("Bit-commitment: " + str(CryptoObject.bit_vector_to_int(commitment)))
    return commitment

  def check_commit(self, commitment):
    pass

class BlindSignature(FiniteFieldCryptoObject):

  def __init__(self, modulus):
    FiniteFieldCryptoObject.__init__(self, constants.BLIND_SIGNATURE_TAG, modulus)

  def set_r(self, r):
    self.r = r

  def blind_sign(self, n):
    return pow(int(n), self.get_inverse(constants.BLIND_SIGNATURE_PUBLIC_KEY), self.modulus)

  def verify(self, n):
    return (pow(int(n), constants.BLIND_SIGNATURE_PUBLIC_KEY, self.modulus) * self.get_inverse(self.r)) % self.modulus

class Signature(FiniteFieldCryptoObject):

  def __init__(self, p, q, e):
    FiniteFieldCryptoObject.__init__(self, constants.SIGNATURE_TAG, p * q)
    assert(fractions.gcd((p-1)*(q-1), e) == 1)
    self.p = p
    self.q = q
    self.e = e
    self.n = (p * q) % self.modulus
    self.d = self.get_inverse_mod(self.e, (self.p - 1) * (self.q - 1))

  @staticmethod
  def hash(n):
    modulus = (constants.RSA_P - 1) * (constants.RSA_Q - 1)
    return int(hashlib.md5(str(n)).hexdigest(), 16) % modulus

  def sign(self, n):
    return pow(self.hash(n), self.d, self.modulus)

  def verify(self, n):
    return pow(int(n), self.e, self.modulus)

if __name__ == "__main__":
  main()
