import pdfplumber
import pandas as pd
from typing import List, Dict

def extract_tables_from_pdf(pdf_path: str, merge_spanning_tables: bool = True):
    """
    Extract tables from PDF, handling tables that span multiple pages.
    
    Args:
        pdf_path: Path to the PDF file
        merge_spanning_tables: Whether to attempt merging tables across pages
    
    Returns:
        List of DataFrames containing the extracted tables
    """
    all_tables = []
    
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Processing {len(pdf.pages)} pages...")
        
        for page_num, page in enumerate(pdf.pages, start=1):
            print(f"Extracting tables from page {page_num}...")
            
            # Extract tables from current page
            tables = page.extract_tables()
            
            for table_num, table in enumerate(tables):
                if table:
                    # Convert to DataFrame
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append({
                        'page': page_num,
                        'table_num': table_num,
                        'data': df
                    })
    
    if merge_spanning_tables and len(all_tables) > 1:
        print("\nAttempting to merge spanning tables...")
        merged_tables = merge_consecutive_tables(all_tables)
        return merged_tables
    
    return [t['data'] for t in all_tables]


def merge_consecutive_tables(tables: List[Dict]) -> List[pd.DataFrame]:
    """
    Merge tables that appear to be continuations across pages.
    Tables are merged if they have the same column structure.
    """
    if not tables:
        return []
    
    merged = []
    current_group = [tables[0]]
    
    for i in range(1, len(tables)):
        prev_table = current_group[-1]['data']
        curr_table = tables[i]['data']
        
        # Check if tables have same columns
        if list(prev_table.columns) == list(curr_table.columns):
            # Check if pages are consecutive
            if tables[i]['page'] - current_group[-1]['page'] <= 1:
                current_group.append(tables[i])
                continue
        
        # Merge current group and start new one
        if len(current_group) > 1:
            merged_df = pd.concat([t['data'] for t in current_group], ignore_index=True)
            print(f"Merged table spanning pages {current_group[0]['page']}-{current_group[-1]['page']}")
            merged.append(merged_df)
        else:
            merged.append(current_group[0]['data'])
        
        current_group = [tables[i]]
    
    # Handle last group
    if len(current_group) > 1:
        merged_df = pd.concat([t['data'] for t in current_group], ignore_index=True)
        print(f"Merged table spanning pages {current_group[0]['page']}-{current_group[-1]['page']}")
        merged.append(merged_df)
    else:
        merged.append(current_group[0]['data'])
    
    return merged


def extract_with_custom_settings(pdf_path: str):
    """
    Extract tables with custom table detection settings for better accuracy.
    """
    all_tables = []
    
    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "intersection_tolerance": 3,
    }
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables(table_settings=table_settings)
            
            for table in tables:
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    all_tables.append(df)
    
    return all_tables


# Example usage
if __name__ == "__main__":
    pdf_file = "Email_Statement_unlocked-1-20.pdf"
    
    # Method 1: Basic extraction with auto-merge
    print("Method 1: Basic extraction with auto-merge")
    tables = extract_tables_from_pdf(pdf_file, merge_spanning_tables=True)
    
    for i, table in enumerate(tables, start=1):
        print(f"\nTable {i}:")
        print(table.head())
        print(f"Shape: {table.shape}")
        
        # Save to CSV
        table.to_csv(f"table_{i}.csv", index=False)
    
    print("\n" + "="*50 + "\n")
    
    # Method 2: Custom settings
    print("Method 2: Custom table detection settings")
    custom_tables = extract_with_custom_settings(pdf_file)
    
    for i, table in enumerate(custom_tables, start=1):
        print(f"\nTable {i}: {table.shape}")
        print(table.head())