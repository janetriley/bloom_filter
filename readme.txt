GOALS:

A Bloom filter provides a fast, memory-efficient way to look up
set membership. It's used in scenarios where a normal in-memory lookup
is too slow or there are too many terms to store, and where a certain
amount of false positives is acceptable.

This is an implementation of the Bloom filter code kata (http://codekata.com/kata/kata05-bloom-filters/).

RUN:
Written in Python 3.6.  Lower 3x versions of python should be ok.
To run:
    python3 bloom_filter.py wordlist.txt

Tests:
    pytest test.py


APPROACH:
"Make it run, make it right, make it fast."  - Kent Beck


MAKE IT RUN: THE MECHANICS

Bloom filters support two operations: add, and lookup.  There is no delete.
The BloomFilter class provides this API.


Arrays make lookup simple if you know the index something is stored
at. The hash functions return numbers for the terms, and the keys are
the last N digits of the hashed terms.

For the first dumb implementation I used a list of booleans for the
bit vector. I switched it to a bytearray to use less space, and broke
the bit vector classes apart from the filter to make it easier to
experiment.

I made a C++-flavored assumption that it would be better to allocate
vectors in chunks.  I started with big 1024 chunks, but as the hashing
got more efficient, the final size dropped. I ended with a growth
factor of 10.


MAKE IT RIGHT
How do I know if it's right? It should use little memory,
be fast, and provide few false positives. This isn't for a
real project, so there's no performance target. I aimed for smaller
and more correct.

How do I know if something's a false positive?  Assuming the wordlist
is unique, it should report a term is not contained before it's
inserted, and contained afterward. test.py::test_false_positives()
checks this.

I experimented with combinations of hash key length and hashing
functions. I ran the script with the python3 -m cProfile option to get
profiling information on runtime.  The comparisons are in
notes/bloom_filter_performance_numbers.pdf .


In reading about Bloom filters, I've heard 2-3% false positivesis typical and
appropriate. T the biggest determiner of false positives was key length.
Two hashes at length 6 produced about 5%; length 7 produced .0003%.

There was no difference on false positives based on which
hash algorithm I used. For two of the three combinations, I used
keys from the beginning and end of one hexdigest, which saved a second
hash computation.

Longer keys meant a wider range of index values. Not surprisingly,
these produced larger arrays that were more sparsely occupied. With
key length 4, the vectors were 99% full and 85% false positives.

There are a few tests in tests.py, mainly to ensure the bit vectors
are working properly.


MAKE IT FAST
I didn't optimize for speed, so this falls under Future Improvements.

During the profiling above, which included one lookup for false
positives and one add per term, each run took 10-15 seconds on my laptop. The
outlier was the last experiment, with hash key of length 7; 68 of the
75 seconds were spent counting up how many bits were used in the final reporting.

If I were to optimize further, I would look into better hashing
functions.  Stack Overflow says that jenkins and murmur are good
algorithms because they distribute values well and don't take long to
compute.  For a high throughput, time to hash would become very
important.  I had compilation issues installing these packages, so
used the algorithms in hashlib for this experiment/

For real optimization I'd shift to using a more production-like
processor and data set.


FUTURE DIRECTIONS

* Use a better hash. If I planned to experiment a
lot, I'd make the Bloom filter hash functions a configurable tuple of
lambdas and change the hash function to iterate through them.

* If space were really at a premium, I could start setting actual bits
  in the byte array. 8 bits to a byte would drop memory use to
  1/8. I'd have to calculate the index with value/8, bit with value %
  8, and use bitwise operations to set and get the bit within the
  byte.
