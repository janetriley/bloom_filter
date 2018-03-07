from bloom_filter import BloomFilter, ByteBitVector
from collections import Counter
from sys import getsizeof
import logging

def test_bits_initted_to_zeros():
    bb = ByteBitVector(initial_size=4)
    assert bb.bits == bytearray.fromhex('00000000')

def test_bits_set_and_get():
    bb = ByteBitVector(initial_size=2)
    assert not 1 in bb
    bb.set(1)
    assert 1 in bb
    assert bb.bits == bytearray.fromhex('0001')

def test_vector_resizes_when_capacity_is_reached():
    bb = ByteBitVector(initial_size=2)
    assert len(bb) is 2
    bb.set(1)
    assert len(bb) is 2
    bb.set(2)
    assert 2 in bb

def test_filter_add_and_contains():
    bf = BloomFilter(initial_size=4)
    assert not 'one' in bf
    bf.add('one')
    assert 'one' in bf

def test_false_positives():
    """ see how well it does at false positives"""
    bloom = BloomFilter(initial_size=10, vector_type=ByteBitVector)
    stats = Counter()
    counter = 0
    logging.basicConfig(level=logging.DEBUG)
    with open('./wordlist.txt', 'r', encoding='iso-8859-1') as fp:
        for line in fp:
            term = line.strip()
            contains = term in bloom
            if contains is True:
                counter += 1
                print( counter, "\tTerm already set:\t", term )
            stats.update([str(contains)])
            bloom.add(term)

    false_positives = float(stats[True]/sum(stats.values()))
    print('Count of false positives:', stats, "{:0.04f}%".format(100 * false_positives))
    print('sys.getsizeof filter:', getsizeof(bloom))
    print('sys.getsizeof bitvector needed:', getsizeof(bloom.bitvector.bits))
    print('num bits in vector:', len(bloom.bitvector))
    print('num bitvector set:', bloom.bitvector.num_set())
    # A bit arbitrary - descriptions of bloom filters said 2-3% false positives is pretty good
    assert false_positives <= .03

