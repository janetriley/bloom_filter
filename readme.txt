
GOALS:
A Bloom Filter provides a fast, memory-efficient way to look up set membership.
It's used in scenarios where a normal in-memory lookup is too slow or there are
too many terms to store, and where a certain amount of false positives is acceptable.

RUN:
Written in Python 3.6.  Lower 3x versions of python should be ok.
To run:
    python3 bloom_filter.py wordlist.txt
Tests:
    pytest test.py


APPROACH:
"Make it run, make it right, make it fast."  - Kent Beck


MAKE IT RUN: THE MECHANICS
Bloom filters support two operations:  add, and lookup.  There is no delete.
The Bloom Filter class provides this API.

For the first dumb implementation I used a list of booleans for the bit vector,
and returned the term as-is as the hash.

Arrays make lookup simple if you know the index something is stored at. The Bloom Filter maintains a lookup dict,
where the key is the hashed term and the value is the index in the array. It maintains a pointer to the next index to insert at.
The bit vectors will increase their size as necessary behind the scenes. 

I switched the boolean vector for a bytearray after the first pass, and broke the vector classes out of the filter to make it easier to experiment.
One byte-length element in an array will be smaller than one pointer-length element in a list. If I tried a third kind of structure I would
take a hard look at using inheritance for the bit vectors, to abstract out repetitions. 

I made a C++-flavored assumption that it would be better to allocate vectors in chunks.  I started with big 1024 chunks, but as the hashing
got more efficient, the final size dropped. I ended with a growth factor of 10. 


MAKE IT RIGHT
How do I know if it's right? It should  use little memory, be fast, and provide few false positives. This isn't for a real project, so
there's no performance target. I aimed for smaller and more correct.

How do I know if something's a false positive, without loading a hugew wordlist into memory?  Assuming the wordlist is unique, it should
report a term is not contained before it's inserted, and contained afterward.  test.py::test_false_positives() checks this. 

***********
KNOWN ISSUE
***********
... and so ironic:  in this implementation, almost everything is producing a false positive.  In ByteVector::__grow_size, the array is
extended with a new array. The new one should be filled with zeros. In the debugger, I see it is not.  Future Improvement.
***********
/KNOWN ISSUE
***********

I can measure smaller by the size of the bit vector.  I also checked the number of values set.  I'm curious if the values are 
distributed evenly, or if there are only a few flags set.  I'd have to think more about how to determine if it's good-
I'd like to see fewer negatives, and would probably just observe under different conditions to see what the average is. 
However, I'd rather burn memory than performance time, and wouldn't make it a priority unless there were memory constraints. 

There are a few tests in tests.py, mainly to ensure the bit vectors are working properly. 

For the first-pass mock hash, it required N bits, as you'd expect.  For the second hash, I returned the full digest value and got about the same result.
I trimmed the returned hash size to 8, then 6, (1% false positive, , 5, and 4.   


**** 
See above - due to the false positive issue above, the % false positive and bits set is inaccurate. 
The keys in lookup is unaffected, however, and we can see later hashes require fewer keys. 
****

key len	  keys in lookup    % false positive    num bits set
6      	  335489 	    1%	   		65146   
5	  289682	    14%			289682
4	  65146		    19%			65146


Hasing the term twice made a dramatic difference.  Using two hashes, with hash key trimmed to length 2, 
key len	   keys in lookup    % false positive    num bits set
2 @ 2each  256	   	     .05%    		 256

Reading about bloom filters,  I heared 2-3% false positive mentioned as typical and acceptable. 


MAKE IT FAST
I didn't optimize for speed, so this falls under Future Improvements.

I would optimize hashing functions.  Stack Overflow says that jenkins and murmur are good choices because they distribute values well
and don't take long to compute.  For a high throughput, time to hash would become very important.  I had compilation issues
installing these packages, so went with the algorithms in hashlib. 

These completed quickly on my laptop.  I'd run it with the profile option set and bigger wordlists to compile some stats. 

If we needed optimization, I'd shift to using a more representative processor and data set. 


FUTURE DIRECTIONS
Fix the byte array initialization and rerun calculations. 

Would a set work better than a lookup table and indicies?  It costs to maintain the lookup table and adds some mental complexity.
It's probably not a win, but I'm curious. 

Could I get the same results by taking the first and last N characters of a single hash?  I'd have two keys for the cost of one hash. 
Are they different enough to give the same kind of random variety as two hashes?

If I wanted to experiment with different hashes, I'd add a field to BloomFilter
for hash functions, and make the hash method iterate through them.



