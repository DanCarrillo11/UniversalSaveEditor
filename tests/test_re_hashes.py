"""CityHash fingerprints from Google's MIT-licensed city-test.cc.

Copyright (c) 2011 Google, Inc. Full notice: THIRD_PARTY_NOTICES.txt.
"""
import unittest
from re_hashes import city64,murmur32,MASK64


class HashTests(unittest.TestCase):
    def test_cityhash_google_vectors_at_all_length_boundaries(self):
        data=bytearray(1<<20);a=9;b=777;k0=0xc3a5c85c97cb3127
        for i in range(len(data)):
            a=(a+b)&MASK64;b=(b+a)&MASK64
            a=((a^(a>>41))*k0)&MASK64;b=((b^(b>>41))*k0+i)&MASK64
            data[i]=(b>>37)&255
        expected={0:0x9ae16a3b2f90404f,1:0x541150e87f415e96,3:0xef923a7a1af78eab,
                  4:0x11df592596f41d88,7:0x1b5a063fb4c7f9f1,8:0xa0f10149a0e538d6,
                  16:0x03ead5f21d344056,17:0x6abbfde37ee03b5b,32:0x0782fa1b08b475e7,
                  33:0xc5dc19b876d37a80,64:0xe88419922b87176f,65:0x105191e0ec8f7f60,
                  127:0xcbaa3cb8f64f54e0,128:0xb2e23e8116c2ba9f,
                  255:0x915263c671b28809,298:0x74c0b8a6821faafe}
        for length,target in expected.items():
            self.assertEqual(city64(data[length*length:length*length+length]),target,length)
        self.assertEqual(city64(data),0x5fb5e48ac7b7fa4f)

    def test_murmur3_reference_vectors_with_explicit_seed(self):
        self.assertEqual(murmur32(b'',0),0)
        self.assertEqual(murmur32(b'foo',0),0xf6a5c420)
        self.assertEqual(murmur32(b'hello',0),0x248bfa47)
        self.assertEqual(murmur32(b'foo',42),0xb12f489e)


if __name__=='__main__':unittest.main()
