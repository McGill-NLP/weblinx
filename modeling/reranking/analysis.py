import json
import pandas as pd

# get average length of the query and doc for each file in reranking_data/jsonls
# also, get the total number of samples for each split as well
# it should be in the following format (query numbers only for avg_character_length):
# n_samples={"validation": None, "test_iid": None, "test_cat": None, "test_geo": None, "test_vis": None, "test_web": None},
# avg_character_length={"validation": None, "test_iid": None, "test_cat": None, "test_geo": None, "test_vis": None, "test_web": None},

# create a list of dictionaries
data = {'n_samples': {}, 'avg_character_length': {}}

# iterate over the splits
for split in ['valid', 'test_iid', 'test_cat', 'test_web', 'test_vis', 'test_geo']:
    # read the jsonl file
    df = pd.read_json(f'reranking_data/jsonls/{split}.jsonl', lines=True)
    
    # get the average length of the query and doc
    avg_query_len = df['query'].apply(len).mean()
    # avg_doc_len = df['positives'].apply(len).mean()

    # get the total number of samples
    n_samples = len(df)

    # add to the data
    data['n_samples'][split] = n_samples
    data['avg_character_length'][split] = round(avg_query_len, 2)

with open('reranking_data/analysis.json', 'w') as f:
    json.dump(data, f, indent=4)