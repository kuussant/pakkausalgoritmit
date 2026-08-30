from pathlib import Path
import pytest
from huffman.huffman import encode_file, decode_file, build_tree


def test_empty_list_returns_none():
        root = build_tree([])

        assert root is None


def test_single_symbol():
    root = build_tree([(65, 10)])

    assert root is not None
    assert root.symbol == 65
    assert root.freq == 10
    assert root.left is None
    assert root.right is None


def test_two_symbols():
        root = build_tree([
            (65, 5),
            (66, 10),
        ])

        assert root is not None
        assert root.symbol is None
        assert root.freq == 15

        assert root.left.symbol == 65
        assert root.left.freq == 5

        assert root.right.symbol == 66
        assert root.right.freq == 10


def test_equal_frequencies_do_not_crash():
        freqs = [
            (65, 10),
            (66, 10),
            (67, 10),
            (68, 10),
        ]

        root = build_tree(freqs)

        assert root is not None
        assert root.freq == 40


def test_three_symbols():
    root = build_tree([
        (65, 5),
        (66, 2),
        (67, 1),
    ])

    assert root is not None
    assert root.symbol is None
    assert root.freq == 8

    assert root.left.freq == 3
    assert root.left.symbol is None

    assert root.left.left.symbol == 67
    assert root.left.left.freq == 1

    assert root.left.right.symbol == 66
    assert root.left.right.freq == 2

    assert root.right.symbol == 65
    assert root.right.freq == 5


def test_root_frequency_is_sum_of_all_frequencies():
        freqs = [
            (65, 10),
            (66, 20),
            (67, 30),
            (68, 40),
        ]

        root = build_tree(freqs)

        assert root.freq == 100


def encode_decode(tmp_path: Path, data: bytes):
    in_f = tmp_path / "test_input.bin"
    en_f = tmp_path / "test_encoded.bin"
    de_f = tmp_path / "test_decoded.bin"

    in_f.write_bytes(data)
    encode_file(in_f, en_f)
    decode_file(en_f, de_f)

    return de_f.read_bytes()


def test_big_file(tmp_path: Path):
    tests_dir = Path(__file__).parent
    input_file = tests_dir / "big_file.html"

    encoded_file = tmp_path / "large_test_file.encoded"
    decoded_file = tmp_path / "large_test_file.decoded"

    encode_file(input_file, encoded_file)
    decode_file(encoded_file, decoded_file)

    assert decoded_file.read_bytes() == input_file.read_bytes()


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