import pandas as pd
import echr_extractor.echr as echr
import sys, json
from datetime import datetime

def print_log(message):
    """Print with timestamp and flush immediately"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)
    sys.stdout.flush()

def process_data(input_file, output_nodes, output_edges, output_folder):
    print_log("Starting data processing")
    
    # Load and prepare data
    df = pd.read_csv(input_file, low_memory=False)
    print_log(f"Number of rows in metadata: {len(df)}")

    # Log rows with missing ECLIs before dropping them
    missing_eclis = df[df['ecli'].isna()]
    print_log(f"Found {len(missing_eclis)} rows with missing ECLIs")

    print_log("Merging duplicate entries...")
    # Count duplicates before merging
    duplicate_count = len(df) - len(df['ecli'].unique())
    print_log(f"Found {duplicate_count} duplicate entries")
    
    # df = df.groupby('ecli').agg({
    #     'article': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine unique articles
    #     'importance': 'first',  # Take first non-null value
    #     'doctypebranch': 'first',  # Take first non-null value
    #     'date': 'first',  # Take first non-null value
    #     'extractedappno': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine application numbers
    #     'scl': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine case law references
    #     'languageisocode': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine language codes
    #     'respondent': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine respondents
    #     'conclusion': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine conclusions
    #     'documentcollection': lambda x: ';'.join(set(filter(None, x.dropna()))),  # Combine collections
    #     'originatingbody_name': 'first',  # Take first non-null value
    #     'kpthesaurus': lambda x: ';'.join(set(filter(None, x.dropna())))  # Combine thesaurus terms
    # }).reset_index()

    try:
        print_log(f"Processing {len(df)} cases")
        nodes, edges = echr.get_nodes_edges(df=df, save_file='n')
        print_log(f"Processing complete - Generated {len(nodes)} nodes and {len(edges)} edges")

        # Save raw DataFrames for debugging/analysis
        nodes.to_csv(f'{output_folder}/nodes.csv', index=False)
        edges.to_csv(f'{output_folder}/edges.csv', index=False)
        print_log("Raw DataFrames saved to CSV files")
        
        # Convert edges DataFrame to proper JSON format
        edges_json = []
        for _, row in edges.iterrows():
            edge = {
                'ecli': row['ecli'],
                'references': row['references'] if isinstance(row['references'], list) else eval(row['references'])
            }
            edges_json.append(edge)
        
        # Convert nodes DataFrame to proper JSON format
        nodes_json = nodes.to_dict(orient='records')
        
        # Save as proper JSON
        with open(output_nodes, 'w', encoding='utf-8') as f:
            json.dump(nodes_json, f, indent=2, ensure_ascii=False)
            
        with open(output_edges, 'w', encoding='utf-8') as f:
            json.dump(edges_json, f, indent=2, ensure_ascii=False)
            
        print_log("Results saved successfully")
        
    except Exception as e:
        import traceback
        print_log(f"Error processing data: {str(e)}")
        print_log(f"Traceback: {traceback.format_exc()}")
        return False
    
    return True

if __name__ == '__main__':
    process_data(
        '../data/METADATA/echr_metadata.csv',
        '../data/METADATA/nodes.json',
        '../data/METADATA/edges.json',
        '../data/METADATA'
    )
