import sys
import heapq
from itertools import count


FILE_BUFFER = 1024


class HuffmanTreeNode():
    def __init__(self, symbol = None):
        self.symbol = symbol
        self.freq = None
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(freqs_list: list[tuple[str, int]]) -> HuffmanTreeNode:
    pq = []
    counter = count() # laskuri, joka erottaa toisistaan esiintymät, joilla on sama todennäköisyys

    for freq in freqs_list:
        node = HuffmanTreeNode(freq[0])
        node.freq = freq[1]
        heapq.heappush(pq, (node.freq, next(counter), node)) # prioriteettijono auttaa valitsemaan seuraavaksi harvinaisimman merkin

    # yhdistele merkkejä (solmuja) kunnes jäljellä on yksi 
    while len(pq) > 1:
        freq_left, _, node_left = heapq.heappop(pq)

        freq_right, _, node_right = heapq.heappop(pq)

        new_freq = freq_left + freq_right

        new_node = HuffmanTreeNode()
        new_node.left = node_left
        new_node.right = node_right
        new_node.freq = new_freq
        heapq.heappush(pq, (new_node.freq, next(counter), new_node))

    _, _, root = heapq.heappop(pq)

    return root


def traverse(root: HuffmanTreeNode) -> dict[int, str]:
    """Kulkee Huffman-puun läpi ja määrittää jokaiselle lehtisolmulle koodin."""
    codes = dict()

    def _traverse(node: HuffmanTreeNode, code: str = ''):
        if node is None:
            return

        if node.symbol is not None:
            codes[node.symbol] = code
            node.code = code
            return

        _traverse(node.left, code + '0')
        _traverse(node.right, code + '1')

    if root is not None:
        _traverse(root)

    return codes


def encode_file(in_filename: str, out_filename: str) -> None:
    freqs = [0] * 256 # taulukko ascii merkkejä varten
    
    with open(in_filename, "rb") as f:
        while True:
            chunk = f.read(FILE_BUFFER)

            if not chunk:
                break

            # kasvata esiintyvän merkin määrää
            for b in chunk:
                freqs[b] += 1

    # suodata esiintymät
    freqs_tuples = [(i, freq) for i, freq in enumerate(freqs) if freq > 0]

    # rakenna huffman-puu
    root = build_tree(freqs_tuples)

    # määritä huffman-koodit
    codes = traverse(root)

    print(codes)

    byte_len = 8
    current_byte = ''
    overflow_bits = ''
    symbol_count = len(freqs_tuples)

    # kulje syötetiedosto uudelleen läpi ja luo pakattu tiedosto
    with open(in_filename, "rb") as in_file, open(out_filename, "wb") as out_file:
        # headeri
        out_file.write(symbol_count.to_bytes(2, byteorder="big"))

        print(freqs_tuples)
        for b, f in freqs_tuples:
            out_file.write(b.to_bytes(1, byteorder="big"))
            out_file.write(f.to_bytes(4, byteorder="big"))


        # kirjoita data tavuina
        while True:
            chunk = in_file.read(FILE_BUFFER) # lue data lohkoina

            if not chunk:
                break

            for b in chunk:
                current_byte += codes[b]

                # kirjoittaa tavun
                while len(current_byte) >= byte_len:
                    write_out = current_byte[:8]
                    overflow_bits = current_byte[8:]

                    # print(write_out)
                    # print(overflow_bits)
                    # muunna merkkijono tavuksi
                    byte = int(write_out, 2)
                    out_file.write(bytes([byte]))

                    current_byte = overflow_bits
                    #print(write_out)

        # hoida jäämät
        if len(current_byte) > 0:
            current_byte = current_byte + '0' * (byte_len - len(current_byte))

            print(current_byte)
            byte = int(current_byte, 2)
            out_file.write(bytes([byte]))

        # if overflow_bits != '':
        #     overflow_bits = overflow_bits + '0' * (byte_len - len(overflow_bits))

        #     byte = int(overflow_bits, 2)
        #     out_file.write(bytes([byte]))


def decode_file(in_filename: str, out_filename: str) -> None:
    freqs_tuples = []
    file_size = 0

    with open(in_filename, "rb") as bin, open(out_filename, "wb") as out:
        # lue headeri
        data = bin.read(2)
        symbol_count = int.from_bytes(data, byteorder="big")

        for _ in range(symbol_count):
            symbol = int.from_bytes(bin.read(1), byteorder="big")
            freq = int.from_bytes(bin.read(4), byteorder="big")
            freqs_tuples.append((symbol, freq))
            file_size += freq

        # lue data
        root = build_tree(freqs_tuples)
        traverse(root)
        next_node = root

        symbol_count = 0

        while True:
            byte = bin.read(1) # lue tavu

            if not byte:
                break

            val = byte[0]

            # lue tavun bitit ja kulje huffman-puuta pitkin bitti kerrallaan
            for i in range(7, -1, -1):
                if symbol_count >= file_size:
                    break

                bit = (val >> i) & 1

                if bit == 1:
                    next_node = next_node.right
                else:
                    next_node = next_node.left

                next_symbol = next_node.symbol

                # tarkista onko lehtisolmu
                if next_symbol is not None:
                    out.write(bytes([next_symbol]))
                        
                    next_node = root
                    symbol_count += 1


def _usage():
    print("Käyttö: python huffman.py <moodi> <syöte> <tuloste>")
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
