import argparse
import logging
from hashlib import md5, sha1
from sys import getsizeof


class ByteBitVector:
    """ A bit vector backed by a bytearray """
    GROW_BY = 1024  # 100 #1024

    def __init__(self, size=GROW_BY):
        MIN_SIZE = 2
        #self.size = max(size, MIN_SIZE)
        self.bits = bytearray()
        self.__grow_bits(max(size, MIN_SIZE))


    def set(self, index):
        """ Add an element to the bit vector """
        if index >= len(self.bits):
            self.__grow_bits(chunk_size=(index - len(self.bits) +1))
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
        #self.bits+= bytearray(chunk_size)
        new_chunk=bytearray(chunk_size)
        self.bits.extend(new_chunk)
        pass

    def __len__(self):
        return len(self.bits)


class BloomFilter:

    NOT_SET = 0 # Leave the first bit as unset, as a default for the getter.

    def __init__(self, vector_type=ByteBitVector, size=0):
        self.lookup = {}
        self.bitvector = vector_type(size)
        self.insert_at_index = self.NOT_SET + 1
        pass

    def add(self, item):
        indices = self.indexes(item)
        for key in indices:
            self.bitvector.set(key)

    def contains(self, term):
        indices = self.indexes(term)
        all_set =  all(index in self.bitvector for index in indices)
        return all_set

    def indexes(self, term):
        # Get the bit vector indexes for the hash term

        keys = self.hash(term)
        #convert to ints
        keys = [ int( '0x' + key, 0) for key in keys]
        return keys

    @classmethod
    def hash(cls, term):
        term = term.encode('utf-8')
        md5_hash = md5(term).hexdigest()
        sha_hash = sha1(term).hexdigest()
        return (md5_hash[:6], md5_hash[-6:])

        #return (md5_hash[-6:], sha_hash[-6:])
        #return (md5_hash[-5:], md5_hash[:5], sha_hash[-5:], sha_hash[:5])

        #return (md5_hash[-2:], sha_hash[-2:])


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


class BloomFilterWithLookupTable:

    NOT_SET = 0 # Leave the first bit as unset, as a default for the getter.

    def __init__(self, vector_type=ByteBitVector, size=0):
        self.lookup = {}
        self.bitvector = vector_type(size)
        self.insert_at_index = self.NOT_SET + 1
        pass

    def add(self, item):
        indices = self.indexes(item)
        for key, value in indices.items():
            if value is BloomFilter.NOT_SET:
                value = self.insert_at_index
                self.lookup[key] = value
                self.insert_at_index += 1
            self.bitvector.set(value)

    def contains(self, term):
        indices = self.indexes(term).values()
        if BloomFilter.NOT_SET in indices:
            return False
        all_set =  all(index in self.bitvector for index in indices)
        return all_set

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
        return (md5_hash[-5:], md5_hash[:5], sha_hash[-5:], sha_hash[5:])

        #return (md5_hash[-2:], sha_hash[-2:])



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
    line_counter = 0.0
    logging.debug('loading {}'.format(args.wordlist))
    with open(args.wordlist, 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            line = line.strip()
            line_counter += 1
            already_there = bloom.contains(line)
            if already_there:
                false_positives += 1
            bloom.add(line)


    print('Num false positives: ', false_positives)
    print('Percent false positives: {:05f}'.format(false_positives / line_counter))
    #print('sys.getsizeof filter:', getsizeof(bloom))
    print('sys.getsizeof lookup table:', getsizeof(bloom.lookup))
    print('keys in lookup:', len(bloom.lookup))
    print('elements in bitvector:', len(bloom.bitvector.bits))
    print('sys.getsizeof bitvector:', getsizeof(bloom.bitvector.bits))
    print('num bits set in vector:', bloom.bitvector.num_set())
