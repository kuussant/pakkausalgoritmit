def decode_file(in_file, out_file):
    MASK_8_BIT = 255
    tokens = [(0, b"")]
    token_count = 1
    index = 0
    symbol = 0
    index_bits_left = 1
    symbol_bits_left = 0
    bits_left = 8

    test_count = 40

    with open(in_file, "rb") as i_f, open(out_file, "wb") as o_f:
        while True:
            byte = i_f.read(1)

            if not byte:
                break

            byte = byte[0]
            bits_left = 8

            while bits_left > 0:
                if symbol_bits_left > 0:
                    if bits_left == 8:
                        # leading or tailing symbol bits
                        bits_left -= symbol_bits_left
                        symbol += byte >> bits_left
                        symbol_bits_left = 0
                        print(index, symbol)
                        token = (index, symbol)
                        tokens.append(token)
                        
                        write = symbol
                        occurs = []

                        while True:
                            occurs.append(write)

                            if index > 0:
                                index, write = tokens[index]
                            else:
                                break

                        occurs.reverse()

                        for b in occurs:
                            o_f.write(bytes([b]))

                        index_bits_left = max(token_count.bit_length(), 1)
                        token_count += 1
                    else:
                        # starting to read new symbol
                        symbol = (byte << (8 - bits_left)) & MASK_8_BIT
                        symbol_bits_left -= bits_left
                        bits_left = 0

                if index_bits_left > 0:
                    if bits_left == 8:
                        # leading index bits
                        if bits_left >= index_bits_left:
                            bits_left -= index_bits_left
                            index += byte >> bits_left
                            index_bits_left = 0
                        else:
                            index_bits_left -= bits_left
                            index += byte << index_bits_left
                            bits_left = 0
                    else:
                        if bits_left > index_bits_left:
                            # index bits in the middle
                            index = (byte >> (bits_left - index_bits_left)) & ((1 << index_bits_left) - 1)
                            bits_left -= index_bits_left
                            index_bits_left = 0
                        else:
                            # index bits tail end
                            index_bits_left -= bits_left
                            index = (byte & ((1 << bits_left) - 1)) << index_bits_left
                            bits_left = 0

                    if index_bits_left == 0:
                        symbol_bits_left = 8

            test_count -= 1
            # token_count += 1
        print(tokens)