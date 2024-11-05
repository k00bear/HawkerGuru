# data_handlers/merge_hawker_data.py

import pandas as pd
import os
from pathlib import Path
from typing import Optional, Tuple
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HawkerDataMerger:
    """Class to handle merging of hawker centre data from different sources."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """Initialize paths for data files."""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.raw_data_dir = self.project_root / 'data' / '01_raw'
        self.processed_data_dir = self.project_root / 'data' / '02_processed'
        self.output_dir = self.project_root / 'data'
        
    def load_dataframes(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Load the source Excel files into DataFrames."""
        try:
            # Load main hawker centres list
            hawker_list_path = self.raw_data_dir / 'HawkerCentresList.xlsx'
            df_main = pd.read_excel(hawker_list_path)
            logger.info(f"Loaded main hawker list with {len(df_main)} entries")
            
            # Load processed geojson data
            geojson_data_path = self.processed_data_dir / 'hawker_centres_from_geojson.xlsx'
            df_geo = pd.read_excel(geojson_data_path)
            logger.info(f"Loaded geojson data with {len(df_geo)} entries")
            
            return df_main, df_geo
            
        except FileNotFoundError as e:
            logger.error(f"Could not find required file: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def clean_and_standardize(self, df_main: pd.DataFrame, df_geo: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Clean and standardize the dataframes before merging."""
        try:
            # Clean column names
            df_main.columns = df_main.columns.str.strip()
            df_geo.columns = df_geo.columns.str.strip()
            
            # Standardize hawker centre names for matching
            df_main['Hawker Centre'] = df_main['Hawker Centre'].str.strip().str.upper()
            df_geo['Name'] = df_geo['Name'].str.strip().str.upper()
            
            # Log any potential mismatches
            main_centres = set(df_main['Hawker Centre'])
            geo_centres = set(df_geo['Name'])
            unmatched = main_centres - geo_centres
            if unmatched:
                logger.warning(f"Found {len(unmatched)} unmatched centres: {unmatched}")
            
            return df_main, df_geo
            
        except Exception as e:
            logger.error(f"Error in data cleaning: {str(e)}")
            raise
    
    def merge_data(self) -> pd.DataFrame:
        """Merge the hawker centre data and save to Excel."""
        try:
            # Load data
            df_main, df_geo = self.load_dataframes()
            
            # Clean and standardize
            df_main, df_geo = self.clean_and_standardize(df_main, df_geo)
            
            # Perform left merge
            merged_df = pd.merge(
                df_main,
                df_geo,
                left_on='Hawker Centre',
                right_on='Name',
                how='left',
                indicator=True
            )
            
            # Log merge results
            logger.info(f"Merge complete. Results:")
            logger.info(f"Total rows: {len(merged_df)}")
            logger.info(f"Merge statistics:\n{merged_df['_merge'].value_counts()}")
            
            # Drop unnecessary columns and rename for clarity
            columns_to_drop = ['Name', '_merge']
            merged_df = merged_df.drop(columns=columns_to_drop)
            
            # Save merged data
            output_path = self.output_dir / 'HawkerCentres.xlsx'
            merged_df.to_excel(output_path, index=False)
            logger.info(f"Saved merged data to {output_path}")
            
            return merged_df
            
        except Exception as e:
            logger.error(f"Error in merge process: {str(e)}")
            raise

def main():
    """Main function to execute the merge process."""
    try:
        merger = HawkerDataMerger()
        merged_data = merger.merge_data()
        logger.info("Merge process completed successfully")
        
    except Exception as e:
        logger.error(f"Failed to complete merge process: {str(e)}")
        raise

if __name__ == "__main__":
    main()