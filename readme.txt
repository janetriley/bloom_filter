TODO:
+ fixed hashes
+ removed lookup table
[] investigagte issue reading wordlist from command line
[] update writeup
[] analyze hash size - num keys to num bits




GOALS:
A Bloom Filter provides a fast, memory-efficient way to look up set membership.
It's used in scenarios where a normal in-memory lookup is too slow or there are
too many terms to store, and where a certain amount of false positives is acceptable.

RUN:
Written in Python 3.6.  Lower 3x versions of python should be ok.
To run:
    python3 bloom_filter.py wordlist.txt
    python3 bloom_filter.py alice_in_wonderland_words.txt

Tests:
    pytest test.py

*** KNOWN ISSUE***  there's an encoding issue with wordlist.txt - the script stops when I run from the commandline,
works with PyCharm.  The experiments were run with wordlist.txt.   alice_in_wonderland_words.txt is
provided as an alternative.


APPROACH:
"Make it run, make it right, make it fast."  - Kent Beck


MAKE IT RUN: THE MECHANICS
Bloom filters support two operations:  add, and lookup.  There is no delete.
The Bloom Filter class provides this API.


Arrays make lookup simple if you know the index something is stored at. The hash functions return numbers for
the terms, and the keys are the last N digits of the hashed terms.

For the first dumb implementation I used a list of booleans for the bit vector. I switched it to a bytearray to use less
space, and broke the bit vector classes apart from the filter to make it easier to experiment.

I made a C++-flavored assumption that it would be better to allocate vectors in chunks.  I started with big 1024 chunks,
but as the hashing got more efficient, the final size dropped. I ended with a growth factor of 10.


MAKE IT RIGHT
How do I know if it's right? It should  use little memory, be fast, and provide few false positives. This isn't for a
real project, so there's no performance target. I aimed for smaller and more correct.

How do I know if something's a false positive?  Assuming the wordlist is unique, it should report a term
is not contained before it's inserted, and contained afterward. test.py::test_false_positives() checks this.

I experimented with combinations of hash key length and hashing functions. I ran the script with the -m cProfile
option to get profiling information on runtime.  The comparisons are in notes/bloom filter performance numbers.pdf .
Summing up, the biggest determiner of false positives was key length.

In reading about Bloom Filters, I've heard 2-3% is typical and appropriate. Two hashes at length 6 produced about 5%;
length 7 produced .0003%.  There was no difference on false positives based on which hash algorithm I used. For two
of the three combinations, I used keys from the beginning and end of one hexdigest, which saved a second hash computation.

Longer keys meant a wider range of index values. Not surprisingly, these produced larger arrays that were more sparsely
occupied. With key length 4, the vectors were 99% full and 85% false positives.

There are a few tests in tests.py, mainly to ensure the bit vectors are working properly.

MAKE IT FAST
I didn't optimize for speed, so this falls under Future Improvements.

During the profiling above, which included one lookup for false positives and one add, each run took 10-15 seconds on my laptop.
The outlier  was the last experiment, with hash key of length 7; 68 of the 75 seconds were spent counting up how many
bits were used.

If I were to optimize further, I would look into better hashing functions.  Stack Overflow says that jenkins and murmur
are good algorithms because they distribute values well and don't take long to compute.  For a high throughput,
time to hash would become very important.  I had compilation issues installing these packages,
so used the algorithms in hashlib for this experiment/

For real optimization I'd shift to using a more production-like processor and data set.


FUTURE DIRECTIONS

TODO: Figure out why the script can't read wordlist.txt if run from the command line.

* Use a better hash. If I planned to experiment a lot, I'd make the Bloom Filter hash functions a configurable
tuple of lambdas and change the hash function to iterate through them.

* If space were really at a premium, I could start setting actual bits in the byte array. 8 bits to a byte would
drop memory use to 1/8. I'd have to calculate the index with value/8, bit with value % 8, and use bitwise operations to
set and get the bit within the byte.

