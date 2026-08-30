import time, argparse, heapq
from pathlib import Path
from itertools import count


FILE_BUFFER = 1024


class HuffmanTreeNode():
    """Huffmanin puun muodostava solmu."""
    def __init__(self, symbol = None):
        """Luo solmun symbolille, alustaa frekvenssin ja vasemman ja oikean lapsen"""
        self.symbol = symbol
        self.freq = None
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def build_tree(freqs_list: list[tuple[int, int]]) -> HuffmanTreeNode:
    """Rakentaa Huffman-puun.
    
    Puu rakennetaan listasta tupleja jotka sisältävät symbolin ja sen frekvenssin.
    Lista käydään läpi symboli kerrallaan ja symbolit prioriteettijonoon.
    Symboleita yhdisellään pienemmät frekvenssit ensin ja poistetaan jonosta, 
    kunnes jäljellä on yksi (Huffmanin puun juuri).

    Args:
        freqs_list: Lista tupleja muotoa (symboli, frekvenssi).

    Returns:
        Puun juuri
    """
    pq = []
    counter = count() # laskuri, joka erottaa toisistaan esiintymät, joilla on sama todennäköisyys

    if freqs_list:
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
    return None


def traverse(root: HuffmanTreeNode) -> dict[int, str]:
    """Kulkee Huffman-puun läpi ja määrittää jokaiselle lehtisolmulle koodin.
    
    Huffman-puu kuljetaan rekursiivisesti juuresta alkaen, ja lapsisolmuille määritetään
    Huffman-koodi.

    Args:
        root: Huffman-puun juuri
    
    Returns:
        Sanakirja jonka avaimina toimii symboli, ja arvoina symbolin Huffman-koodi.
    """
    codes = dict()

    def _traverse(node: HuffmanTreeNode, code: str = ''):
        """Rekursiossa käytetty apufunktio."""
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


def encode_file(in_file: str, out_file: str) -> None:
    """Pakkaa tiedosto Huffmanin koodauksen mukaisesti.
    
    Syötetiedosto luetaan aluksi tavu kerrallaan, ja niiden frekvenssit
    tallennetaan listaan. Listan esiintymät muunnetaan sanakirjaksi, josta
    rakennetaan Huffman-puu. Puusta koostetaan Huffman-koodit jokaiselle symbolille.
    Tulostiedostoon tallennetaan headeri, 
    joka pitää sisällään eri symbolien määrän ja itse symbolit sekä niiden frekvenssit.
    Syötetiedosto käydään toisen kerran läpi tavu kerrallaan, ja esiintymät kirjoitetaan
    Huffman-koodeina tulostiedostoon.

    Args:
        in_file: syötetiedosto
        out_file: pakattu tulostiedosto
    """
    freqs = [0] * 256 # taulukko ascii merkkejä varten
    
    with open(in_file, "rb") as f:
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

    byte_len = 8
    current_byte = ''
    overflow_bits = ''
    symbol_count = len(freqs_tuples)

    # kulje syötetiedosto uudelleen läpi ja luo pakattu tiedosto
    with open(in_file, "rb") as in_file, open(out_file, "wb") as out_file:
        # headeri
        out_file.write(symbol_count.to_bytes(2, byteorder="big"))

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

                    # muunna merkkijono tavuksi
                    byte = int(write_out, 2)
                    out_file.write(bytes([byte]))

                    current_byte = overflow_bits

        # hoida jäämät
        if len(current_byte) > 0:
            current_byte = current_byte + '0' * (byte_len - len(current_byte))

            byte = int(current_byte, 2)
            out_file.write(bytes([byte]))


def decode_file(in_file: str, out_file: str) -> None:
    """Purkaa Huffman-pakatun tiedoston.
    
    Aluksi pakatun syötetiedoston headeristä rakennetaan Huffman-puu, ja luodaan symboleille Huffman-koodit. Symbolien frekvensseistä
    otetaan talteen alkuperäisen tiedoston koko.
    Loput tiedoston datasta luetaan bitti kerrallaan. Kun bittijonosta on saatu koostettua validi Huffman-koodi,
    tätä vastaava symboli kirjoitetaan tulostiedostoon kunnes kaikki tavut on kirjoitettu.
    
    Args:
        in_file: Huffman-pakattu syötetiedosto
        out_file: tulostiedosto
    """
    freqs_tuples = []
    file_size = 0

    with open(in_file, "rb") as bin, open(out_file, "wb") as out:
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

        # jos merkit ovat kaikki identtisiä, kirjoita ne suoraan tiedostoon
        if len(freqs_tuples) == 1:
            symbol, freq = freqs_tuples[0]
            out.write(bytes([symbol]) * freq)
            return
        
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


def compression_stats(input_size, encoded_size, time_elapsed):
    compression_ratio = encoded_size / input_size
    space_saved = 1 - compression_ratio

    print(f"{'Input file size:':<25}{input_size} bytes")
    print(f"{'Encoded file size:':<25}{encoded_size} bytes")
    print(f"{'Compression ratio:':<25}{compression_ratio:.2%}")
    print(f"{'Space saved:':<25}{space_saved:.2%}")
    print(f"{'Time:':<25}{time_elapsed:.4f} s")


def main():
    parser = argparse.ArgumentParser(
        description = "Huffman coding"
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

        encode_file(args.input_file, args.output_file)

        delta = time.perf_counter() - start

        if args.stats:
            input_size = Path(args.input_file).stat().st_size
            encoded_size = Path(args.output_file).stat().st_size

            compression_stats(input_size, encoded_size, delta)
    else:
        decode_file(args.input_file, args.output_file)


if __name__ == "__main__":
    main()
