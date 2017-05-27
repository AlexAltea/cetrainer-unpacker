CETRAINER files (mod-MrAntiFun)
===============================

This documents covers *CETRAINER* files in the modified Cheat Engine software used in MrAntiFun trainers.

---

## Stand-Alone Executable File (*.EXE*)

UNDOCUMENTED.

## CETRAINER File (*.CETRAINER*)

`CETRAINER` files are protected exactly as described in the original CE docs (see [cetrainer.md](cetrainer.md)), but the XOR-encryptions waves have been altered.

The two first waves remain the same. Quoting from the original documentation:

> * 1st wave is a before-key relationship where the first byte (*x*) starts at 2 and the first XOR key starts at *x-2*.
> * 2nd wave is an after-key relationship where the first byte (*x*) starts at length-2 and the first XOR key starts at *x+1*.

Then, an arbitrary number of static-incrementing key relationship waves are applied using initial keys. As described the original CE docs, these waves are basically:

```cpp
uint8_t ckey = ...; 
for (auto& byte : data) {
    byte ^= ckey++;
}
```

After they are all applied, the rest of the process goes exactly as described by the original CE docs, i.e. skipping the `CHEAT` header and decompressing the remaining data. While MrAntiFun does not seem to update these wave keys per-trainer, he has changed the keys in multiple occasions. There are three possible strategies to deal with his trainers.

### Strategy #1 (`unpack_cet_mrantifun.py`)

Reverse and reimplement every variation. Not really time consuming, as it takes few moments to locate the corresponding code in IDA Pro, and add the key to the database.


### Strategy #2 (*Unimplemented*)

Spawn the modified Cheat Engine with Frida and interecept the decrypted buffer right after decryption finishes. Should be relatively easy to implement but arises once again security concerns.


### Strategy #3 (*Unimplemented*)

Pseudo-bruteforce the key. After applying the two first waves we are left with the buffer `c` of length *N*, and we want to obtain the message `m` by XOR'ing with the unknowns `k0` to `kN-1`. That is:

```
c0 ^ k0 = m0
c1 ^ k1 = m1
c2 ^ k2 = m2
...
```

Since we already know the values of *m0* to *m4* (`CHEAT`), we know *k0* to *k4*. Additionally, we know all *ki* values are derived as follows, where the `+` symbols represent modulo-256 additions:

```
k0 = (x1 + 0) ^ (x2 + 0) ^ ... ^ (xM + 0)
k1 = (x1 + 1) ^ (x2 + 1) ^ ... ^ (xM + 1)
k2 = (x1 + 2) ^ (x2 + 2) ^ ... ^ (xM + 2)
...
```

Our unknowns are *M* and *x1* to *xM*. A possible algorithm to find them is:

```
for M in 0..255:
  for (x1, ..., xM-1) in (0..255)^(M-1):
    xM := k0
    for i in 1..M-1:
      xM ^= xi
    if check(M, x1, ..., xM):
      print "Key found:", M, x1, ..., xM
```

This should be 256 times faster than naive bruteforce, since we need to try *256^M-1* values rather than *256^M*. However, this might be still too slow for keys of 8 or more bytes in size. Finding some nice mathematical property linking XOR and modulo additions, if it exists, might help reducing the computations even further.

The maximum value of *M* is 255 as repeated bytes in the key cancel each other. Furthermore, since XOR is commutative we can enforce *xi* < *xi+1*, reducing the total keys to bruteforce from *256^M-1* to *256 choose M*.