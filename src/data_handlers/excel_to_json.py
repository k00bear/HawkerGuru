# data_converter.py

import pandas as pd
import json
import os
from pathlib import Path
from typing import Dict, List

PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

def convert_excel_to_json(data_dir: str = DATA_DIR) -> None:
    """
    Convert Excel file to JSON format and save in the same directory
    Args:
        data_dir: Directory containing the Excel file
    """
    # Construct file paths
    excel_path = os.path.join(data_dir, 'AGuideToArticleOfSale.xlsx')
    json_path = os.path.join(data_dir, 'article_of_sale.json')
    
    # Check if Excel file exists
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel file not found at {excel_path}")
    
    # Read Excel file
    print(f"Reading Excel file from {excel_path}")
    df = pd.read_excel(excel_path)
    
    # Clean column names and handle NaN values
    df.columns = df.columns.str.strip()
    df = df.fillna('')  # Replace NaN with empty string
    
    # Convert to dictionary format
    records = df.to_dict(orient='records')
    
    # Save as JSON file
    print(f"Saving JSON file to {json_path}")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    
    print("Conversion completed successfully!")
    print(f"Created JSON file with {len(records)} records")
    
    # Print first record as sample
    if records:
        print("\nSample record:")
        print(json.dumps(records[0], indent=2, ensure_ascii=False))

if __name__ == "__main__":
    try:
        convert_excel_to_json()
    except Exception as e:
        print(f"Error occurred: {str(e)}")