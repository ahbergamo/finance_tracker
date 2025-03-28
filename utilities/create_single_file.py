import os


def write_all_files_to_single_file(directory, output_filename):
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                outfile.write(f"\n{'='*80}\n")
                outfile.write(f"File: {os.path.relpath(file_path, directory)}\n")
                outfile.write(f"{'='*80}\n\n")
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"Error reading file: {e}\n")
                outfile.write("\n")
    print(f"All files have been written to {output_filename}")


if __name__ == "__main__":
    directories = [
        "./app",                        # 0
        "./docker",                     # 1
        "./app/templates/budgets",      # 2
        "./app/templates",              # 3
        "./app/templates/reports",      # 4
        "./app/routes/reports",         # 5
        "./app/routes/transactions",    # 6
        "./app/forms",                  # 7
        "./.github/workflows",          # 8
    ]

    current_directory = directories[8]  # Change this index to switch

    output_filename = "combined_files.txt"
    write_all_files_to_single_file(current_directory, output_filename)
