import numpy as np
import pandas as pd
import re, os
import dateparser
from echr_extractor.clean_ref import clean_pattern
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
from functools import lru_cache
import multiprocessing
from typing import Dict, List, Set, Tuple

# Global cache for DataFrame lookups
case_name_cache: Dict[str, Set[str]] = {}

def clear_caches() -> None:
    """Clear all caches when needed"""
    global case_name_cache
    case_name_cache.clear()
    lookup_casename.cache_clear()  # Clear the LRU cache


def open_metadata(PATH_metadata):
    """
    Finds the ECHR metadata file and loads it into a dataframe
    
    param filename_metadata: string with path to metadata
    """
    try:
        df = pd.read_csv(PATH_metadata)  # change hard coded path
        print(df.columns)
        return df
    except FileNotFoundError:
        print("File not found. Please check the path to the metadata file.")
        return False
    
def get_casename(ref):
    count = 0
    if 'v.' in ref:
        slice_at_versus = ref.split('v.')  # skip if typo (count how many)
    elif 'c.' in ref:
        slice_at_versus = ref.split('c.')
    else:
        count = count + 1
        name = ref.split(',')
        return name[0]

    num_commas = slice_at_versus[0].count(',')

    if num_commas > 0:
        num_commas = num_commas + 1
        name = ",".join(ref.split(",", num_commas)[:num_commas])
    else:
        name = ref.split(',')
        return name[0]
    return name

def metadata_to_nodesedgeslist(df):
    """
    Returns a dataframe where column 'article' only contains a certain article

    param df: the complete dataframe from the metadata
    """
    
    return df

def retrieve_nodes_list(df):
    """
    Returns a dataframe where 'ecli' is moved to the first column.
    
    param df: the dataframe after article filter
    """
    df = metadata_to_nodesedgeslist(df)
    # Instead of dropping first column blindly, keep appno
    df_copy = df.copy()
    
    # Move ecli to first position
    col = df_copy.pop("ecli")
    df_copy.insert(0, col.name, col)
    
    return df_copy

@lru_cache(maxsize=50000)
def get_year_from_ref(ref_tuple: Tuple[str]) -> int:
    """Cached version of get_year_from_ref"""
    ref = list(ref_tuple)  # Convert tuple back to list
    for component in ref:
        if '§' in component:
            continue
        component = re.sub('judgment of ', "", component)
        if dateparser.parse(component) is not None:
            date = dateparser.parse(component)
        elif ("ECHR" in component or "CEDH" in component):
            date = re.sub('ECHR |CEDH ', '', component).strip()
            date = re.sub('-.*|\\s.*', '', date)
            date = dateparser.parse(date)
   
    try:
        return date.year
    except:
        return 0

@lru_cache(maxsize=50000)
def lookup_casename(ref: str, df_dict: Tuple[Tuple]) -> Set[str]:
    """
    Process the reference for lookup in metadata.
    Returns the ECLIs corresponding to the cases.
    """
    name = get_casename(ref)
    patterns = clean_pattern

    uptext = name.upper()

    # Simple replacements as in original
    if 'NO.' in uptext:
        uptext = uptext.replace('NO.', 'No.')
    if 'BV' in uptext:
        uptext = uptext.replace('BV', 'B.V.')
    if 'v.' in name:
        uptext = uptext.replace('V.', 'v.')
    else:
        uptext = uptext.replace('C.', 'c.')

    # Apply cleaning patterns
    for pattern in patterns:
        uptext = re.sub(pattern, '', uptext)

    # Remove anything in square brackets and trim
    uptext = re.sub(r'\[.*', "", uptext).strip()
    
    # Convert tuple to dict for processing
    df_dict_list = [dict(zip(('docname', 'ecli', 'appno'), row)) for row in df_dict]
    
    # FIXED: Require exact case name match
    matches = [row['ecli'] for row in df_dict_list 
              if pd.notna(row.get('docname')) and 
              pd.notna(row.get('ecli')) and 
              f"CASE OF {uptext}" == row['docname'].upper()]  # Exact match only!
    
    return set(matches)

