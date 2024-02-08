import os
from pathlib import Path


def get_env_dict(filepath: str = ".env") -> dict:
    """
    Get environment variables from a .env file.

    Parameters
    ----------
    filepath : str, optional
        The path to the .env file. Defaults to '.env'.

    Returns
    -------
    dict
        A dictionary of environment variables.
    """
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filepath}")

    with path.open() as f:
        env_vars = f.readlines()
        # Split by first =, conver to dict
        env_vars_list = [line.split("=", 1) for line in env_vars]
        env_vars_dict = {key: value.strip() for key, value in env_vars_list}

    return env_vars_dict


def set_env_vars(filepath: str = ".env") -> None:
    """
    Set environment variables from .env file into the current os.environ.

    Parameters
    ----------
    filepath : str, optional
        The path to the .env file. Defaults to '.env'.

    """
    env_vars_dict = get_env_dict(filepath)
    for key, value in env_vars_dict.items():
        os.environ[key] = value
