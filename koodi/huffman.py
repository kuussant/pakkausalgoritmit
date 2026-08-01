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
        heapq.heappush(pq, (node.freq, next(counter), node))

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


# kulkee huffman-puun läpi, määrittää jokaiselle lehtisolmulle huffman-koodin ja palauttaa koodit
def traverse(root: HuffmanTreeNode) -> dict[int, str]:
    codes = dict()

    def _traverse(node: HuffmanTreeNode, code: str = ''):
        if node is None:
            return

        if node.symbol is not None:
            codes[node.symbol] = code
            return

        _traverse(node.left, code + '0')
        _traverse(node.right, code + '1')

    if root is not None:
        _traverse(root)

    return codes


def encode_file(codes, freqs):
    byte_len = 8
    current_byte = ''
    overflow = ''
    symbol_count = len(freqs)

    with open(DIR_PATH + "input3.txt", "rb") as file, open(DIR_PATH + "output.bin", "wb") as out:
        # header
        out.write(symbol_count.to_bytes(2, byteorder="big"))

        for b, f in freqs:
            out.write(b.to_bytes(1, byteorder="big"))
            out.write(f.to_bytes(4, byteorder="big"))

        # kirjoitaa datan
        while True:
            chunk = file.read(FILE_BUFFER)

            if not chunk:
                break

            for b in chunk:
                current_byte += codes[b]

                # kirjoittaa tavun
                if len(current_byte) >= byte_len:
                    write_out = current_byte[:8]
                    overflow = current_byte[8:]
                    current_byte = overflow

                    print(write_out)

            print(overflow)


def test_read():
    freqs = []
    file_size = 0

    with open(DIR_PATH + "output.bin", "rb") as out:
        # header
        data = out.read(2)
        symbol_count = int.from_bytes(data, byteorder="big")
        print("Unique symbols", symbol_count)

        for _ in range(symbol_count):
            symbol = int.from_bytes(out.read(1), byteorder="big")
            freq = int.from_bytes(out.read(4), byteorder="big")
            freqs.append((symbol, freq))
            file_size += freq

    print("Reconstructed", freqs)


def main():
    freqs = [0] * 256   # valmis taulukko jokaista tavua kohden

    with open(DIR_PATH + "input3.txt", "rb") as f:
        while True:
            chunk = f.read(FILE_BUFFER)

            if not chunk:
                break

            # kasvattaa esiintyvän tavun määrää
            for b in chunk:
                freqs[b] += 1

    # suodattaa esiintymät
    freq_tuples = [(i, freq) for i, freq in enumerate(freqs) if freq > 0]

    # rakentaa huffman-puun
    root = build_tree(freq_tuples)

    # määrittää huffman-koodit
    codes = traverse(root)

    print(codes)

    encode_file(codes, freq_tuples)
    #test_read()

main()