def process_batch(batch_data: Tuple[pd.DataFrame, List[Dict], int]) -> Tuple[List[Dict], List[Dict]]:
    """Process a batch of nodes in parallel"""
    df_batch, df_dict, batch_size = batch_data
    edges_list = []
    missing_cases = []

    # Convert tuple of tuples back to list of dicts for consistent access
    df_dict_list = [dict(zip(('docname', 'ecli', 'appno'), row)) for row in df_dict]
    
    for _, item in df_batch.iterrows():
        # Track rows with NaN ECLI source in missing_cases
        if pd.isna(item.ecli):
            missing_cases.append({
                'source_ecli': 'NaN',
                'missing_reference': 'Source ECLI is missing',
                'reference_type': 'missing_source'
            })
            continue
            
        eclis = set()
        
        if pd.notna(item.extractedappno):
            extracted_appnos = set(item.extractedappno.split(';'))
            matches = [row for row in df_dict_list 
                      if pd.notna(row.get('appno')) and 
                      row['appno'] in extracted_appnos]
            
            found_appnos = {row['appno'] for row in matches}
            unmatched_appnos = extracted_appnos - found_appnos
            for appno in unmatched_appnos:
                missing_cases.append({
                    'source_ecli': item.ecli,
                    'missing_reference': f"Application number: {appno}",
                    'reference_type': 'extracted_appno'
                })
            
            eclis.update(row['ecli'] for row in matches if pd.notna(row.get('ecli')))
        
        if pd.notna(item.scl):
            ref_list = [ref.strip() for ref in item.scl.split(';')]
            
            for ref in ref_list:
                app_numbers = set(re.findall(r"[0-9]{3,5}/[0-9]{2}", ref))
                if app_numbers:
                    matches = [row for row in df_dict_list 
                             if pd.notna(row.get('appno')) and 
                             row['appno'] in app_numbers]
                    
                    found_apps = {row['appno'] for row in matches}
                    unmatched_apps = app_numbers - found_apps
                    for app in unmatched_apps:
                        missing_cases.append({
                            'source_ecli': item.ecli,
                            'missing_reference': f"Application number: {app}",
                            'reference_type': 'scl_appno'
                        })
                    
                    eclis.update(row['ecli'] for row in matches if pd.notna(row.get('ecli')))
                else:
                    case_eclis = lookup_casename(ref, df_dict)
                    if not case_eclis:
                        missing_cases.append({
                            'source_ecli': item.ecli,
                            'missing_reference': ref,
                            'reference_type': 'case_name'
                        })
                    eclis.update(case_eclis)
        
        valid_refs = [ref for ref in eclis 
                     if isinstance(ref, str) and 
                     pd.notna(ref) and 
                     ref != item.ecli and 
                     ref.startswith('ECLI:')]
        
        edges_list.append({
            'ecli': item.ecli,
            'references': valid_refs
        })
    
    return edges_list, missing_cases

