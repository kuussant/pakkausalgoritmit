## LZ78

LZ78-toteutus jakautuu kolmeen osaan: 

1. Tokenien tietorakenne

`class TokenDictionary()`

2. Pakkaaminen

`def encode_file(in_file, out_file)`

5. Purkaminen

`def decode_file()`

### Saavutetut aika- ja tilavaativuudet
Tavoitteena oli O(n) aikavaativuus, mutta lopputulokseksi tuli noin O(n log n).

Yksi ongelmista on esimerkiksi tämä osa koodia:

<img width="594" height="38" alt="image" src="https://github.com/user-attachments/assets/74328488-64c5-4f36-ac26-e9aab61e362e" />

<br>
<br>
Bittien käsittely merkkijonoina ei välttämättä ole tehokkain ratkaisu. format() aikavaativuus on O(n), 
mutta koska indeksien pituudet kasvavat hiljattain, olettaisin tämän maksavan O(log m).

Purkaminen toisaalta vaikuttaisi olevan O(n).

Tilavaativuudet molemmat O(n).

## Huffman koodaus

Huffman-toteutus jakautuu viiteen osaan:

1. Huffman-puun muodostava solmu

`class HuffmanTreeNode()`

2. Funktio joka rakentaa Huffman-puun

`def build_tree(freqs_list)`

3. Funktio joka kulkee Huffman-puun läpi ja antaa kaikille symboleille Huffman-koodin

`def traverse(root)`

4. Pakkaaminen
`def encode_file(in_file, out_file)`

5. Purkaminen
`def decode_file(in_file, out_file)`

### Saavutetut aika- ja tilavaativuudet
Huffman-puun luonnin tavoite: aika O(n log n), tila O(n)
Tavoite pakkaaminen: aika O(n), tila O(1)
Tavoite purkaminen: aika O(n), tila O(1)

Puun luonti vie noin O(m log m) aikaa.

Pakkaaminen saattaa viedä enemmän taas merkkijono-operaatioiden takia:

<img width="279" height="42" alt="image" src="https://github.com/user-attachments/assets/b3dfc3d1-bd80-4d45-aeee-004814a75706" />

Jolloin haluttua O(n) aikaa ei voi saavuttaa.

Purkaminen näyttäisi olevan O(n).

## Puutteet
Puutteita on paljon, molemmissa algoritmeissa varsinkin tavujen käsittely merkkijonoina vaikuttaa algoritmien tehokkuuteen. 
Tietorakenteet ja/tai niiden käsittely ei ole tehty parhaalla mahdollisella tavalla myöskään. Mutta oletan, 
että nopeus ei ole keskeinen aihe näissä kahdessa algoritmissa.

## Lähteet
Nämä olivat pääasialliset lähteet:

[Wikipedia](https://fi.wikipedia.org/wiki/Wikipedia:Etusivu)
<br>
[Data Compression, The complete reference](https://archive.org/details/pdfy-Ezz1QE-FRYsgeVKU/mode/2up)

## Laajojen kielimallien käyttö
- ChatGPT
- Pythonin syntaksiin liittyvät asiat ja kysymyksiä liittyen molempiin algoritmeihin (ilman koodia)
