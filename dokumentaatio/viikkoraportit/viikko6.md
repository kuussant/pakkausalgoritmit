Tuntimäärä: 8

Korjasin bugin Huffmanissa, joka aiheutti sen, että viimeistä tavua ei kirjoitettu purettuun tiedostoon. Lisäksi, muutin koodia siten, että pakkaaminen ja purkaaminen toimii nyt kaikentyyppisillä tiedostoilla.

Opiskelin LZ78:aa, ja aloitin siitä ensimmäisen implementaation. Tällä hetkellä pakkaamisella on käänteinen efekti, koska tokenien indeksi kirjoitetaan aina neljään tavuun, jolloin erityisesti pieniä tiedostoja (~4 kB) pakattaessa, "pakattu" tiedosto on _huomattavasti_ alkuperäistä suurempi.

Etsin seuraavaksi tavan esittää indeksit pienemmässä muodossa.
