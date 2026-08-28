from pathlib import Path
import pytest
from lz78.lz78 import encode_file, decode_file

def encode_decode(tmp_path: Path, data: bytes):
    in_f = tmp_path / "test_input.bin"
    en_f = tmp_path / "test_encoded.bin"
    de_f = tmp_path / "test_decoded.bin"

    in_f.write_bytes(data)
    encode_file(in_f, en_f)
    decode_file(en_f, de_f)

    return de_f.read_bytes()


@pytest.mark.parametrize(
    "data",
    [
        b"",
        b"hello",
        b"world",
        b"A",
        b"AB",
        b"ABB",
        b"ABBA",
        b"ABBAA",
        b"ABCDEFGHIJKLMNOP",
        b"xyzxyzxyzxy",
        b"A"*1000,
        b" ( hello world from lz78 )  ",
    ],
)

def test_encode_decode(tmp_path, data):
    res = encode_decode(tmp_path, data)

    assert res == data


def test_all_byte_values(tmp_path):
    data = bytes(range(256))

    res = encode_decode(tmp_path, data)

    assert res == data


def test_all_byte_values_repeated(tmp_path):
    data = bytes(range(256)) * 100
    
    res = encode_decode(tmp_path, data)

    assert res == data


@pytest.mark.parametrize(
    "size",
    [
        1023,
        1024,
        1025,
        2047,
        2048,
        2049,
        4095,
        4096,
        4097,
    ],
)

def test_file_sizes_around_buffer_boundary(tmp_path, size):
    data_bytes = b"xyz"
    data = data_bytes * (size // len(data_bytes)) + data_bytes[: size % len(data_bytes)]
    res = encode_decode(tmp_path, data)

    assert res == data