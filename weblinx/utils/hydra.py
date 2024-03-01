"""
Miscellaneous Hydra-related utilities.
"""

from pathlib import Path


def resolve_cache_path(cfg) -> 'tuple[str, bool]':
    """
    Assuming we have the following:
    - cfg.data.cache : controls whether to read/write from cache or not
    - cfg.data.cache_dir : the directory to store the cache file, if cache=True
    - cfg.data.cache_filename : the name of the cache file, if cache=True
    - cfg.data.load_file_from_cache : controls whether to load from cache or not

    This will return the path to the cache file and load_from_cache_file boolean.

    Parameters
    ----------
    cfg : dict
        The configuration object. It must be a hydrated OmegaConf object.

    Returns
    -------
    tuple[str, bool]
        The path to the cache file and the load_from_cache_file boolean.
    """

    if cfg.data.cache is None or cfg.data.cache_filename is None:
        load_from_cache_file = False
        cache_path = None

        return cache_path, load_from_cache_file

    cache_dir = Path(cfg.data.cache_dir).expanduser()
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = str(cache_dir / cfg.data.cache_filename)

    return cache_path, cfg.data.load_from_cache_file


def save_path_to_hydra_logs(save_dir, save_name="hydra_path.txt"):
    """
    This helper function saves the path to the hydra logs into the model directory.
    This is useful for archival purposes.

    Parameters
    ----------
    save_dir : str
        The directory to save the hydra path to.

    save_name : str
        The name of the file to save the hydra path to.

    """
    try:
        from hydra.core.hydra_config import HydraConfig
    except ImportError:
        raise ImportError(
            "Hydra is not installed. Please install it with `pip install hydra-core`."
        )
    save_dir = Path(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)

    # Save the path to hydra_path into the model directory
    with open(save_dir.joinpath(save_name), "w") as f:
        hydra_path = HydraConfig.get().runtime.output_dir
        f.write(str(hydra_path))
