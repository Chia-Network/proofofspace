/*
<%
setup_pybind11(cfg)
cfg['compiler_args'] = ['-g', '-O3', '-Wall', '-msse2',  '-msse', '-march=native',  '-std=c++11', '-maes']
%>
*/
// Copyright 2018 Chia Network Inc

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Some code is taken from pycrypto: https://github.com/dlitz/pycrypto/blob/master/src/AESNI.c
// License below.
/*
 *  AESNI.c: AES using AES-NI instructions
 *
 * Written in 2013 by Sebastian Ramacher <sebastian@ramacher.at>
 *
 * ===================================================================
 * The contents of this file are dedicated to the public domain.  To
 * the extent that dedication to the public domain is not available,
 * everyone is granted a worldwide, perpetual, royalty-free,
 * non-exclusive license to exercise all rights associated with the
 * contents of this file for any purpose whatsoever.
 * No rights are reserved.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 * ===================================================================
 */

#ifndef SRC_CPP_AES_HPP_
#define SRC_CPP_AES_HPP_

#include <pybind11/pybind11.h>


namespace py = pybind11;

#ifdef WIN32

#include <windows.h>
double get_time() {
    LARGE_INTEGER t, f;
    QueryPerformanceCounter(&t);
    QueryPerformanceFrequency(&f);
    return static_cast<double>(t.QuadPart) / static_cast<double>(f.QuadPart);
}

#else

#include <sys/time.h>
#include <sys/resource.h>
#include <map>
#include <unordered_map>

double get_time() {
    struct timeval t;
    struct timezone tzp;
    gettimeofday(&t, &tzp);
    return t.tv_sec + t.tv_usec * 1e-6;
}

#endif

// #include <stdint.h>    //for int8_t
#include <string.h>    // for memcmp
#include <wmmintrin.h>   // for intrinsics for AES-NI
// #include <iostream>
// #include <stdio.h>

#define DO_ENC_BLOCK_256(m, k) \
    do {\
        m = _mm_xor_si128(m, k[ 0]); \
        m = _mm_aesenc_si128(m, k[ 1]); \
        m = _mm_aesenc_si128(m, k[ 2]); \
        m = _mm_aesenc_si128(m, k[ 3]); \
        m = _mm_aesenc_si128(m, k[ 4]); \
        m = _mm_aesenc_si128(m, k[ 5]); \
        m = _mm_aesenc_si128(m, k[ 6]); \
        m = _mm_aesenc_si128(m, k[ 7]); \
        m = _mm_aesenc_si128(m, k[ 8]); \
        m = _mm_aesenc_si128(m, k[ 9]); \
        m = _mm_aesenc_si128(m, k[ 10]);\
        m = _mm_aesenc_si128(m, k[ 11]);\
        m = _mm_aesenc_si128(m, k[ 12]);\
        m = _mm_aesenc_si128(m, k[ 13]);\
        m = _mm_aesenclast_si128(m, k[ 14]);\
    }while(0)

#define DO_ENC_BLOCK_2ROUND(m, k)      \
    do                                 \
    {                                  \
        m = _mm_xor_si128(m, k[0]);    \
        m = _mm_aesenc_si128(m, k[1]); \
        m = _mm_aesenc_si128(m, k[2]); \
    } while (0)

static __m128i key_schedule[20];  // The expanded key

static __m128i aes128_keyexpand(__m128i key) {
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    key = _mm_xor_si128(key, _mm_slli_si128(key, 4));
    return _mm_xor_si128(key, _mm_slli_si128(key, 4));
}

#define KEYEXP128_H(K1, K2, I, S) _mm_xor_si128(aes128_keyexpand(K1), \
        _mm_shuffle_epi32(_mm_aeskeygenassist_si128(K2, I), S))

#define KEYEXP128(K, I) KEYEXP128_H(K, K, I, 0xff)
#define KEYEXP256(K1, K2, I)  KEYEXP128_H(K1, K2, I, 0xff)
#define KEYEXP256_2(K1, K2) KEYEXP128_H(K1, K2, 0x00, 0xaa)

