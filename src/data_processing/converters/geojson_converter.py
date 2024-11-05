import pandas as pd
import json
import re
from pathlib import Path
from typing import Dict, List

def extract_attributes(description: str) -> Dict:
    """Extract attributes from HTML-formatted description"""
    attrs = {}
    
    # Extract values between <th> and <td> tags
    matches = re.findall(r'<th>(.*?)<\/th>\s*<td>(.*?)<\/td>', description)
    for key, value in matches:
        attrs[key.strip()] = value.strip()
    
    return attrs

def convert_geojson_to_excel():
    # Set up paths relative to project root
    PROJECT_ROOT = Path(__file__).parent.parent.parent
    input_path = PROJECT_ROOT / "data" / "01_raw" / "HawkerCentresGEOJSON.geojson"
    output_path = PROJECT_ROOT / "data" / "02_processed" / "hawker_centres_from_geojson.xlsx"
    
    # Read GEOJSON file
    with open(input_path, 'r', encoding='utf-8') as f:
        geojson_data = json.load(f)
    
    # Extract data from features
    data = []
    for feature in geojson_data['features']:
        # Get coordinates
        coords = feature['geometry']['coordinates']
        
        # Extract attributes from description
        attrs = extract_attributes(feature['properties'].get('Description', ''))
        
        # Create row with key information
        row = {
            'Name': attrs.get('NAME', ''),
            'Status': attrs.get('STATUS', ''),
            'Description': attrs.get('DESCRIPTION', ''),
            'Address': f"{attrs.get('ADDRESSBLOCKHOUSENUMBER', '')} {attrs.get('ADDRESSSTREETNAME', '')}".strip(),
            'Postal_Code': attrs.get('ADDRESSPOSTALCODE', ''),
            'Building_Name': attrs.get('ADDRESSBUILDINGNAME', ''),
            'GFA': attrs.get('APPROXIMATE_GFA', ''),
            'Latitude': coords[1],
            'Longitude': coords[0],
            'Last_Updated': attrs.get('FMEL_UPD_D', '')
        }
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to Excel
    df.to_excel(output_path, index=False)
    
    print(f"Created Excel file with {len(data)} hawker centres")
    print(f"Output saved to: {output_path}")
    print("\nColumns included:")
    for col in df.columns:
        print(f"- {col}")

if __name__ == "__main__":
    convert_geojson_to_excel()