import pandas as pd
import os

input_file = "your_file.csv"
rows_per_file = 2000
output_dir = "output_parts"

def split_csv(file_path, rows_per_file=2000, output_dir="output_parts"):
    os.makedirs(output_dir, exist_ok=True)
    chunk_iter = pd.read_csv(file_path, chunksize=rows_per_file)

    for i, chunk in enumerate(chunk_iter, start=1):
        output_file = os.path.join(output_dir, f"part_{i}.csv")
        chunk.to_csv(output_file, index=False, header=True)
        print(f"Saved {output_file}")

if __name__ == "__main__":
    split_csv(input_file, rows_per_file, output_dir)