// public API
void aes_load_key(uint8_t *enc_key, int keylen) {
    switch (keylen) {
        case 16: {
            /* 128 bit key setup */
            key_schedule[0] = _mm_loadu_si128((const __m128i*) enc_key);
            key_schedule[1] = KEYEXP128(key_schedule[0], 0x01);
            key_schedule[2] = KEYEXP128(key_schedule[1], 0x02);
            key_schedule[3] = KEYEXP128(key_schedule[2], 0x04);
            key_schedule[4] = KEYEXP128(key_schedule[3], 0x08);
            key_schedule[5] = KEYEXP128(key_schedule[4], 0x10);
            key_schedule[6] = KEYEXP128(key_schedule[5], 0x20);
            key_schedule[7] = KEYEXP128(key_schedule[6], 0x40);
            key_schedule[8] = KEYEXP128(key_schedule[7], 0x80);
            key_schedule[9] = KEYEXP128(key_schedule[8], 0x1B);
            key_schedule[10] = KEYEXP128(key_schedule[9], 0x36);
            break;
        }
        case 32: {
            /* 256 bit key setup */
            key_schedule[0] = _mm_loadu_si128((const __m128i*) enc_key);
            key_schedule[1] = _mm_loadu_si128((const __m128i*) (enc_key+16));
            key_schedule[2] = KEYEXP256(key_schedule[0], key_schedule[1], 0x01);
            key_schedule[3] = KEYEXP256_2(key_schedule[1], key_schedule[2]);
            key_schedule[4] = KEYEXP256(key_schedule[2], key_schedule[3], 0x02);
            key_schedule[5] = KEYEXP256_2(key_schedule[3], key_schedule[4]);
            key_schedule[6] = KEYEXP256(key_schedule[4], key_schedule[5], 0x04);
            key_schedule[7] = KEYEXP256_2(key_schedule[5], key_schedule[6]);
            key_schedule[8] = KEYEXP256(key_schedule[6], key_schedule[7], 0x08);
            key_schedule[9] = KEYEXP256_2(key_schedule[7], key_schedule[8]);
            key_schedule[10] = KEYEXP256(key_schedule[8], key_schedule[9], 0x10);
            key_schedule[11] = KEYEXP256_2(key_schedule[9], key_schedule[10]);
            key_schedule[12] = KEYEXP256(key_schedule[10], key_schedule[11], 0x20);
            key_schedule[13] = KEYEXP256_2(key_schedule[11], key_schedule[12]);
            key_schedule[14] = KEYEXP256(key_schedule[12], key_schedule[13], 0x40);
            break;
        }
    }
}

char ciphertext_bytes_16[16];

PYBIND11_MODULE(aes, m) {
    m.def("load_key", [](const char* key, int num_bytes) {  // Accepts str or bytes from Python
        aes_load_key((uint8_t*)key, num_bytes);
    });

    m.def("encrypt256", [](const char* plaintext) {  // Accepts str or bytes from Python
        __m128i m = _mm_loadu_si128(reinterpret_cast<const __m128i *>(plaintext));
        DO_ENC_BLOCK_256(m, key_schedule);
        _mm_storeu_si128(reinterpret_cast<__m128i *>(ciphertext_bytes_16), m);
        return py::bytes(ciphertext_bytes_16, 16);
    });

    m.def("encrypt128", [](const char* plaintext) {  // Accepts str or bytes from Python
        __m128i m = _mm_loadu_si128(reinterpret_cast<const __m128i *>(plaintext));

        // Uses the 2 round encryption innstead of the full 10 round encryption
        DO_ENC_BLOCK_2ROUND(m, key_schedule);

        _mm_storeu_si128(reinterpret_cast<__m128i *>(ciphertext_bytes_16), m);
        return py::bytes(ciphertext_bytes_16, 16);
    });
}

#endif  // SRC_CPP_AES_HPP_
