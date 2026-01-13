import camelot
import pandas as pd

# Read ALL pages from the PDF
tables = camelot.read_pdf(
    'Email_Statement_unlocked-1-20.pdf',
    pages='all',
    flavor='lattice',
    strip_text='\n'
)

print(f"Found {len(tables)} tables across all pages\n")

# Group tables by structure (number of columns)
table_groups = {}
for i, table in enumerate(tables):
    cols = table.shape[1]
    print(f"Table {i+1}: {table.shape} - Accuracy: {table.accuracy}")
    
    if cols not in table_groups:
        table_groups[cols] = []
    table_groups[cols].append(table.df)

print(f"\nFound {len(table_groups)} different table structures")

# Combine and export tables with same structure
for cols, dfs in table_groups.items():
    if len(dfs) > 1:
        combined = pd.concat(dfs, ignore_index=True)
        combined.to_csv(f'combined_{cols}_columns.csv', index=False)
        print(f"Combined {len(dfs)} tables with {cols} columns -> combined_{cols}_columns.csv")
    else:
        dfs[0].to_csv(f'single_table_{cols}_columns.csv', index=False)
        print(f"Single table with {cols} columns -> single_table_{cols}_columns.csv")