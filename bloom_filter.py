import argparse
import argparse
import logging


# http://codekata.com/kata/kata05-bloom-filters/


class BloomFilter:
    CHUNK_SIZE = 1024
    MIN_SIZE = 2
    NOT_SET = 0

    def __init__(self, size=CHUNK_SIZE):
        self.lookup = {}
        self.size = max(size, BloomFilter.MIN_SIZE)
        # self.bits = [False] * self.size
        self.bits = bytearray(self.size)
        self.pointer = self.NOT_SET + 1
        pass

    def add(self, item):
        if not self.contains(item):
            self.lookup[self.hash(item)] = self.pointer
            self.__set_bit(self.pointer)
            # self.bits[self.pointer] = True
            self.pointer += 1
            if self.pointer >= len(self.bits):
                self.__grow_bits()

    def __set_bit(self, index):
        self.bits[self.pointer] = 1

    def __grow_bits(self):
        self.bits.extend([False] * self.size)

    def contains(self, term):
        key = self.hash(term)
        index = self.lookup.get(key, self.NOT_SET)
        return self.bits[index] is not 0

    def hash(self, term):
        return term


class ByteBits:
    CHUNK_SIZE = 1024
    MIN_SIZE = 2

    def __init__(self, size):
        self.size = max(size, BooleanBits.MIN_SIZE)
        self.bits = bytearray(self.size)

    def is_set(self, index):
        if index < len(self.bits):
            return self.bits[index] is not 0
        return False

    def set(self, index):
        if index >= len(self.bits):
            self.__grow_bits(chunk_size=(index - len(self.bits)))
            logging.debug("Bit array was too small, grew to {}".format(len(self.bits)))

        self.bits[index] = 1


    def __grow_bits(self, chunk_size=None):
        if chunk_size is None:
            chunk_size = self.size

        self.bits += bytearray(chunk_size)


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

    logging.debug("Final lookup table size:{}\nFinal bit len:{}\n".format(len(bloom.lookup), len(bloom.bits)))
