# convert json based format to the following csv format
# query, positive, negative
# query: string
# positive: list of strings
# negative: list of strings
# example: https://huggingface.co/datasets/mteb/askubuntudupquestions-reranking

import json
from pathlib import Path

import pandas as pd

def format_query(q):
    out = []

    for turn in q:
        out.append(f"{turn['role'].capitalize()}: {turn['content']}")
    
    return '\n'.join(out)

splits = ['valid', 'test_iid', 'test_cat', 'test_web', 'test_vis', 'test_geo']

for split in splits:
    records_path = f'reranking_data/{split}/input_records.jsonl'

    with open(records_path, 'r') as f:
        records = [json.loads(line) for line in f]

    # create reranking_data/csvs/
    csv_dir = Path('reranking_data/csvs')
    csv_dir.mkdir(parents=True, exist_ok=True)
    parquet_dir = Path('reranking_data/parquets')
    parquet_dir.mkdir(parents=True, exist_ok=True)
    jsonl_dir = Path('reranking_data/jsonls')
    jsonl_dir.mkdir(parents=True, exist_ok=True)


    data = []

    for r in records:
        qd = r['query']
        q = format_query(qd)

        positives = []
        negatives = []

        for doc in r['docs']:
            if doc['doc_id'] == r['doc_id']:
                positives.append(doc['doc'])
            else:
                negatives.append(doc['doc'])
        

        data.append(
            {'query_id': r['query_id'], 'query': q, 'positive': positives, 'negative': negatives, 'query_dict': qd}
        )

    # create pandas
    df = pd.DataFrame(data)

    # # save as parquet
    # output_path = parquet_dir / f'{split}.parquet'
    # df.to_parquet(output_path)

    # print(f"Saved to {output_path}")

    # # save as jsonl
    # output_path = jsonl_dir / f'{split}.jsonl'
    # with open(output_path, 'w') as f:
    #     for d in data:
    #         f.write(json.dumps(d) + '\n')
    
    # save as json.gz
    json_dir = Path('reranking_data/jsons')
    json_dir.mkdir(parents=True, exist_ok=True)
    
    # save as json.gz using pandas
    output_path = json_dir / f'{split}.json.gz'
    df.to_json(output_path, orient='records', lines=True, compression='gzip')

    # # save as csv
    # output_path = csv_dir / f'{split}.csv'
    # df.to_csv(output_path, index=False)

    print(f"Finished {split}!")