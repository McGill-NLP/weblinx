from huggingface_hub import HfApi

# save files to repository called McGill-NLP/statcan-dialogue-dataset-retrieval
# this will be the repository that the dataset will be uploaded to


data_dir = "reranking_data/csvs"

api = HfApi()


# for real:
repo_name = "McGill-NLP/WebLINX"
branch = "main"

# UNCOMMENT TO DELETE DIRECTORY INSIDE API
removed_dir = "reranking"

api.delete_folder(
    repo_id=repo_name,
    repo_type="dataset",
    path_in_repo=removed_dir,
    revision=branch,
    commit_message=f"Delete directory {removed_dir} from Hugging Face Hub via API",
)
