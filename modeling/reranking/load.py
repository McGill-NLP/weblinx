import json
from pathlib import Path

records_path = 'reranking_data/valid/input_records.jsonl'

with open(records_path, 'r') as f:
    records = [json.loads(line) for line in f]

r = records[0]
q = r['query']
