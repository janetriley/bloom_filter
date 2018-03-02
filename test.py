from bloom_filter import BloomFilter, ByteBits
from collections import Counter
from sys import getsizeof


def test_bits_init():
    bb = ByteBits(size=4)
    assert bb.bits == bytearray.fromhex('00000000')

def test_bits_set_and_get():
    bb = ByteBits(size=2)
    assert not bb.contains(1)
    bb.set(1)
    assert bb.contains(1)
    assert bb.bits == bytearray.fromhex('0001')

def test_bits_resize():
    bb = ByteBits(size=2)
    assert len(bb) is 2
    bb.set(1)
    assert len(bb) is 2
    bb.set(2)
    assert bb.contains(2)


def test_add_and_contains():
    bf = BloomFilter(size=4)
    bf.add('one')
    assert bf.contains('one')

def test_false_positives():
    bloom = BloomFilter(size=1024, vector_type=ByteBits)
    stats = Counter()

    with open('./wordlist.txt', 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            term = line.strip()
            contains = str(bloom.contains(term))
            stats.update([contains])
            bloom.add(term)
    print(stats)
    print('size of filter:', getsizeof(bloom))
    print('size of lookup:', getsizeof(bloom.lookup))
    print('keys in lookup:', len(bloom.lookup))

    print('sizeof bitvector needed:', getsizeof(bloom.bitvector.bits))
    print('num bitvector set:', bloom.bitvector.num_set())

def test_hash_returns_collection():
    values = BloomFilter.hash("blah")
    assert len(values) >= 1