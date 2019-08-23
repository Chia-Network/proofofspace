import unittest
from bitstring import BitArray
from src.python.verifier import validate_proof


class TestVerify(unittest.TestCase):
    def test_k25(self):
        seed = bytes.fromhex("022fb42c08c12de3a6af053880199806532e79515f94e83461612101f9412f9e")
        with open("tests/test_vectors/proofs-25.txt") as f:
            lines = f.readlines()
            for i in range(0, len(lines) - 1, 5):
                challenge = bytes.fromhex(lines[i+1].split()[1][2:])
                proof = bytes.fromhex(lines[i+2].split()[1][2:])
                read_quality = BitArray(bin=lines[i+3].split()[1][1:])
                k = int(lines[i+4].split()[5])
                assert(len(challenge) == 256/8)
                assert(len(proof) == 8*k)
                assert(len(read_quality) == 2*k)
                computed_quality = validate_proof(seed, k, challenge, proof)
                assert(computed_quality == read_quality)


if __name__ == '__main__':
    unittest.main()
