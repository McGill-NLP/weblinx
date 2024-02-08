"""
This module contains utility functions for manipulating urls.
"""

import urllib.parse


def shorten_url(url: str, width: int = 50, placeholder: str = "[...]") -> str:
    actual_width = width - len(placeholder)

    if len(url) <= width:
        return url
    if actual_width <= 0:
        raise ValueError(
            f"Width is too small. Your placeholder has length {len(placeholder)} but width is {width}."
        )

    return url[:width] + placeholder


def remove_subdomain(url: str) -> str:
    """
    Given a url, remove the subdomain part, if the subdomain is not in domains_allowed
    """

    tld_length = calculate_length_of_tld(url)
    # Get the domain name using urllib.parse
    parsed_url = urllib.parse.urlparse(url)
    # Split the domain name by .
    net_loc_split = parsed_url.netloc.split(".")
    # Based on the length of the tld, get the domain name (including the tld) and return it
    domain = ".".join(net_loc_split[-(tld_length + 1) :])

    return domain


def calculate_length_of_tld(url: str) -> int:
    """
    Given a url, calculate the length of the top level domain.
    In general, the length of tld is 1, e.g. .com, .org, .net, etc.

    However, there are some exceptions, e.g. .co.uk, .co.nz, etc.
    We want to return >1 for these cases.

    Parameters
    ----------
    url : str
        The url from which to calculate the length of the tld.

    Returns
    -------
    int
        The length of the tld.
    """
    # Get the domain name using urllib.parse
    parsed_url = urllib.parse.urlparse(url)
    # remove www. from the domain name
    net_loc = parsed_url.netloc.replace("www.", "")
    # Split the domain name by .
    net_loc_split = net_loc.split(".")

    if len(net_loc_split) == 0:
        raise ValueError(f"Could not parse the domain name from {url}")

    # If the length of the split is 1, then return 1
    if len(net_loc_split) == 1:
        return 1

    domains_allowing_ac = ["uk", "in", "jp", "cn", "nz", "kr"]

    # Now, check if it's one of co.uk, co.nz, co.in, etc.
    if net_loc_split[-2] in ["co", "com", "edu"]:
        # In this case, the geo tld is co.uk or com.au or co.in, etc.
        # This means it has length of 2
        return 2

    elif net_loc_split[-2] in ["ac"] and net_loc_split[-1] in domains_allowing_ac:
        # In this case, the geo tld is ac.uk or ac.in, etc.
        # So still length of 2
        return 2
    else:
        # In this case, the geo tld is uk or jp or in, etc.
        # This means it has length of 1
        return 1


def has_valid_tld(url: str) -> bool:
    """
    Given a url, check if it has a valid tld. If it does, return True, else False.

    Parameters
    ----------
    url : str
        The url to check.

    Returns
    -------
    bool
        True if the url has a valid tld, else False.
    """
    # If the length of the tld is 1, then it's valid
    # Get the domain name using urllib.parse
    parsed_url = urllib.parse.urlparse(url)
    # remove www. from the domain name
    net_loc = parsed_url.netloc.replace("www.", "")
    # Split the domain name by .
    net_loc_split = net_loc.split(".")

    if net_loc_split[-1] == "":
        return False

    if len(net_loc_split) == 1:
        return False  # No tld has length of 1

    if len(net_loc_split[-1]) > 1:
        return True
