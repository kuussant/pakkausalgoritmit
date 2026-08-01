import heapq
from itertools import count

DIR_PATH = ""
FILE_BUFFER = 1024

class HuffmanTreeNode():
    def __init__(self, symbol = None):
        self.symbol = symbol
        self.freq = None
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


# rakentaa huffman-puun ja palauttaa juuren
def build_tree(freqs_list: list[tuple[str, int]]) -> HuffmanTreeNode:
    pq = []
    counter = count() # laskuri, joka erottaa toisistaan esiintymät, joilla on sama todennäköisyys

    for freq in freqs_list:
        node = HuffmanTreeNode(freq[0])
        node.freq = freq[1]
        heapq.heappush(pq, (node.freq, next(counter), node)) # prioriteettijono auttaa valitsemaan seuraavaksi harvinaisimman merkin

    # yhdistele merkkejä (solmuja) kunnes jäljellä on yksi 
    while len(pq) > 1:
        # vasen solmu
        freq_left, _, node_left = heapq.heappop(pq)

        # oikea solmu
        freq_right, _, node_right = heapq.heappop(pq)

        new_freq = freq_left + freq_right

        new_node = HuffmanTreeNode()
        new_node.left = node_left
        new_node.right = node_right
        new_node.freq = new_freq
        heapq.heappush(pq, (new_node.freq, next(counter), new_node))

    _, _, root = heapq.heappop(pq)

    return root


# kulkee huffman-puun läpi, määrittää jokaiselle lehtisolmulle koodin
def traverse(root: HuffmanTreeNode) -> dict[int, str]:
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


# kulje syötetiedosto uudelleen läpi ja luo pakattu tiedosto
def encode_file(codes: dict[int, str], freqs: list[tuple[str, int]]) -> None:
    byte_len = 8
    current_byte = ''
    overflow_bits = ''
    symbol_count = len(freqs)

    with open(DIR_PATH + "input.txt", "rb") as in_file, open(DIR_PATH + "encoded.bin", "wb") as out_file:
        # headeri
        out_file.write(symbol_count.to_bytes(2, byteorder="big"))

        for b, f in freqs:
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
                if len(current_byte) >= byte_len:
                    write_out = current_byte[:8]
                    overflow_bits = current_byte[8:]

                    # muunna merkkijono tavuksi
                    byte = int(write_out, 2)
                    out_file.write(bytes([byte]))

                    current_byte = overflow_bits
                    #print(write_out)

            if overflow_bits != '':
                overflow_bits = overflow_bits + '0' * (byte_len - len(overflow_bits))

                byte = int(overflow_bits, 2)
                out_file.write(bytes([byte]))


def test_read() -> None:
    freqs_tuples = []
    file_size = 0

    with open(DIR_PATH + "encoded.bin", "rb") as bin, open(DIR_PATH  + "decoded.txt", "w") as out:
        # lue headeri
        data = bin.read(2)
        symbol_count = int.from_bytes(data, byteorder="big")
        print("Unique symbols", symbol_count)

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
                    out.write(chr(next_symbol))
                        
                    next_node = root
                    symbol_count += 1


def main():
    # valmis taulukko jokaista merkkiä kohden
    freqs = [0] * 256

    with open(DIR_PATH + "input.txt", "rb") as f:
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

    encode_file(codes, freqs_tuples)
    test_read()

main()
