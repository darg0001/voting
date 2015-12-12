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

  @staticmethod
  def int_to_bit_vector(n):
    return [int(x) for x in bin(int(n))[2:]]

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

  Currently uses a toy implementation, eventually
  to be replaced with Justesen code
  """
  @staticmethod
  def error_checking_encode(n):
    bit_vector = CryptoObject.int_to_bit_vector(n)
    return ([0] * (constants.ENCODED_VOTE_SIZE - len(bit_vector))) + bit_vector

  """
  Decodes codes created by error_checking_encode
  """
  @staticmethod
  def error_checking_decode(bit_vector):
    return CryptoObject.bit_vector_to_int(bit_vector[:constants.ENCODED_VOTE_SIZE])

  """
  Constructs the key to be XOR'ed with the bit vector during commitment
  """
  def get_commit_key(self, bit_vector):
    one_indices = []
    for i in range(len(bit_vector)):
      if bit_vector[i] == 1:
        one_indices.append(i)
    assert(len(one_indices) == len(bit_vector) / 2)
    seeded_sequence = self.random_bit_vector(len(one_indices) * 2)
    key = [0] * (len(one_indices))
    for i in range(len(key)):
      key[i] = seeded_sequence[one_indices[i]]
    self.logger.debug_log("Bit-commitment key: " + str(CryptoObject.bit_vector_to_int(key)))
    return key

  def commit(self, bit_vector, r):
    key = self.get_commit_key(r)
    # key = self.random_bit_vector_proportion(len(bit_vector), len(bit_vector) / 2)
    assert(len(bit_vector) == len(key))
    commitment = [bit_vector[i] ^ key[i] for i in range(len(bit_vector))]
    self.logger.debug_log("Bit-commitment: " + str(CryptoObject.bit_vector_to_int(commitment)))
    commitment = CryptoObject.bit_vector_to_int(commitment)
    assert(commitment < (constants.RSA_P * constants.RSA_Q))
    return (key, commitment)

  @staticmethod
  def check_commit(commitment, commit_key):
    return [commitment[i] ^ commit_key[i] for i in range(len(commitment))]

class Signature(FiniteFieldCryptoObject):

  def __init__(self, p, q, e):
    FiniteFieldCryptoObject.__init__(self, constants.SIGNATURE_TAG, p * q)
    assert(fractions.gcd((p-1)*(q-1), e) == 1)
    self.p = p
    self.q = q
    self.e = e
    self.d = self.get_inverse_mod(self.e, (self.p - 1) * (self.q - 1))

  @staticmethod
  def hash(n):
    modulus = (constants.RSA_P - 1) * (constants.RSA_Q - 1)
    return int(hashlib.md5(str(n)).hexdigest(), 16) % modulus

  def sign(self, n):
    return pow(int(n), self.d, self.modulus)

  # This should be separated from signing
  def verify(self, n):
    return pow(int(n), self.e, self.modulus)

class Blinder(FiniteFieldCryptoObject):

  def __init__(self, p, q, e):
    FiniteFieldCryptoObject.__init__(self, constants.BLIND_SIGNATURE_TAG, p * q)
    self.p = p
    self.q = q
    self.e = e
    self.r = CryptoObject.bit_vector_to_int(CryptoObject.random_bit_vector(constants.ENCODED_VOTE_SIZE))

  def blind(self, n):
    return (int(n) * pow(self.r, self.e, self.modulus)) % self.modulus

  def retrieve(self, n):
    return (int(n) * self.get_inverse(self.r)) % self.modulus

if __name__ == "__main__":
  main()
