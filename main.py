import numpy as np
import re

def parse_file(filename): 
    with open(filename, 'r') as file:
        lines = file.readlines()

    matrices = []
    current_matrix = {}
    matrix_rows = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Print to see what each line is
        print(f"Processing line: {line}")

        # Parse matrix metadata
        match = re.match(r'([A-Za-z0-9]+)\s*:\s*(.*)', line)  # Allow spaces around colon
        if match:
            key, value = match.groups()
            key = key.strip()
            value = value.strip()

            if key == 'Num':
                # If there's an existing matrix, save it first
                if current_matrix:
                    current_matrix['matrix_rows'] = matrix_rows  # Assign collected matrix rows
                    matrices.append(current_matrix)
                    matrix_rows = []  # Reset matrix rows for next matrix
                
                # Start a new matrix
                current_matrix = {'Num': int(value)}
            
            elif key == 'H11':
                current_matrix['H11'] = float(value)
            
            elif key == 'C2':
                current_matrix['C2'] = list(map(int, value.strip('{}').split(',')))
            
            elif key == 'Redun':
                current_matrix['Redun'] = list(map(int, value.strip('{}').split(',')))

        elif line.startswith('{') and line.endswith('}'):
            # Parse matrix row inside curly braces
            matrix_row = list(map(int, line[1:-1].strip().split(',')))
            matrix_rows.append(matrix_row)

    # Don't forget to add the last matrix after the loop
    if current_matrix:
        current_matrix['matrix_rows'] = matrix_rows
        matrices.append(current_matrix)

    print(f"Number of matrices parsed: {len(matrices)}")
    return matrices


def split_matrix(matrix): 
    """Split the matrix according to the given rule."""
    matrix_data = np.array(matrix['matrix_rows'])
    X = matrix_data[:, :-1]  # All columns except the last
    M = matrix_data[:, -1]   # Last column
    a = np.sum(M)  # Sum of last column
    return X, M, a

def are_matrices_identical(matrix1, matrix2):
    """Check if two matrices are identical under row and column swaps."""
    return (np.array_equal(np.sort(matrix1, axis=0), np.sort(matrix2, axis=0)) and
            np.array_equal(np.sort(matrix1, axis=1), np.sort(matrix2, axis=1)))

def process_matrices(matrices):
    """Process matrices, split them, and find unique results."""
    split_results = []
    
    for mat in matrices:
        # Apply splitting rule
        X, M, a = split_matrix(mat)
        
        # Create the new matrix from the split
        split_mat = np.hstack([X, M.reshape(-1, 1)])  # Add M as the last column
        split_mat = np.append(split_mat, [[a]], axis=1)  # Add sum a as the last row

        # Check for duplicates based on row/column swaps
        is_duplicate = False
        for res in split_results:
            if are_matrices_identical(res['Matrix'], split_mat):
                is_duplicate = True
                break
        
        if not is_duplicate:
            split_results.append({
                'Num': mat['Num'],
                'H11': mat['H11'],
                'Matrix': split_mat
            })
    
    # Sort results by H11
    split_results.sort(key=lambda x: x['H11'])
    return split_results

def write_output(results, output_filename):
    """Write the processed matrices to the output file."""
    if not results:
        print("No results to write!")
        return
    
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
