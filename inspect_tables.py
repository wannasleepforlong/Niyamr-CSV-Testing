import camelot
import pandas as pd

# Read ALL pages from the PDF
tables = camelot.read_pdf(
    'Email_Statement_unlocked-1-20.pdf',
    pages='all',
    flavor='lattice',
    strip_text='\n'
)

print(f"Found {len(tables)} tables\n")

for i, table in enumerate(tables):
    print(f"Table {i+1} (Shape: {table.shape}):")
    print(table.df.head())
    print("-" * 20)
