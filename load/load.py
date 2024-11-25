# Run: python load.py --input_path ECHR_metadata.csv --save_path EHCR --metadata



import numpy as np
import pandas as pd
import re
import os
import sys
import time
import dateutil.parser as parser  
import dateparser
import datetime
import argparse
import echr_extractor as echr
from os.path import dirname, abspath

current_dir = dirname(dirname(abspath(__file__)))
correct_dir = '\\'.join(current_dir.replace('\\', '/').split('/')[:-2])
sys.path.append(correct_dir)

def open_metadata(filename_metadata):
    """
    Returns a dataframe constructed from the given csv file.

    params:
    filename_metadata -- the filename string to the csv file
    """
    df = pd.read_csv(filename_metadata)
    return df

def filter_article(df,articles):
    """
    Returns a dataframe where column 'article' only contains a certain article

    params:
    df -- the complete dataframe from the metadata
    """
    try:
        df = df[df['article'].notna()]
        # df = df[df.article.str.contains(r'\b6;6-1\b', regex=True)]      # in case a specific article is wanted
        #article_numbers = ['6', '6-1', '13']
        pattern = '|'.join(map(str, articles))
        df = df[df.article.str.contains(pattern, regex=True)] 
    except:
        return df
    return df


def retrieve_nodes_list(df,articles):
    """
    Returns a dataframe where 'ecli' is moved to the first column.

    params:
    df -- the dataframe after article filter
    """
    if articles != '':  
        print("it filters!")
        df = filter_article(df,articles)    # use this if you want to filter a specific article
    return df


def retrieve_edges_list(df, df_unfiltered, articles):
    """
    Returns a dataframe consisting of 2 columns 'ecli' and 'reference' which
    indicate a reference link between cases.

    params:
    df -- the node list extracted from the metadata
    df_unfiltered -- the complete dataframe from the metadata
    """
    edges = pd.DataFrame(columns=['ecli', 'references'])

    count = 0
    tot_num_refs = 0
    missing_cases = []
    for index, item in df.iterrows():
        
        # to keep track of progress
        if index % 10 == 0:
            print(index, '/', len(df.index))

        eclis = []
        app_number = [] 

        if item.extractedappno is not np.nan:
            extracted_appnos = item.extractedappno.split(';')

        if item.scl is not np.nan:
            """
            Split the references from the scl column i nto a list of references.

            Example:
            references in string: "Ali v. Switzerland, 5 August 1998, § 32, Reports of Judgments and 
            Decisions 1998-V;Sevgi Erdogan v. Turkey (striking out), no. 28492/95, 29 April 2003"

            ["Ali v. Switzerland, 5 August 1998, § 32, Reports of Judgments and 
            Decisions 1998-V", "Sevgi Erdogan v. Turkey (striking out), no. 
            28492/95, 29 April 2003"]
            """
            ref_list = item.scl.split(';')
            new_ref_list = []
            for ref in ref_list:
                ref = re.sub('\n', '', ref)
                new_ref_list.append(ref)

            tot_num_refs = tot_num_refs + len(ref_list)

            for ref in new_ref_list:
                num_ref = len(new_ref_list)

                app_number = re.findall("[0-9]{3,5}\/[0-9]{2}", ref)
                app_number = app_number + extracted_appnos
                app_number = set(app_number)

                if len(app_number) > 0:

                    # get dataframe with all possible cases by application number
                    if len(app_number) > 1:
                        app_number = [';'.join(app_number)]

                    case = lookup_app_number(app_number, df_unfiltered)

                else: # if no application number in reference
                    # get dataframe with all possible cases by casename
                    case = lookup_casename(ref, df_unfiltered)

                if len(case) == 0:
                    case = lookup_casename(ref, df_unfiltered)

                components = ref.split(',')
                # get the year of case
                year_from_ref = get_year_from_ref(components)

                # remove cases in different language than reference
                for id, it in case.iterrows():
                    if 'v.' in components[0]:
                        lang = 'ENG'
                    else:
                        lang = 'FRE'

                    if lang not in it.languageisocode:
                        case = case[case['languageisocode'].str.contains(lang, regex=False, flags=re.IGNORECASE)]

                for id, i in case.iterrows():
                    date = dateparser.parse(i.judgementdate)
                    try:
                        year_from_case = date.year
                    except:
                        year_from_case = year_from_ref

                    if year_from_case - year_from_ref == 0:
                        case = case[case['judgementdate'].str.contains(str(year_from_ref), regex=False, flags=re.IGNORECASE)]

                case = filter_article(case, articles)

                if len(case) > 0:

                    for _,row in case.iterrows():
                        eclis.append(row.ecli)

                else:
                    count = count + 1
                    missing_cases.append(ref)

            eclis = set(eclis)

            #add ecli to edges list
            if len(eclis) == 0:
                continue
            else:
                edges = pd.concat(
                    [edges, pd.DataFrame.from_records([{'ecli': item.ecli, 'references': list(eclis)}])])
        else:
            edges = pd.concat(
                    [edges, pd.DataFrame.from_records([{'ecli': item.ecli, 'references': []}])])

    print("num missed cases: ", count)
    print("total num of refs: ", tot_num_refs)
    missing_cases_set = set(missing_cases)
    missing_cases = list(missing_cases_set)

    missing_df = pd.DataFrame(missing_cases)
    missing_df.to_csv('missing_cases.csv', index=False, encoding='utf-8')
    edges = edges.groupby('ecli', as_index=False).agg({'references' : 'sum'})
    return edges

