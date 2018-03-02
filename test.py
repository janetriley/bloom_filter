from bloom_filter import BloomFilter
from collections import Counter
from sys import getsizeof

def test_init():
    bf = BloomFilter(size=4)
    #assert bf.bits == [False, False, False, False]
    assert bf.bits == bytearray.fromhex('00000000')


def test_add_and_contains():
    bf = BloomFilter(size=4)
    bf.add('one')
    assert bf.hash('one') in bf.lookup
    #assert bf.bits ==[False, True, False, False]
    assert bf.bits ==bytearray.fromhex('00010000')
    assert bf.contains('one')

def test_auto_resize():
    bf = BloomFilter(size=2)
    assert len(bf.bits) is 2
    bf.add('one')
    assert len(bf.bits) is 2 * 2
    bf.add('two')
    bf.add('three')
    assert len(bf.bits) is 3 * 2


def test_false_positives():
    bloom = BloomFilter(size=100000)
    stats = Counter()

    with open('./wordlist.txt', 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            term = line.strip()
            contains = str(bloom.contains(term))
            stats.update([contains])
            bloom.add(term)
    print(stats)
    print(getsizeof(bloom))
    print(getsizeof(bloom.lookup))
    print(getsizeof(bloom.bits))
