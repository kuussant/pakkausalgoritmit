import csv
from copy import deepcopy

with open('results.txt', 'r') as txt_f, open('comparison.csv', 'w', newline='') as csv_f:
    rows = []

    row = {
        "algorithm": "",
        "file": "",
        "input_size": "",
        "encoded_size": "",
        "compression_ratio": "",
        "space_saved": "",
        "compression_time": "",
        "decompression_time": "",
    }

    new_row = deepcopy(row)

    for line in txt_f:
        line = line.strip()
        words = line.split()

        match words[0]:
            case "Algorithm:":
                new_row["algorithm"] = words[1]
                new_row["file"] = words[2]
            case "Input":
                new_row["input_size"] = words[3] + " B"
            case "Encoded":
                new_row["encoded_size"] = words[3] + " B"
            case "Compression":
                new_row["compression_ratio"] = words[2]
            case "Space":
                new_row["space_saved"] = words[2]
            case "Time:":
                new_row["compression_time"] = words[1] + " s"
            case "Decompression":
                new_row["decompression_time"] = words[2] + " s"
                rows.append(new_row)
                new_row = deepcopy(row)
            case _:
                pass

    fieldnames = [
        "algorithm",
        "file",
        "input_size",
        "encoded_size",
        "compression_ratio",
        "space_saved",
        "compression_time",
        "decompression_time",
    ]

    writer = csv.DictWriter(csv_f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