def lookup_app_number(pattern, df):
    """
    Returns a list with rows containing the cases linked to the found app numbers.

    params:
    pattern -- the full application number from the reference
    df -- the full metadata dataframe
    """
    row = df.loc[df['appno'].isin(pattern)]

    if row.empty:
        return pd.DataFrame()
    elif row.shape[0] > 1:
        return row
    else:
        return row


def lookup_casename(ref, df):
    """
    Process the reference for lookup in metadata.
    Returns the rows corresponding to the cases.

    - Example of the processing (2 variants) -

    Original reference from scl:
    - Hentrich v. France, 22 September 1994, § 42, Series A no. 296-A
    - Eur. Court H.R. James and Others judgment of 21 February 1986,
    Series A no. 98, p. 46, para. 81

    Split on ',' and take first item:
    Hentrich v. France
    Eur. Court H.R. James and Others judgment of 21 February 1986

    If certain pattern from CLEAN_REF in case name, then remove:
    Eur. Court H.R. James and Others judgment of 21 February 1986 -->
        James and Others

    Change name to upper case and add additional text to match metadata:
    Hentrich v. France --> CASE OF HENTRICH V. FRANCE
    James and Others --> CASE OF JAMES AND OTHERS
    """

    name = get_casename(ref)

    f = open('CLEAN_REF.txt', 'r')
    patterns = f.read().splitlines()

    uptext = name.upper()

    # clean specific abbreviations
    if 'NO.' in uptext:
        uptext = uptext.replace('NO.', 'No.')

    if 'BV' in uptext:
        uptext = uptext.replace('BV', 'B.V.')

    if 'v.' in name:
        uptext = uptext.replace('V.', 'v.')
        lang = 'ENG'
    else:
        uptext = uptext.replace('C.', 'c.')
        lang = 'FRE'

    for pattern in patterns:
        uptext = re.sub(pattern, '', uptext)

    uptext = re.sub(r'\[.*', "", uptext)
    uptext = re.sub("[\(\[].*?[\)\]]", "", uptext) # remove text with (...)
    uptext = uptext.strip()
    
    if len(uptext) <= 1:
        row = pd.DataFrame()
    else:
        row = df[df['docname'].str.contains(uptext, regex=False, flags=re.IGNORECASE)]

    return row

def get_casename(ref):
    """
    Returns the casename extracted from a reference.

    params:
    ref -- the string containing the full reference
    """
    count = 0
    if 'v.' in ref:
        slice_at_versus = ref.split('v.')  
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

def get_year_from_ref(ref):
    """
    Returns the date mentioned in the reference.

    params:
    ref -- the string containing the full reference
    """
    for component in ref:
        if '§' in component:
            continue
        component = re.sub('judgment of ', "", component)
        if dateparser.parse(component) is not None:
            date = dateparser.parse(component)
        elif ("ECHR" in component or "CEDH" in component):
            if ("ECHR" in component or "CEDH" in component):
                date = re.sub('ECHR ', '', component)
                date = re.sub('CEDH ', '', date)
                date = date.strip()
                date = re.sub('-.*', '', date)
                date = re.sub('\s.*', '', date)
                date = dateparser.parse(date)
    try:
        return date.year
    except:
        return 0


def create_argument_parser():
    """
    Creates an argument parser
    Returns:
        parser (argparse.ArgumentParser): The argument parser
    """
    parser = argparse.ArgumentParser(description="Generate a nodes and edges list")
    parser.add_argument("--input_path", type=str, required=True, help="The metadata file")
    parser.add_argument("--save_path", type=str, required=True, help="The path to save the nodes and edges lists")
    parser.add_argument("--metadata", type=bool, required=True, default=False, action=argparse.BooleanOptionalAction, help="Include the retrieval of ECHR metadata")
    parser.add_argument('--articles', nargs='+', required=False, type=str, default='', help="A list of articles")
    return parser


# ---- RUN ----
args = create_argument_parser().parse_args()

# Ensure the save directory exists
os.makedirs(args.save_path, exist_ok=True)

if args.metadata == True:
    data = echr.get_echr(start_id=0,end_id=100000,save_file='n',verbose=True)
    complete_data = data.copy()

else:
    print('\n--- PREPARING DATAFRAME ---\n')
    data = open_metadata(filename_metadata=args.input_path)       
    complete_data = open_metadata(filename_metadata=args.input_path)  

print('\n--- CREATING NODES LIST ---\n')
nodes = retrieve_nodes_list(data, args.articles)
print(nodes)

print('\n--- START EDGES LIST ---\n')
start = time.time()

print('\n--- CREATING EDGES LIST ---\n')
edges = retrieve_edges_list(nodes, complete_data, args.articles)
print(edges)
print("Done!")

print('\n--- POST-PROCESSING ---\n')
for index, item in edges.iterrows():
    item.references = set(item.references)
print("Done!")

print('\n--- CREATING CSV FILES ---\n')
edges.to_csv(os.path.join(args.save_path, 'edges.csv'), index=False, encoding='utf-8')
nodes.to_csv(os.path.join(args.save_path, 'nodes.csv'), index=False, encoding='utf-8')
print("Done!")

end = time.time()
print("\n--- DONE ---")
print("Time taken: ", time.strftime('%H:%M:%S', time.gmtime(end - start)))
