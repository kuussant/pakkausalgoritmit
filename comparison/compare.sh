for i in {1..16}; do
    echo "Algorithm: lz78 file${i}.txt"

    poetry run lz78 1 "comp_test_files/file${i}.txt" "comp_test_files/out" -s
    poetry run lz78 2 "comp_test_files/out" "comp_test_files/out.txt" -s
    
    echo "Algorithm: huffman file${i}.txt"

    poetry run huffman 1 "comp_test_files/file${i}.txt" "comp_test_files/out" -s
    poetry run huffman 2 "comp_test_files/out" "comp_test_files/out.txt" -s
done | tee results.txt

python3 write_csv.py
rm comp_test_files/out comp_test_files/out.txt results.txt