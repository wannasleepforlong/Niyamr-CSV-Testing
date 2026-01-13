import pandas as pd
import numpy as np
import re
from datetime import datetime

def clean_csv(input_file, output_file="fixed.csv"):
    """
    Automatically detect and fix common CSV issues
    
    Args:
        input_file (str): Path to input CSV file
        output_file (str): Path to save cleaned CSV
    
    Returns:
        pd.DataFrame: Cleaned dataframe
    """
    print(f"Reading {input_file}...")
    df = pd.read_csv(input_file)
    print(f"Original shape: {df.shape}")
    print(f"Original dtypes:\n{df.dtypes}\n")
    
    # 1. Clean column names
    df = standardize_column_names(df)
    
    # 2. Remove duplicate rows
    df = remove_duplicates(df)
    
    # 3. Fix whitespace in text columns
    df = fix_whitespace(df)
    
    # 4. Detect and fix numeric columns stored as strings
    df = fix_numeric_columns(df)
    
    # 5. Detect and fix date columns
    df = fix_date_columns(df)
    
    # 6. Fix boolean columns
    df = fix_boolean_columns(df)
    
    # 7. Handle missing values
    df = handle_missing_values(df)
    
    # 8. Remove empty rows/columns
    df = remove_empty_rows_cols(df)
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"\n✓ Cleaned CSV saved to: {output_file}")
    print(f"Final shape: {df.shape}")
    print(f"Final dtypes:\n{df.dtypes}")
    
    return df


def standardize_column_names(df):
    """Clean column names: lowercase, replace spaces with underscores"""
    original = df.columns.tolist()
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('[^a-z0-9_]', '', regex=True)
    )
    print(f"✓ Standardized {len(df.columns)} column names")
    return df


def remove_duplicates(df):
    """Remove duplicate rows"""
    before = len(df)
    df = df.drop_duplicates()
    removed = before - len(df)
    if removed > 0:
        print(f"✓ Removed {removed} duplicate rows")
    return df


def fix_whitespace(df):
    """Remove leading/trailing whitespace from string columns"""
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].replace('nan', np.nan)
            df[col] = df[col].replace('', np.nan)
    print("✓ Cleaned whitespace from text columns")
    return df


def fix_numeric_columns(df):
    """Convert string columns that should be numeric"""
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(100)
            if len(sample) == 0:
                continue
            
            # Check if values look numeric
            numeric_pattern = re.compile(r'^-?[\d,]+\.?\d*%?$|^-?\d*\.?\d+%?$')
            sample_str = sample.astype(str).str.strip()
            numeric_count = sum(1 for x in sample_str if numeric_pattern.match(x))
            
            if numeric_count / len(sample) > 0.7:  # 70% threshold
                try:
                    # Remove commas, dollar signs, percentages
                    cleaned = (
                        df[col]
                        .astype(str)
                        .str.replace(',', '')
                        .str.replace('$', '')
                        .str.replace('%', '')
                        .str.strip()
                    )
                    df[col] = pd.to_numeric(cleaned, errors='coerce')
                    print(f"✓ Converted '{col}' to numeric")
                except Exception as e:
                    print(f"✗ Could not convert '{col}': {e}")
    return df


def fix_date_columns(df):
    """Detect and convert date columns"""
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(50)
            if len(sample) == 0:
                continue
            
            # Try to parse as dates
            try:
                parsed = pd.to_datetime(sample, errors='coerce')
                if parsed.notna().sum() / len(sample) > 0.7:  # 70% successfully parsed
                    df[col] = pd.to_datetime(df[col], errors='coerce')
                    print(f"✓ Converted '{col}' to datetime")
            except:
                pass
    return df


def fix_boolean_columns(df):
    """Convert text boolean values to actual boolean"""
    bool_mapping = {
        'yes': True, 'no': False,
        'true': True, 'false': False,
        'y': True, 'n': False,
        't': True, 'f': False,
        '1': True, '0': False
    }
    
    for col in df.columns:
        if df[col].dtype == 'object':
            sample = df[col].dropna().head(100)
            if len(sample) == 0:
                continue
            
            sample_lower = sample.astype(str).str.lower().str.strip()
            unique_vals = set(sample_lower.unique())
            
            # Check if all unique values are boolean-like
            if unique_vals.issubset(bool_mapping.keys()):
                df[col] = df[col].astype(str).str.lower().str.strip().map(bool_mapping)
                print(f"✓ Converted '{col}' to boolean")
    return df


def handle_missing_values(df):
    """Report missing values (don't fill automatically)"""
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("\n⚠ Missing values found:")
        for col, count in missing[missing > 0].items():
            pct = (count / len(df)) * 100
            print(f"  {col}: {count} ({pct:.1f}%)")
    return df


def remove_empty_rows_cols(df):
    """Remove completely empty rows and columns"""
    before_rows = len(df)
    before_cols = len(df.columns)
    
    # Remove empty columns
    df = df.dropna(axis=1, how='all')
    
    # Remove empty rows
    df = df.dropna(axis=0, how='all')
    
    removed_cols = before_cols - len(df.columns)
    removed_rows = before_rows - len(df)
    
    if removed_cols > 0:
        print(f"✓ Removed {removed_cols} empty columns")
    if removed_rows > 0:
        print(f"✓ Removed {removed_rows} empty rows")
    
    return df


# Example usage
if __name__ == "__main__":
    # Clean a CSV file
    cleaned_df = clean_csv("input.csv", "fixed.csv")
    print("\n" + "="*50)
    print("CLEANING COMPLETE")
    print("="*50)