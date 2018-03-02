from bloom_filter import BloomFilter, ByteBitVector
from collections import Counter
from sys import getsizeof


def test_bits_init():
    bb = ByteBitVector(size=4)
    assert bb.bits == bytearray.fromhex('00000000')

def test_bits_set_and_get():
    bb = ByteBitVector(size=2)
    assert not 1 in bb
    bb.set(1)
    assert 1 in bb
    assert bb.bits == bytearray.fromhex('0001')

def test_vector_resizes_when_capacity_is_reached():
    bb = ByteBitVector(size=2)
    assert len(bb) is 2
    bb.set(1)
    assert len(bb) is 2
    bb.set(2)
    assert 2 in bb


def test_add_and_contains():
    bf = BloomFilter(size=4)
    assert not bf.contains('one')

    bf.add('one')
    assert bf.contains('one')

def test_false_positives():
    bloom = BloomFilter(size=1024, vector_type=ByteBitVector)
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
