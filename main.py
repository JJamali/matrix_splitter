import numpy as np

def parse_file(filename): # I believe this is working well
    with open(filename, 'r') as file:
        lines = file.readlines()

    matrices = []
    current_matrix = {}

    for line in lines:
        # Skip empty lines or lines that don't contain the expected structure
        line = line.strip()
        if not line:
            continue
        
        # Debug: print each line as you process it
        print(f"Processing line: {line}")

        # Try to extract 'Num:' information
        if 'Num:' in line:
            try:
                current_matrix['Num'] = int(line.split(':')[1].strip())
            except IndexError:
                print(f"Error parsing line: {line}")
                continue
        elif 'H11:' in line:
            try:
                current_matrix['H11'] = float(line.split(':')[1].strip())
            except IndexError:
                print(f"Error parsing line: {line}")
                continue
        
        # Process rows enclosed in curly braces
        elif line.startswith('{') and line.endswith('}'):
            matrix_row = line[1:-1].strip()  # Remove curly braces
            current_matrix['matrix_rows'] = matrix_row
        
        # Handle end of matrix (if needed)
        # For example, when you encounter a new 'Num:' line or the end of the file:
        if 'Num:' in line or line == lines[-1]:
            matrices.append(current_matrix)
            current_matrix = {}

    return matrices

def split_matrix(matrix): # Might need some work
    """Split the matrix according to the given rule."""
    X = matrix[:, :-1]
    M = matrix[:, -1]
    a = np.sum(M)
    return X, M, a

def are_matrices_identical(matrix1, matrix2):
    """Check if two matrices are identical under row and column swaps."""
    return (np.array_equal(np.sort(matrix1, axis=0), np.sort(matrix2, axis=0)) and
            np.array_equal(np.sort(matrix1, axis=1), np.sort(matrix2, axis=1)))

def process_matrices(matrices):
    """Process matrices, split them and find unique results."""
    split_results = []
    for mat in matrices:
        # Apply splitting rule
        X, M, a = split_matrix(mat['Matrix'])
        # Create the new matrix from the split
        split_matrix = np.hstack([X, M.reshape(-1, 1)])
        split_matrix = np.append(split_matrix, [[a]], axis=1)
        
        # Check if this split matrix already exists (considering row and column swaps)
        is_duplicate = False
        for res in split_results:
            if are_matrices_identical(res['Matrix'], split_matrix):
                is_duplicate = True
                break
        
        if not is_duplicate:
            split_results.append({
                'Num': mat['Num'],
                'H11': mat['H11'],
                'Matrix': split_matrix
            })
    
    # Sort by H11
    split_results.sort(key=lambda x: x['H11'])
    return split_results

def write_output(results, output_filename):
    """Write the processed matrices to the output file."""
    with open(output_filename, 'w') as f:
        for res in results:
            f.write(f"Num    : {res['Num']}\nH11    : {res['H11']}\n")
            f.write("Matrix:\n")
            for row in res['Matrix']:
                f.write("{" + ",".join(map(str, row)) + "}\n")
            f.write("\n")

def main():
    input_filename = 'cicylist.txt'
    output_filename = 'split_results.txt'
    matrices = parse_file(input_filename)
    results = process_matrices(matrices)
    write_output(results, output_filename)
    print(f"Results saved to {output_filename}")

if __name__ == "__main__":
    main()
