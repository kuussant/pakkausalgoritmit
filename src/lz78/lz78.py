import time, argparse
from typing import BinaryIO
from pathlib import Path


FILE_BUFFER = 1024
BYTE_BITS = 8


def encode_file(in_file, out_file):
    tokens = [(0, b"")]
    token_indexes = {(0, b""): 0}
    next_index = 1
    last_index = 0
    token_count = 0
    byte_buff = ""

    with open(in_file, "rb") as input, open(out_file, "wb") as output:
        while True:
            chunk = input.read(FILE_BUFFER)

            if not chunk:
                break

            for b in chunk:
                token = (last_index, b)
                index = token_indexes.get(token)

                if index is not None:
                    last_index = index
                else:
                    # 1. Count current entries, determine the number of bits to represent previous indices
                    # for the next entry.
                    # 2. construct bit string for the next index, limit to max bits needed, concat symbol
                    # 3. write byte to file, buffer carry over bits for next entry
                    tokens.append(token)
                    token_indexes[token] = next_index
                    next_index += 1
                    last_index = 0

                    index_bits = format(token[0], f"0{max(token_count.bit_length(), 1)}b")
                    symbol_bits = format(token[1], "08b")
                    
                    byte_buff += index_bits + symbol_bits
                    token_count += 1

                    while len(byte_buff) >= BYTE_BITS:
                        output.write(bytes([int(byte_buff[:BYTE_BITS], 2)]))
                        byte_buff = byte_buff[BYTE_BITS:]

        byte_buff += format(last_index, f"0{token_count.bit_length()}b")

        tokens_len = len(tokens)

        if byte_buff:
            tokens_len += 1

            # write the rest of full bytes from buffer
            while len(byte_buff) >= BYTE_BITS:
                output.write(bytes([int(byte_buff[:BYTE_BITS], 2)]))
                byte_buff = byte_buff[BYTE_BITS:]

            # write padding to remaining bits in buffer
            if byte_buff:
                padding = '0' * (BYTE_BITS - len(byte_buff))
                byte_buff += padding
                output.write(bytes([int(byte_buff, 2)]))

        return tokens_len


def decode_file(in_file, out_file):
    tokens = [(0, b"")]
    buffer = 0
    cur_buff_bit = 0
    index = 0
    symbol = 0
    index_bits_to_read = 1
    symbol_bits_to_read = 8

    def read_bits(n: int, cur_buff_bit: int) -> tuple[int, int]:
        res = (buffer >> (cur_buff_bit - n)) & ((1 << n) - 1)
        cur_buff_bit -= n

        return res, cur_buff_bit

    def write_token_to_file(token: tuple[int, int], file: BinaryIO) -> None:
        occurs = []
        
        while token != tokens[0]:
            occurs.append(token[1])
            token = tokens[token[0]]

        for b in reversed(occurs):
            file.write(bytes([b]))

    with open(in_file, "rb") as input, open(out_file, "wb") as output:         
        while True:
            byte = input.read(1)

            if not byte:
                break

            # make space for new byte in buffer
            buffer = (buffer << BYTE_BITS) + byte[0]
            cur_buff_bit += BYTE_BITS

            if index_bits_to_read + symbol_bits_to_read > cur_buff_bit:
                continue

            index, cur_buff_bit = read_bits(index_bits_to_read, cur_buff_bit)
            symbol, cur_buff_bit = read_bits(symbol_bits_to_read, cur_buff_bit)

            index_bits_to_read = max(len(tokens).bit_length(), 1)

            token = (index, symbol)
            tokens.append(token)

            write_token_to_file(token, output)

            # flush buffer to 8 bits
            if cur_buff_bit <= BYTE_BITS:
                buffer = buffer & ((1 << BYTE_BITS) - 1)

        last_index, _ = read_bits(index_bits_to_read, cur_buff_bit)
        token = tokens[last_index]
        write_token_to_file(token, output)

        return output


def compression_stats(input_size, encoded_size, token_count, time_elapsed):
    compression_ratio = encoded_size / input_size
    space_saved = 1 - compression_ratio
    avg_token_size = encoded_size / token_count

    print(f"{'Input file size:':<25}{input_size} bytes")
    print(f"{'Encoded file size:':<25}{encoded_size} bytes")
    print(f"{'Compression ratio:':<25}{compression_ratio:.2%}")
    print(f"{'Space saved:':<25}{space_saved:.2%}")
    print(f"{'Token count:':<25}{token_count}")
    print(f"{'Time:':<25}{time_elapsed:.4f} s")


def main():
    parser = argparse.ArgumentParser(
        description = "LZ78 codec"
    )

    parser.add_argument(
        "mode",
        choices = ["1", "2"],
        help = "1 = encode file, 2 = decode file"
    )

    parser.add_argument("input_file", help="encoding: any file, decoding: encoded file")
    parser.add_argument("output_file", help="encoding: any filename, decoding: a filename with the original file extension")

    parser.add_argument("-s", "--stats", action="store_true", help="show compression stats")
    args = parser.parse_args()

    if args.mode == "1":
        start = time.perf_counter()

        token_count = encode_file(args.input_file, args.output_file)

        delta = time.perf_counter() - start

        if args.stats:
            input_size = Path(args.input_file).stat().st_size
            encoded_size = Path(args.output_file).stat().st_size

            compression_stats(input_size, encoded_size, token_count, delta)
    else:
        decode_file(args.input_file, args.output_file)


if __name__ == "__main__":
    main()