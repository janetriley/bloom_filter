import argparse
import logging
from hashlib import md5, sha1
from sys import getsizeof


class ByteBitVector:
    """ A bit vector backed by a bytearray """
    GROW_BY = 10  # 100 #1024

    def __init__(self, size):
        MIN_SIZE = 2
        self.size = max(size, MIN_SIZE)
        self.bits = bytearray()
        self.__grow_bits(self.size)


    def set(self, index):
        """ Add an element to the bit vector """
        if index >= len(self.bits):
            self.__grow_bits(chunk_size=(index - len(self.bits)))
            logging.debug("Bit array was too small, grew to {}".format(len(self.bits)))

        self.bits[index] = 1

    def num_set(self):
        return sum(b for b in self.bits)

    def __contains__(self, index):
        if index < len(self.bits):
            return self.bits[index] == 1
        return False

    def __grow_bits(self, chunk_size=0):

        if chunk_size <= 0:
            chunk_size = ByteBitVector.GROW_BY
        self.bits+= bytearray(chunk_size)

    def __len__(self):
        return len(self.bits)


class BloomFilter:

    NOT_SET = 0 # Leave the first bit as unset, as a default for the getter.

    def __init__(self, vector_type=ByteBitVector, size=0):
        self.lookup = {}
        self.bitvector = vector_type(size)
        self.pointer = self.NOT_SET + 1
        pass

    def add(self, item):
        indices = self.indexes(item)
        for key, value in indices.items():
            if value is BloomFilter.NOT_SET:
                value = self.pointer
                self.lookup[key] = value
                self.pointer += 1
            self.bitvector.set(value)
        return
        if not self.contains(item):
            self.lookup[self.hash(item)] = self.pointer
            self.bitvector.set(self.pointer)
            self.pointer += 1

    def contains(self, term):
        indices = self.indexes(term).values()
        if BloomFilter.NOT_SET in indices:
            return False
        return all(index in self.bitvector for index in indices)

    def indexes(self, term):
        # Get the bit vector indexes for the hash term

        keys = self.hash(term)
        # The first bit in the vector was left false,
        # to serve as a default value for missing terms
        # rather than 'if None, ...'
        # for speed.  The theory should be tested to see if it's worth the extra mental complexity.
        return {key: self.lookup.get(key, self.NOT_SET) for key in keys}

    @classmethod
    def hash(cls, term):
        term = term.encode('utf-8')
        md5_hash = md5(term).hexdigest()
        sha_hash = sha1(term).hexdigest()

        return (md5_hash[-2:], sha_hash[-2:])


class BooleanBits:
    def __init__(self, size=0):
        MIN_SIZE = 2
        GROW_BY = 1024

        self.bits = []
        if size:
            self.size = max(size, MIN_SIZE)
        else:
            size = GROW_BY
        self.__grow_bits(self.size)

    def __contains__(self, index):
        if index < len(self.bits):
            return self.bits[index]
        return False

    def set(self, index):
        # set a value
        self.bits[index] = True

    def __grow_bits(self):
        self.bits.extend([False] * self.size)

    def __len__(self):
        return len(self.bits)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A bloom filter. ")
    parser.add_argument("-d", "--debug", help="print debug messages",
                        action="store_true")
    parser.add_argument("wordlist", help="filepath to the word list.")

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    bloom = BloomFilter()
    false_positives =0
    logging.debug('loading {}'.format(args.wordlist))
    with open(args.wordlist, 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            line = line.strip()
            already_there = bloom.contains(line)
            if already_there:
                false_positives += 1
            bloom.add(line)


    print('Num false positives: ', false_positives)
    print('sys.getsizeof filter:', getsizeof(bloom))
    print('size of lookup table:', getsizeof(bloom.lookup))
    print('keys in lookup:', len(bloom.lookup))
    print('sizeof bitvector:', getsizeof(bloom.bitvector.bits))
    print('num bits set in vector:', bloom.bitvector.num_set())
