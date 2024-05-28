from huggingface_hub import HfApi

# save files to repository called McGill-NLP/statcan-dialogue-dataset-retrieval
# this will be the repository that the dataset will be uploaded to


data_dir = "reranking_data/jsons"

api = HfApi()

# for real:
repo_name = "McGill-NLP/WebLINX"
branch = "main"

# # for testing:
# repo_name = "xhluca/WebLINX-testing"
# branch = "main"
# api.create_repo(repo_id=repo_name, exist_ok=True, repo_type="dataset")

# upload now:
api.upload_folder(
    repo_id=repo_name,
    repo_type="dataset",
    path_in_repo="data/reranking",
    revision=branch,
    folder_path=data_dir,
    commit_message="Upload dataset files to Hugging Face Hub via API",
)