def retrieve_edges_list(df: pd.DataFrame, df_unfiltered: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Optimized version of edge list retrieval with parallel processing"""
    num_cores = multiprocessing.cpu_count()
    batch_size = max(100, len(df) // (num_cores * 4))
    
    # Convert DataFrame to tuple of tuples (hashable) for caching
    df_dict = tuple(
        tuple(row) for row in df_unfiltered[['docname', 'ecli', 'appno']].itertuples(index=False)
    )
    
    batches = [(df[i:i+batch_size], df_dict, batch_size) 
              for i in range(0, len(df), batch_size)]
    
    edges_list = []
    all_missing_cases = []
    
    with tqdm(total=len(df), desc="Processing edges") as pbar:
        with ProcessPoolExecutor(max_workers=num_cores) as executor:
            for batch_edges, batch_missing in executor.map(process_batch, batches):
                edges_list.extend(batch_edges)
                all_missing_cases.extend(batch_missing)
                pbar.update(batch_size)
    
     # Print summary statistics
    print("\nReference Extraction Summary:")
    print(f"Total nodes processed: {len(df)}")
    print(f"Total edges found: {sum(len(d['references']) for d in edges_list)}")
    print(f"Total missing references: {len(all_missing_cases)}")
    
    return pd.DataFrame(edges_list), pd.DataFrame(all_missing_cases)


def echr_nodes_edges(metadata_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Create nodes and edges list for the ECHR data with progress tracking
    """
    print('\n--- COLLECTING METADATA ---\n')
    data = open_metadata(metadata_path)
    if data is False:
        raise FileNotFoundError(f"Could not open metadata file: {metadata_path}")

    print('\n--- EXTRACTING NODES LIST ---\n')
    nodes = retrieve_nodes_list(data)
    print(f"Number of nodes: {len(nodes)}")

    print('\n--- EXTRACTING EDGES LIST ---\n')
    edges, missing_df = retrieve_edges_list(nodes, data)
    print(f"\nExtracted {len(edges)} edges")
    print(f"Found {len(missing_df)} missing references")

    return nodes, edges, missing_df

def count_total_edges(edges_df: pd.DataFrame) -> Tuple[int, dict]:
    """
    Count total number of edges in the network with detailed statistics
    """
    stats = {
        'total_edges': 0,
        'total_source_nodes': len(edges_df),
        'nodes_with_refs': 0,
        'max_refs_per_node': 0,
        'refs_distribution': [],
        'suspicious_nodes': []  # Track nodes with unusually high number of references
    }
    
    for _, row in edges_df.iterrows():
        refs = row['references']
            
        # Handle string representation of list
        if isinstance(refs, str):
            try:
                refs_list = eval(refs)
            except:
                continue
        else:
            refs_list = refs
            
        # Count valid references
        valid_refs = [ref for ref in refs_list 
                     if isinstance(ref, str) and 
                     not pd.isna(ref) and 
                     ref.startswith('ECLI:')]
        
        num_refs = len(valid_refs)
        if num_refs > 0:
            stats['nodes_with_refs'] += 1
            stats['total_edges'] += num_refs
            stats['refs_distribution'].append(num_refs)
            stats['max_refs_per_node'] = max(stats['max_refs_per_node'], num_refs)
            
            # Flag suspiciously high number of references (e.g., > 100)
            if num_refs > 100:
                stats['suspicious_nodes'].append({
                    'ecli': row['ecli'],
                    'ref_count': num_refs
                })
    
    # Calculate statistics
    if stats['refs_distribution']:
        stats['avg_refs_per_node'] = sum(stats['refs_distribution']) / len(stats['refs_distribution'])
        stats['median_refs_per_node'] = np.median(stats['refs_distribution'])
    
    # Print detailed analysis
    print("\nEdge Analysis:")
    print(f"Total source nodes: {stats['total_source_nodes']}")
    print(f"Nodes with references: {stats['nodes_with_refs']}")
    print(f"Total edges: {stats['total_edges']}")
    print(f"Average refs per node: {stats.get('avg_refs_per_node', 0):.2f}")
    print(f"Median refs per node: {stats.get('median_refs_per_node', 0):.2f}")
    print(f"Max refs per node: {stats['max_refs_per_node']}")
    
    if stats['suspicious_nodes']:
        print("\nSuspicious Nodes (>100 references):")
        for node in stats['suspicious_nodes']:
            print(f"ECLI: {node['ecli']}, References: {node['ref_count']}")
    
    return stats['total_edges'], stats


def count_application_numbers(metadata_file):
    # Read the metadata CSV
    df = pd.read_csv(metadata_file, low_memory=False)
    print(f"Total rows in metadata: {len(df)}")
    
    # Count rows with non-null extractedappno
    has_appno = df['extractedappno'].notna()
    print(f"Rows with application numbers: {has_appno.sum()}")
    
    # Count total unique application numbers
    total_appnos = 0
    unique_appnos = set()
    
    for appno in df[has_appno]['extractedappno']:
        if isinstance(appno, str):
            # Split by semicolon as they're semicolon-separated
            appnos = appno.split(';')
            total_appnos += len(appnos)
            unique_appnos.update(appnos)
    
    print(f"Total application numbers: {total_appnos}")
    print(f"Unique application numbers: {len(unique_appnos)}")


def test_process_batch():
    """
    Test the process_batch function with known input and expected output.
    """
    # Create test data
    test_batch = pd.DataFrame([
        {
            'ecli': 'ECLI:CE:ECHR:2020:0101JUD001234567',
            'extractedappno': '1234/56;5678/90',  # Two application numbers
            'scl': 'Smith v. UK (no. 9876/54); Jones c. France'  # One app number + one case name
        },
        {
            'ecli': 'ECLI:CE:ECHR:2020:0102JUD002345678',
            'extractedappno': None,
            'scl': None
        },
        {
            'ecli': 'ECLI:CE:ECHR:2020:0103JUD003456789',
            'extractedappno': '3456/78',
            'scl': 'Invalid reference'  # Should be tracked as missing
        }
    ])

    # Create test metadata dictionary
    test_dict = [
        {'docname': 'CASE OF SMITH v. THE UNITED KINGDOM', 
         'ecli': 'ECLI:CE:ECHR:2010:0101JUD009876540', 
         'appno': '9876/54'},
        {'docname': 'CASE OF JONES v. FRANCE', 
         'ecli': 'ECLI:CE:ECHR:2015:0101JUD008765432', 
         'appno': '8765/43'},
        {'docname': 'Test Case', 
         'ecli': 'ECLI:CE:ECHR:2010:0101JUD001234560', 
         'appno': '1234/56'},
        {'docname': 'Test Case 2', 
         'ecli': 'ECLI:CE:ECHR:2010:0101JUD005678900', 
         'appno': '5678/90'},
        {'docname': 'Test Case 3', 
         'ecli': 'ECLI:CE:ECHR:2010:0101JUD003456780', 
         'appno': '3456/78'}
    ]

    # Convert to tuple for caching
    test_dict_tuple = tuple(tuple(d.values()) for d in test_dict)
    
    # Process batch
    edges_list, missing_cases = process_batch((test_batch, test_dict_tuple, 3))

    # Expected results
    expected_edges = [
        {
            'ecli': 'ECLI:CE:ECHR:2020:0101JUD001234567',
            'references': [
                'ECLI:CE:ECHR:2010:0101JUD001234560',  # From extractedappno
                'ECLI:CE:ECHR:2010:0101JUD005678900',  # From extractedappno
                'ECLI:CE:ECHR:2010:0101JUD009876540',  # From scl appno
                'ECLI:CE:ECHR:2015:0101JUD008765432'   # From case name lookup
            ]
        },
        {
            'ecli': 'ECLI:CE:ECHR:2020:0102JUD002345678',
            'references': []  # No references
        },
        {
            'ecli': 'ECLI:CE:ECHR:2020:0103JUD003456789',
            'references': [
                'ECLI:CE:ECHR:2010:0101JUD003456780'  # From extractedappno
            ]
        }
    ]

    expected_missing = [
        {
            'source_ecli': 'ECLI:CE:ECHR:2020:0103JUD003456789',
            'missing_reference': 'Invalid reference',
            'reference_type': 'case_name'
        }
    ]
    
    # Print actual results for debugging
    print("\nActual Results:")
    for edge in edges_list:
        print(f"\nECLI: {edge['ecli']}")
        print(f"References: {edge['references']}")
    
    print("\nMissing Cases:")
    for case in missing_cases:
        print(f"\nSource: {case['source_ecli']}")
        print(f"Missing: {case['missing_reference']}")
        print(f"Type: {case['reference_type']}")

    # Assertions with better error messages
    assert len(edges_list) == 3, f"Expected 3 cases, got {len(edges_list)}"
    
    # Check first case (multiple references)
    actual_refs = len(edges_list[0]['references'])
    assert actual_refs == 4, f"Expected 4 references for first case, got {actual_refs}. References: {edges_list[0]['references']}"
    assert all(ref.startswith('ECLI:') for ref in edges_list[0]['references']), "All references should be ECLIs"
    
    
    # Check second case (no references)
    assert len(edges_list[1]['references']) == 0, "Should have no references for second case"
    
    # Check third case (one reference + one missing)
    assert len(edges_list[2]['references']) == 1, "Should find 1 reference for third case"
    assert len(missing_cases) == 1, "Should track one missing reference"
    
    # Check for duplicates
    for edge in edges_list:
        assert len(edge['references']) == len(set(edge['references'])), "Should not contain duplicate references"
        assert edge['ecli'] not in edge['references'], "Should not contain self-references"

    print("All tests passed!")


if __name__ == "__main__":
    clear_caches()

    # test_process_batch()

    clear_caches()

     # Get the absolute path to the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Construct paths relative to project root
    metadata_path = os.path.join(project_root, 'data', 'METADATA', 'echr_metadata.csv')
    output_dir = os.path.join(project_root, 'data', 'METADATA', 'optimized')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    count_application_numbers(metadata_path)

    # Example usage
    nodes, edges, missing = echr_nodes_edges(metadata_path)

    print(f"Number of nodes: {len(nodes)}")
    print(f"Number of entries in edges: {len(edges)}")

    _, _ = count_total_edges(edges)

    # Save results
    nodes.to_csv(os.path.join(output_dir, 'nodes.csv'), index=False)
    edges.to_csv(os.path.join(output_dir, 'edges.csv'), index=False)
    missing.to_csv(os.path.join(output_dir, 'missing_cases.csv'), index=False)
