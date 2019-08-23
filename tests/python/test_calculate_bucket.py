import unittest
from bitstring import BitArray
from src.python.calculate_bucket import F1Calculator, FxCalculator, BC_param, EXTRA_BITS


class TestPlot(unittest.TestCase):
    def test_f1(self):
        k = 35
        key = bytes([0, 2, 3, 4, 5, 5, 7, 8, 9, 10, 11, 12, 13,
                     14, 15, 16, 1, 2, 3, 41, 5, 6, 7, 8, 9, 10,
                     11, 12, 13, 11, 15, 16])
        f1 = F1Calculator(k, key)

        L = 525
        result1 = f1.calculate_bucket(BitArray(uint=L, length=k))
        L2 = 526
        result2 = f1.calculate_bucket(BitArray(uint=L2, length=k))
        L3 = 625
        result3 = f1.calculate_bucket(BitArray(uint=L3, length=k))

        results = f1.calculate_buckets(BitArray(uint=L, length=k), 101)
        assert(result1 == results[0])
        assert(result2 == results[1])
        assert(result3 == results[100])

        k = 32
        f1 = F1Calculator(k, key)
        L = 192837491
        result1 = f1.calculate_bucket(BitArray(uint=L, length=k))
        L2 = 192837491 + 1
        result2 = f1.calculate_bucket(BitArray(uint=L2, length=k))
        L3 = 192837491 + 2
        result3 = f1.calculate_bucket(BitArray(uint=L3, length=k))
        L4 = 192837491 + 490
        result4 = f1.calculate_bucket(BitArray(uint=L4, length=k))

        results = f1.calculate_buckets(BitArray(uint=L, length=k), 491)
        assert(result1 == results[0])
        assert(result2 == results[1])
        assert(result3 == results[2])
        assert(result4 == results[490])

    def test_f2(self):
        k = 12
        id = bytes([20, 2, 5, 4, 51, 52, 23, 84, 91, 10, 111, 12, 13,
                    24, 151, 16, 228, 211, 254, 45, 92, 198, 204, 10, 9, 10,
                    11, 129, 139, 171, 15, 18])
        f1 = F1Calculator(k, id)
        x = BitArray(uint=0, length=k)

        buckets = {}
        num_buckets = (2**(k + EXTRA_BITS)) // BC_param + 1
        for _ in range(2**(k-4) + 1):
            for y, L in f1.calculate_buckets(x, 2**4):
                bucket = y.uint // BC_param
                if bucket in buckets:
                    buckets[bucket] += [(y, L)]
                else:
                    buckets[bucket] = [(y, L)]

                if x.uint + 1 > 2**k - 1:
                    break
                x = BitArray(uint=x.uint + 1, length=k)
            if x.uint + 1 > 2**k - 1:
                break

        f2 = FxCalculator(k, 2, id)
        total_matches = 0
        for index, bucket_elements in buckets.items():
            print("Bucket index:", index, len(bucket_elements))
            if index == (num_buckets - 1):
                continue
            bucket_elements = sorted(bucket_elements, key=lambda x: x[0].uint)
            bucket_elements_2 = sorted(buckets[index + 1], key=lambda x: x[0].uint)

            matches = f2.find_matches([x[0] for x in bucket_elements], [x[0] for x in bucket_elements_2], k)

            for offset_L, offset_R in matches:
                print("Match:", bucket_elements[offset_L], bucket_elements_2[offset_R])
                total_matches += 1
        assert(total_matches == 3066)


if __name__ == '__main__':
    unittest.main()
