import pandas as pd
import echr_extractor.echr as echr
import sys, json
from datetime import datetime

def print_log(message):
    """Print with timestamp and flush immediately"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}", flush=True)
    sys.stdout.flush()

def process_data(input_file, output_nodes, output_edges):
    print_log("Starting data processing")
    
    # Load and prepare data
    df = pd.read_csv(input_file, low_memory=False)
    print_log(f"Number of rows in metadata: {len(df)}")
    df = df.dropna(subset=['ecli'])
    df = df.drop_duplicates(subset=['ecli'])
    print_log(f"Number of rows after deduplication: {len(df)}")

    try:
        print_log(f"Processing {len(df)} cases")
        nodes, edges = echr.get_nodes_edges(df=df, save_file='n')
        print_log(f"Processing complete - Generated {len(nodes)} nodes and {len(edges)} edges")
        
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
        '../data/METADATA/echr_metadata2.csv',
        '../data/METADATA/nodes.json',
        '../data/METADATA/edges.json'
    )