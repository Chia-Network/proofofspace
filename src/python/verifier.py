from bitstring import BitArray
from .calculate_bucket import F1Calculator, FxCalculator


def compare_arrays(arr1, arr2):
    """
    Compares starting at last element, then second to last, etc.
    """
    assert(len(arr1) == len(arr2))
    for i in range(len(arr1) - 1, -1, -1):
        if arr1[i].uint < arr2[i].uint:
            return True
        if arr1[i].uint > arr2[i].uint:
            return False
    return False


def get_quality_string(k, proof, quality_index):
    """
    Recovers the quality string. In order to do this, the proof must be converted
    from proof ordering to disk ordering. Disk ordering is determined by looking at
    the maximum value in list, and putting that on the right. When comparing two
    lists, first the maximum value is compared, then the next largest, etc.
    """

    proof = [(a,) for a in proof]
    for table_index in range(1, 7):
        new_proof = []
        for j in range(0, 2**(7 - table_index), 2):
            L, R = proof[j], proof[j+1]
            if compare_arrays(list(L), list(R)):
                new_proof.append(L + R)
            else:
                new_proof.append(R + L)
        proof = new_proof
    proof = list(sum(proof, ()))
    return proof[quality_index] + proof[quality_index + 1]


def validate_proof(ident, k, challenge, proof_bytes):
    """
    Returns the quality string if proof is a valid proof of space for
    space parameter k. length of proof is (64 * k) // 8 bytes.
    """
    challenge = int.from_bytes(challenge, "big")
    proof_bits = BitArray(proof_bytes)
    if k*64 != len(proof_bits):
        print("bad lengtH")
        return None

    proof = [proof_bits[i*k:(i+1)*k] for i in range(64)]

    f1 = F1Calculator(k, ident)
    f1_results = [f1.calculate_bucket(proof[i]) for i in range(64)]
    ys, metadata = zip(*f1_results)

    # Calculates f2 through f7
    for depth in range(2, 8):
        f = FxCalculator(k, depth, ident)
        new_ys = []
        new_metadata = []
        for i in range(0, 2**(8 - depth), 2):
            matches = f.find_matches([ys[i]], [ys[i+1]], k)
            if len(matches) != 1:
                return None
            new_ys.append(f.f(metadata[i], metadata[i+1]) ^ ys[i])
            new_metadata.append(f.compose(metadata[i], metadata[i+1]))

        ys, metadata = new_ys, new_metadata

    truncated = BitArray(uint=(challenge >> (256-k)), length=(k))
    quality_index = (challenge & 31) << 1

    if truncated == ys[0][:k]:
        return get_quality_string(k, proof, quality_index)
    else:
        return None
