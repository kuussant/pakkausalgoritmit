import sys

FILE_BUFFER = 1024


def encode_file(in_file, out_file):
    tokens = [(0, 0)]
    token_indexes = {(0, 0): 0}
    next_index = 1
    last_index = 0

    with open(in_file, "rb") as i_f, open(out_file, "wb") as o_f:
        while True:
            chunk = i_f.read(FILE_BUFFER)

            if not chunk:
                break

            for b in chunk:
                token = (last_index, b)
                index = token_indexes.get(token)

                if index is not None:
                    last_index = index
                else:
                    tokens.append(token)
                    token_indexes[token] = next_index
                    o_f.write(token[0].to_bytes(4, byteorder="big"))
                    o_f.write(token[1].to_bytes(1, byteorder="big"))
                    next_index += 1
                    last_index = 0

        o_f.write(last_index.to_bytes(4, byteorder="big"))


def decode_file(in_file, out_file):
    tokens = [(0, b"")]

    with open(in_file, "rb") as i_f, open(out_file, "wb") as o_f:
        while True:
            index_bytes = i_f.read(4)

            if not index_bytes:
                break

            index = int.from_bytes(index_bytes, byteorder="big")
            symbol = i_f.read(1)

            tokens.append((index, symbol))

            write = symbol
            occurs = []

            while True:
                occurs.append(write)

                if index > 0:
                    index, write = tokens[index]
                else:
                    break

            occurs.reverse()

            for byte in occurs:
                o_f.write(byte)


def _usage():
    print("Käyttö: python3 lz78.py <moodi> <syöte> <tuloste>")
    print("Moodit: 1 (pakkaa syötetiedosto), 2 (pura syötetiedosto)")


def main():
    if len(sys.argv) < 4:
        _usage()
        sys.exit(1)
    else:
        mode = sys.argv[1]
        in_filename = sys.argv[2]
        out_filename = sys.argv[3]

        if mode == "1":
            print("encoding")
            encode_file(in_filename, out_filename)
            return
        elif mode == "2":
            print("decoding")
            decode_file(in_filename, out_filename)
        else:
            _usage()
            sys.exit(1)


if __name__ == "__main__":
    main()