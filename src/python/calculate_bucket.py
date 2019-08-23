from bitstring import BitArray
import os
import cppimport

curr_path = os.path.dirname(os.path.realpath(__file__))
aes = cppimport.imp("src.python.aes")

# The block size of encryption
BS_BITS = 128

# Extra bits to be added at the end of the y value. This gives us more
# data that we can use for the matching function. Instead of f being
# a function f:k bits -> k bits, it's f:k bits -> k+EXTRA_BITS bits.
EXTRA_BITS = 5

EXTRA_BITS_POW = 2 ** EXTRA_BITS

vector_lens = {
    2: 1,
    3: 2,
    4: 4,
    5: 4,
    6: 3,
    7: 2,
    8: 0,
}

# B and C groups, used to compute matches.
B_param = 60
C_param = 509
BC_param = B_param * C_param

# Precomputation necessary to compute matches
matching_shifts_c = [[0] * C_param for _ in range(2)]
for parity in range(2):
    for r in range(EXTRA_BITS_POW):
        v = ((2 * r + parity) ** 2) % C_param
        matching_shifts_c[parity][r] = v


def pad(arr, bitlen):
    while len(arr) % bitlen != 0:
        arr += [0]
    return arr


class F1Calculator():
    def __init__(self, k, key):
        assert(len(key) == 32)  # 32 bytes, for AES256
        self.k = k
        self.key = bytes([1]) + key[:31]
        self.reload_key()

    def encrypt(self, input_bits):
        assert(len(input_bits) == BS_BITS)
        return BitArray(aes.encrypt256(input_bits.bytes))

    def reload_key(self):
        aes.load_key(self.key, 32)  # Unique key for each table

    # Evaluates f1 at exactly one value. Only one input L.
    def f(self, L):
        num_output_bits = self.k
        # Calculate index
        counter = (L.uint * num_output_bits) // BS_BITS
        bits_before_L = (L.uint * num_output_bits) % BS_BITS
        bits_of_L = min(BS_BITS - bits_before_L, num_output_bits)

        spans_two_blocks = bits_of_L < num_output_bits

        if spans_two_blocks:
            ciphertext0 = self.encrypt(BitArray(uint=counter, length=BS_BITS))
            ciphertext1 = self.encrypt(BitArray(uint=counter+1, length=BS_BITS))
            output_bits = ciphertext0[bits_before_L:] + ciphertext1[:num_output_bits - bits_of_L]
        else:
            ciphertext1 = self.encrypt(BitArray(uint=counter, length=BS_BITS))
            output_bits = ciphertext1[bits_before_L:bits_before_L + num_output_bits]

        extra_data = L[:EXTRA_BITS]
        if len(extra_data) < EXTRA_BITS:
            extra_data += BitArray(uint=0, length=(EXTRA_BITS - len(extra_data)))

        return output_bits + extra_data

    # Evaluates f1 at exactly one value, L
    def calculate_bucket(self, L):
        return (self.f(L), L)

    # Evaluates f1 at startL up to startL + number_of_evaluations. This is more efficient
    # than calling calculate_bucket multiple times.
    def calculate_buckets(self, startL, number_of_evaluations):
        if startL.uint + number_of_evaluations > (2**self.k):
            raise Exception("Evaluation out of range")

        num_output_bits = self.k
        counter = (startL.uint * num_output_bits) // BS_BITS
        counter_end = (((startL.uint + number_of_evaluations + 1) * num_output_bits)
                       // BS_BITS)
        blocks = []
        L = (counter * BS_BITS) // num_output_bits

        while counter <= counter_end:
            ciphertext = self.encrypt(BitArray(uint=counter, length=BS_BITS))
            blocks.append(ciphertext)
            counter += 1

        results = []
        block_number = 0
        start_bit = (startL.uint * num_output_bits) % BS_BITS
        for L in range(startL.uint, startL.uint + number_of_evaluations):
            extra_data = BitArray(uint=L, length=self.k)[:EXTRA_BITS]
            if len(extra_data) < EXTRA_BITS:
                extra_data += BitArray(uint=0, length=(EXTRA_BITS - len(extra_data)))
            if start_bit + num_output_bits < BS_BITS:
                results.append((blocks[block_number][start_bit:start_bit + num_output_bits] + extra_data,
                               BitArray(uint=L, length=self.k)))
            else:
                left = blocks[block_number][start_bit:]
                right = blocks[block_number + 1][:num_output_bits-(BS_BITS - start_bit)]
                results.append((left + right + extra_data, BitArray(uint=L, length=self.k)))
                block_number += 1
            start_bit = (start_bit + num_output_bits) % BS_BITS
        return results


class FxCalculator():
    def __init__(self, k, table_index, key):
        self.k = k  # k is the plot size parameter

        # length is the size of L and R
        self.length = vector_lens[table_index] * k

        # key per table
        self.key = bytes([table_index]) + key[:15]
        self.reload_key()

        # Used for the composition function
        self.table_index = table_index

    def encrypt(self, input_bits):
        assert(len(input_bits) == BS_BITS)
        return BitArray(aes.encrypt128(input_bits.bytes))

    def reload_key(self):
        aes.load_key(self.key, 16)

    # f functions for f != f1.
    # Takes two BitArrays, each of length self.length. The max value for
    # self.length is 256. This implements the custom block mode with
    # caching. The final outside encryption e is done at the end.
    def f(self, L, R):
        assert(len(L) == len(R) and len(L) == self.length)
        if self.length * 2 <= BS_BITS:
            # Fits in 1 block
            # e(L, R)
            v = pad(L + R, BS_BITS)
        elif self.length * 2 <= 2 * BS_BITS:
            # Fits in 2 blocks
            # e(e(L) ^ R))
            L2 = pad(L.copy(), BS_BITS)
            R2 = pad(R.copy(), BS_BITS)
            v = self.encrypt(L2) ^ R2
        elif self.length * 2 <= 3 * BS_BITS:
            # Fits in 3 blocks
            # e(e(La) ^ e(Ra) ^ e(Lb, Rb))
            v = (self.encrypt(L[:BS_BITS]) ^ self.encrypt(R[:BS_BITS]) ^
                 self.encrypt(pad(L[BS_BITS:] + R[BS_BITS:], BS_BITS)))
        else:
            assert(self.length * 2 <= 4 * BS_BITS)
            # Fits in 4 blocks
            # e(e(e(La) ^ Lb) ^ e(Ra) ^ Rb)
            t1 = self.encrypt(self.encrypt(L[:BS_BITS]) ^ pad(L[BS_BITS:],
                                                              BS_BITS))
            t2 = self.encrypt(R[:BS_BITS])
            t3 = pad(R[BS_BITS:], BS_BITS)
            v = t1 ^ t2 ^ t3
        return self.encrypt(v)[:self.k + EXTRA_BITS]  # e(v) and truncate to first k bits

    # Composes two metadatas into one, depending on which table we're at
    def compose(self, L, R):
        if self.table_index == 2 or self.table_index == 3:
            return L + R
        elif self.table_index == 4:
            return L ^ R
        elif self.table_index == 5:
            assert self.length % 4 == 0
            return (L ^ R)[:int(self.length*(3/4))]
        elif self.table_index == 6:
            assert self.length % 3 == 0
            return (L ^ R)[:int(self.length*(2/3))]
        else:
            return BitArray()

    # Finds matches between two adjacent buckets. Assumes elements in both buckets
    # sorted by y. Returns indeces of matches.
    def find_matches(self, bucket_l, bucket_r, k):
        matches = []
        if not len(bucket_l) or not len(bucket_r):
            return matches

        R_bids = [[] for _ in range(C_param)]
        R_positions = [[] for _ in range(C_param)]

        parity = (bucket_l[0].uint // BC_param) % 2
        for pos_R, y2 in enumerate(bucket_r):
            R_bids[y2.uint % C_param].append((y2.uint % BC_param) // C_param)
            R_positions[y2.uint % C_param].append(pos_R)

        for pos_L, y1 in enumerate(bucket_l):
            yl_bid = (y1.uint % BC_param) // C_param
            yl_cid = y1.uint % C_param

            for m in range(EXTRA_BITS_POW):
                target_bid = yl_bid + m
                target_cid = yl_cid + matching_shifts_c[parity][m]

                if target_bid >= B_param:
                    target_bid -= B_param
                if target_cid >= C_param:
                    target_cid -= C_param
                for i in range(len(R_bids[target_cid])):
                    R_bid = R_bids[target_cid][i]
                    if target_bid == R_bid:
                        yl_bucket = bucket_l[pos_L].uint // BC_param
                        if yl_bucket + 1 == bucket_r[R_positions[target_cid][i]].uint // BC_param:
                            matches.append((pos_L, R_positions[target_cid][i]))
        return matches
