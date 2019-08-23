# Chia Proof of Space

A prototype of Chia's proof of space, written in C++. Includes a plotter, prover, and verifier.
Only runs on 64 bit architectures with AES-NI support. Read the [Proof of Space document](https://www.chia.net/assets/proof_of_space.pdf) to learn about what proof of space is and how it works.
Read the [contest intro](https://github.com/Chia-Network/proofofspace/blob/master/contest_intro.md) to participate in the Proof of Space Contest.

## C++ Usage Instructions

### Compile

```bash
git submodule init
git submodule update
make
make test
```

### Benchmark

```bash
time ./ProofOfSpace -k 25 generate
```

### Run tests

```bash
./RunTests
```

### CLI usage

```bash
./ProofOfSpace -k 25 -f "plot.dat" -m "0x1234" generate
./ProofOfSpace -f "plot.dat" prove <32 byte hex challenge>
./ProofOfSpace -k 25 verify <hex proof> <32 byte hex challenge>
./ProofOfSpace -f "plot.dat" check <iterations>
```

### Hellman Attacks usage

There is an experimental implementation which implements some of the Hellman Attacks that can provide significant space savings for the final file.


```bash
make hellman
./HellmanAttacks -k 18 -f "plot.dat" -m "0x1234" generate
./HellmanAttacks -f "plot.dat" check <iterations>
```

## Python

Finally, a python implementation is also provided for the verification algorithm.

### Install

```bash
git submodule update --init --recursive
python3 -m venv env
. env/bin/activate
pip3 install .
```

### Run python tests

Testings uses pytest.

```bash
py.test ./tests/python -s
```
