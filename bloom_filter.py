import argparse
import logging
from hashlib import md5, sha1
from sys import getsizeof


class ByteBitVector:
    """ A bit vector backed by a bytearray """
    GROW_BY = 1 #128  #10 #1024

    def __init__(self, initial_size=GROW_BY):
        self.bits = bytearray()
        self.size = len(self.bits)
        self.__grow(initial_size)

    def set(self, index):
        """ Add an element to the bit vector """
        if index >= len(self.bits):
            self.__grow(chunk_size=(index - len(self.bits) + 1))
            logging.debug("Bit array was too small, grew to {}".format(len(self.bits)))

        self.bits[index] = 1

    def num_set(self):
        """ How many flags were set? """
        return sum(b for b in self.bits)

    def __contains__(self, index):
        """
        Is this bit set?
        :param index: byte to examine
        :return: boolean
        """
        if index < self.size:
            return self.bits[index] == 1
        return False

    def __grow(self, chunk_size=0):
        """ Expand the size of the array """
        if chunk_size <= 0:
            chunk_size = ByteBitVector.GROW_BY

        self.bits.extend(bytearray(chunk_size))
        self.size = len(self.bits)

    def __len__(self):
        return len(self.bits)


class BloomFilter:
    def __init__(self, vector_type=ByteBitVector, initial_size=0):
        self.bitvector = vector_type(initial_size)

    def add(self, item):
        """
        Add an item
        :param item: an object to store
        """
        indices = self.__indexes(item)
        for key in indices:
            self.bitvector.set(key)

    def __contains__(self, item):
        """
        Has the bit been set for this item?
        :param item: object to look up
        :return: boolean
        """
        indices = self.__indexes(item)
        all_set = all(index in self.bitvector for index in indices)
        return all_set

    @classmethod
    def __indexes(cls, term):
        # Get the bit vector indexes for the hash term
        keys = cls.hash(term)
        # convert to ints
        keys = [int('0x' + key, 0) for key in keys]
        return keys

    @classmethod
    def hash(cls, term):
        """
        Generate lookup indexes for the term
        :param term: a hashable value
        :return: a tuple of strings, each string a hex values
        """
        term = term.encode('utf-8')
        md5_hash = md5(term).hexdigest()
        sha_hash = sha1(term).hexdigest()
        NUM=6
        return (md5_hash[-NUM:], sha_hash[-NUM:])
        # trying different combinations
        #return (sha_hash[:NUM], sha_hash[-NUM:])
        #return (md5_hash[:NUM], md5_hash[-NUM:])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A bloom filter. ")
    parser.add_argument("-d", "--debug", help="print debug messages",
                        action="store_true")
    parser.add_argument("wordlist", help="filepath to the word list.")

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)

    bloom = BloomFilter()
    false_positives = 0
    line_counter = 0.0
    logging.debug('loading {}'.format(args.wordlist))
    with open(args.wordlist, 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            line = line.strip()
            line_counter += 1
            already_there = line in bloom
            if already_there:
                false_positives += 1
            bloom.add(line)

    print('Num false positives: ', false_positives)
    print('Percent false positives: {:05f}'.format(false_positives / line_counter))
    # print('sys.getsizeof filter:', getsizeof(bloom))
    print('elements in bitvector:', len(bloom.bitvector.bits))
    print('sys.getsizeof bitvector:', getsizeof(bloom.bitvector.bits))
    print('num bits set in vector:', bloom.bitvector.num_set())
