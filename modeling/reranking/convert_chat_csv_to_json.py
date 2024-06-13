# convert data in modeling/wl_data/chat/*.csv to json.gz

import pandas as pd
from pathlib import Path

load_dir = Path('modeling/wl_data/chat')
save_dir = Path('modeling/wl_data/chat_jsons')
save_dir.mkdir(parents=True, exist_ok=True)

for file in load_dir.iterdir():
    if file.suffix == '.csv':
        df = pd.read_csv(file)
        df.to_json(save_dir / f'{file.stem}.json.gz', orient='records', lines=True, compression='gzip')
        print(f"Saved to {save_dir / f'{file.stem}.json.gz'}")

# Optional, if we want to upload to Hugging Face Hub via API
from huggingface_hub import HfApi

data_dir = "modeling/wl_data/chat_jsons"

api = HfApi()

# for real:
repo_name = "McGill-NLP/WebLINX"
branch = "main"

# # for testing:
# repo_name = "xhluca/WebLINX-testing"
# branch = "main"

# upload now:
api.upload_folder(
    repo_id=repo_name,
    repo_type="dataset",
    path_in_repo="data/chat",
    revision=branch,
    folder_path=data_dir,
    commit_message="Upload dataset files to Hugging Face Hub via API",
)