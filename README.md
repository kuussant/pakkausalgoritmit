# Pakkausalgoritmit
Algoritmit ja Tekoäly Harjoitustyö, 2026 (heinä-elokuu)
<br>
[Määrittelydokumentti](https://github.com/kuussant/pakkausalgoritmit/blob/main/dokumentaatio/m%C3%A4%C3%A4rittelydokumentti.md)
<br>
[Viikkoraportit](https://github.com/kuussant/pakkausalgoritmit/tree/main/dokumentaatio/viikkoraportit)
<br>
[Toteutusdokumentti](https://github.com/kuussant/pakkausalgoritmit/blob/main/dokumentaatio/toteutusdokumentti.md)
<br>
[Testausdokumentti](https://github.com/kuussant/pakkausalgoritmit/blob/main/dokumentaatio/testausdokumentti.md)

### Projektin käyttöönotto

Lataa projektin vaatimukset projektin juurihakemistossa:

`poetry install`

### Huffman ja LZ78 käyttöohje

#### Ohjelman käynnistys
`poetry run {huffman, lz78} {1, 2} syötetiedosto tulostiedosto`

1 = pakkaa tiedosto
<br>
2 = pura tiedosto
<br>

#### Pakkaaminen
**syötetiedosto**: mikä tahansa tiedosto
<br>
**tulostiedosto**: mikä tahansa tiedostonimi
<br>

#### Purkaminen
**syötetiedosto**: pakattu tiedosto
<br>
**tulostiedosto**: tiedostonimi alkuperäisellä tiedostopäätteellä

#### Optiot
**-h, --help**: käyttöohje
<br>
**-s, --stats** (vain pakattaessa): statistiikka

#### Esimerkki
`poetry run lz78 1 tiedosto.txt tulos.bin --stats`

`poetry run lz78 2 tulos.bin purettu.txt`

### Testit
`poetry run pytest`
