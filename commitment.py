import hashlib
import sys

secret_seed_commitment = "315e54e4734145dca0d715a59bbc0281cd73e05985a870a987a31b313365d882"
if __name__ == '__main__':
    seed = str.encode(sys.argv[1], "latin-1")
    hash_of_secret = hashlib.sha256(seed).digest()
    assert(hash_of_secret.hex() == secret_seed_commitment)
    new_seed = str.encode(sys.argv[1] + "nonce", "latin-1")
    new_hash = hashlib.sha256(new_seed).digest()
    out = "{" + str(new_hash[0])
    for i in range(1, 32):
        out = out + ", " + str(new_hash[i])   
    out = out + "}"
    print(out)
