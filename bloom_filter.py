import argparse
import argparse
import logging
from hashlib import md5, sha1


# http://codekata.com/kata/kata05-bloom-filters/

class ByteBits:
    CHUNK_SIZE = 10#0#1024

    def __init__(self, size):
        MIN_SIZE = 2
        self.size = max(size, MIN_SIZE)
        self.bits = bytearray(self.size)

    def contains(self, index):
        if index < len(self.bits):
            return self.bits[index] is not 0
        return False

    def set(self, index):
        if index >= len(self.bits):
            self.__grow_bits(chunk_size=(index - len(self.bits)))
            logging.debug("Bit array was too small, grew to {}".format(len(self.bits)))

        self.bits[index] = 1

    def __grow_bits(self, chunk_size=0):
        if chunk_size <= 0:
            chunk_size = ByteBits.CHUNK_SIZE

        self.bits.extend(bytearray(chunk_size))

    def __len__(self):
        return len(self.bits)

    def num_set(self):
        return sum(b for b in self.bits)


class BloomFilter:
    NOT_SET = 0

    def __init__(self, vector_type=ByteBits, size=0):
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
        return all(self.bitvector.contains(index) for index in indices)

    def indexes(self, term):
        keys = self.hash(term)
        return { key:self.lookup.get(key,self.NOT_SET) for key in keys }

    @classmethod
    def hash(cls, term):
        term = term.encode('utf-8')
        masher=md5(term).hexdigest()
        shanana = sha1(term).hexdigest()
        #hasher.update(term.encode('utf-8'))

        return (masher[-2:], shanana[-2:])


class BooleanBits:
    def __init__(self, size=0):
        MIN_SIZE = 2
        CHUNK_SIZE = 1024

        self.bits = []
        if size:
            self.size = max(size, MIN_SIZE)
        else:
            size = CHUNK_SIZE
        self.__grow_bits(self.size)

    def contains(self, index):
        if index < len(self.bits):
            return self.bits[index]
        return False

    def set(self, index):
        self.bits[index] = True

    def __grow_bits(self):
        self.bits.extend([False] * self.size)

    def __len__(self):
        return len(self.bits)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", help="print debug messages",
                        action="store_true")
    parser.add_argument("wordlist", help="where to load the words from")

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    bloom = BloomFilter()
    logging.debug('loading {}'.format(args.wordlist))
    with open(args.wordlist, 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            bloom.add(line.strip())

    logging.debug('verifying words')
    with open(args.wordlist, 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            term = line.strip()
            try:
                assert bloom.contains(term)
            except AssertionError as e:
                logging.error("Filter is missing ", term)

    logging.debug("Final lookup table size:{}\nFinal bit len:{}\n".format(len(bloom.lookup), len(bloom.bitvector)))
