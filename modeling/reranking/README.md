# Generating reranking data

To process the reranking data into a JSON file that contains only data relevant for reranking, in a JSON format, run the following:
```bash
python modeling/reranking/process_to_json.py --splits valid test_iid test_cat test_geo test_vis test_web
```

To convert json for reranking (jsonl):
```bash
python modeling/reranking/convert_json_to_reranking.py
```

Upload to huggingface:
```bash
python modeling/reranking/upload_toHf.py
```