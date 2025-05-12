def remove_subset_columns(table):
    if not table or not table[0]:
        return []
    
    # Extract text values from each cell and transpose the table to work with columns
    text_table = [[cell['text'] for cell in row] for row in table]
    columns = list(zip(*text_table))
    num_columns = len(columns)
    
    # Track which columns to keep
    columns_to_keep = [True] * num_columns
    
    # For each pair of columns, check if one is a subset of the other
    for i in range(num_columns):
        if not columns_to_keep[i]:
            continue  # Skip already removed columns
            
        col_i = columns[i]
        
        for j in range(num_columns):
            if i == j or not columns_to_keep[j]:
                continue  # Skip self-comparison and already removed columns
                
            col_j = columns[j]
            
            # Check if col_i is a subset of col_j
            if is_subset(col_i, col_j):
                columns_to_keep[i] = False
                break  # No need to check further if col_i is already identified as a subset
                
            # Check if col_j is a subset of col_i
            elif is_subset(col_j, col_i):
                columns_to_keep[j] = False
    
    # Create a new table with only the kept columns
    result = []
    for row in table:
        new_row = [row[idx] for idx in range(len(row)) if columns_to_keep[idx]]
        result.append(new_row)
    
    # If all columns were removed, return an empty list
    if not result or not result[0]:
        return []
    
    return result


def is_subset(col1, col2):
    # A column is a subset if all its non-empty values match the other column
    # at the same positions, and the other column has at least one more non-empty value
    
    if col1 == col2:
        return False  # Equal columns are not subsets of each other
    
    col1_non_empty_count = sum(1 for val in col1 if val != '')
    col2_non_empty_count = sum(1 for val in col2 if val != '')
    
    if col1_non_empty_count >= col2_non_empty_count:
        return False  # col1 has more or equal non-empty values, so it can't be a subset
    
    # Check if all non-empty values in col1 match col2 at the same positions
    for val1, val2 in zip(col1, col2):
        if val1 != '' and val1 != val2:
            return False  # Found a non-empty value in col1 that doesn't match col2
    
    return True  # All checks passed, col1 is a subset of col2


# Example usage
if __name__ == "__main__":
    # Sample table (each cell is a dictionary with a 'text' key)
    sample_table = [
        [{'text': 'Name'}, {'text': 'Age'}, {'text': 'Age'}, {'text': 'Position with the Company'}], 
        [{'text': 'Satya Nadella'}, {'text': ''}, {'text': '56'}, {'text': 'Chairman and Chief Executive Officer'}], 
        [{'text': 'Judson B. Althoff'}, {'text': ''}, {'text': '51'}, {'text': 'Executive Vice President and Chief Commercial Officer'}], 
        [{'text': 'Kathleen T. Hogan'}, {'text': ''}, {'text': '58'}, {'text': 'Executive Vice President and Chief Human Resources Officer'}], 
        [{'text': 'Amy E. Hood'}, {'text': ''}, {'text': '52'}, {'text': 'Executive Vice President and Chief Financial Officer'}], 
        [{'text': 'Takeshi Numoto'}, {'text': ''}, {'text': '53'}, {'text': 'Executive Vice President and Chief Marketing Officer'}], 
        [{'text': 'Bradford L. Smith'}, {'text': ''}, {'text': '65'}, {'text': 'Vice Chair and President'}], 
        [{'text': 'Christopher D. Young'}, {'text': ''}, {'text': '52'}, {'text': 'Executive Vice President, Business Development, Strategy, and Ventures'}]
    ]
    
    print("Original table:")
    for row in sample_table:
        print([cell['text'] for cell in row])  # Print text values for readability
    
    result = remove_subset_columns(sample_table)
    
    print("\nTable after removing subset columns:")
    for row in result:
        print([cell['text'] for cell in row])  # Print text values for readability