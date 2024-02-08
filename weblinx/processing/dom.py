# Some imports for type checking
from copy import deepcopy
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import lxml.html


def get_tree_repr_simple(
    tree: "lxml.html.HtmlElement",
    keep_html_brackets=False,
    copy=True,
    postfix="\nAbove are the pruned HTML contents of the page.",
):
    """
    This will return a simple representation of the tree in a string format.
    This is useful if you want to pass the tree to a action model like a LLM, which
    can only accept strings (and images in the case of multimodal models).

    Parameters
    ----------
    tree : lxml.html.HtmlElement
        The tree to get the representation of.
    keep_html_brackets : bool, optional
        Whether to keep the HTML brackets or not. Defaults to False.
    copy : bool, optional
        Whether to copy the tree or not. Defaults to True.
    postfix : str, optional
        A string to append to the end of the tree representation. Defaults to "\nAbove are the pruned HTML contents of the page.".

    Returns
    -------
    str
        The string representation of the tree.

    Raises
    ------
    ImportError
        If the lxml library is not installed.

    Note
    ----
    This function is based on the works of Mind2Web (@xiang-deng). Copyrights belong
    to the original author. The original code can be found here at osu-nlp-group/mind2web
    """
    try:
        import lxml.html
    except ImportError:
        raise ImportError("Please install lxml to use this function")

    if tree is None:
        return None

    if copy:
        tree = deepcopy(tree)

    tree_repr = lxml.html.tostring(tree, encoding="unicode")
    # tree_repr = tree_repr.replace('"', " ")
    tree_repr = re.sub(r"<text>(.*?)</text>", r"\1", tree_repr)
    if not keep_html_brackets:
        tree_repr = tree_repr.replace("/>", "$/$>")
        tree_repr = re.sub(r"</(.+?)>", r")", tree_repr)
        tree_repr = re.sub(r"<(.+?)>", r"(\1", tree_repr)
        tree_repr = tree_repr.replace("$/$", ")")
    html_escape_table = [
        ("&quot;", '"'),
        ("&amp;", "&"),
        ("&lt;", "<"),
        ("&gt;", ">"),
        ("&nbsp;", " "),
        ("&ndash;", "-"),
        ("&rsquo;", "'"),
        ("&lsquo;", "'"),
        ("&ldquo;", '"'),
        ("&rdquo;", '"'),
        ("&#39;", "'"),
        ("&#40;", "("),
        ("&#41;", ")"),
    ]
    for k, v in html_escape_table:
        tree_repr = tree_repr.replace(k, v)
    tree_repr = re.sub(r"\s+", " ", tree_repr).strip()

    # Replace all whitespace bewtween two ) ) with no space
    tree_repr = re.sub(r"\) +\)", r"))", tree_repr)
    # Replace all whitespace bewtween two ( ( with no space
    tree_repr = re.sub(r"\( +\(", r"((", tree_repr)

    if postfix is not None:
        tree_repr = tree_repr + postfix
    return tree_repr


def sanitize_elem_attributes(
    tree: "lxml.html.HtmlElement",
    remove_data_attrs=True,
    remove_underscore_attrs=True,
    remove_angular_attrs=True,
    remove_alpine_attrs=True,
    remove_xml_attrs=True,
    remove_google_attrs=True,
    remove_id_attrs=True,
    uid_key="data-webtasks-id",
):
    """
    This will take a tree and sanitize the attributes of the elements.
    This is needed in order to remove any attributes that are not needed before the
    element selection stage of the ranking model.

    Parameters
    ----------
    tree : lxml.html.HtmlElement
        The tree to sanitize.

    remove_data_attrs : bool, optional
        Whether to remove data- attributes or not. Defaults to True.

    remove_underscore_attrs : bool, optional
        Whether to remove _ attributes or not. Defaults to True.

    remove_angular_attrs : bool, optional
        Whether to remove ng attributes or not. Defaults to True.

    remove_alpine_attrs : bool, optional
        Whether to remove x- attributes or not. Defaults to True.

    remove_xml_attrs : bool, optional
        Whether to remove xml attributes or not. Defaults to True.

    remove_google_attrs : bool, optional
        Whether to remove js attributes or not. Defaults to True.

    remove_id_attrs : bool, optional
        Whether to remove id attributes or not. Defaults to True.

    uid_key : str, optional
        The key to use as the unique identifier. Defaults to "data-webtasks-id".

    Raises
    ------
    ImportError
        If the lxml library is not installed.
    """
    for node in tree.iter():
        if node.attrib is None:
            continue

        for k, v in node.attrib.items():
            if remove_underscore_attrs and k.startswith("_"):
                node.attrib.pop(k)

            if remove_angular_attrs and k.startswith("ng"):
                node.attrib.pop(k)

            if remove_alpine_attrs and k.startswith("x-"):
                node.attrib.pop(k)

            if remove_xml_attrs and k.startswith("xml"):
                node.attrib.pop(k)

            if remove_google_attrs and k.startswith("js"):
                node.attrib.pop(k)

            if k == uid_key:
                continue

            if remove_data_attrs and k.startswith("data-"):
                node.attrib.pop(k)

            if remove_id_attrs and k == "id":
                node.attrib.pop(k)


def remove_uid_when_not_candidate(dom_tree, candidate_uids, uid_key="data-webtasks-id"):
    """
    This will remove the uid from the tree if it is not in the candidate_uids. This is
    useful for removing any uids that are not in the candidate set.

    Parameters
    ----------
    dom_tree : lxml.html.HtmlElement
        The tree to remove the uids from.

    candidate_uids : list
        The list of candidate uids to keep.

    uid_key : str, optional
        The key to use as the unique identifier. Defaults to "data-webtasks-id".

    Raises
    ------
    ImportError
        If the lxml library is not installed.
    """
    candidate_uids = set(candidate_uids)
    for node in dom_tree.iter():
        if node.attrib is None:
            continue

        if uid_key in node.attrib and node.attrib[uid_key] not in candidate_uids:
            node.attrib.pop(uid_key)


def remove_html_comments(dom_tree):
    """
    Will try to remove all HTML comments from the tree.

    Parameters
    ----------
    dom_tree : lxml.html.HtmlElement
        The tree to remove the comments from.

    """
    try:
        import lxml.html
    except ImportError:
        raise ImportError("Please install lxml to use this function")

    for node in dom_tree.iter():
        if isinstance(node, lxml.html.HtmlComment):
            node.drop_tree()
            continue


def get_descendants(node, max_depth, current_depth=0):
    """
    This function was originally written by @xiang-deng for the [mind2web repository](https://github.com/OSU-NLP-Group/Mind2Web/blob/3740087ab004fe98a117f6261cb1937dfc9fa66e/src/data_utils/dom_utils.py)

    It is kept as is and added here for convenience. All copyrights belong to the original author.
    """
    if current_depth > max_depth:
        return []

    descendants = []
    for child in node:
        descendants.append(child)
        descendants.extend(get_descendants(child, max_depth, current_depth + 1))

    return descendants


def prune_tree(
    dom_tree: "lxml.html.HtmlElement",
    candidate_set,
    max_depth=5,
    max_children=50,
    max_sibling=3,
    uid_key="data-webtasks-id",
):
    """
    This function was originally written by @xiang-deng for the [mind2web repository](https://github.com/OSU-NLP-Group/Mind2Web/blob/3740087ab004fe98a117f6261cb1937dfc9fa66e/src/data_utils/dom_utils.py#L203)

    It was modified to allow uid_key to be specified. All rights belong to the original author.
    """
    nodes_to_keep = set()
    for candidate_id in candidate_set:
        try:
            xpath = dom_tree.xpath(f'//*[@{uid_key}="{candidate_id}"]')
        except:
            continue

        # If len(xpath) == 0, then the candidate node is not in the tree
        # So we skip it
        if len(xpath) <= 0:
            continue

        candidate_node = xpath[0]
        nodes_to_keep.add(candidate_node.attrib[uid_key])
        # get all ancestors
        nodes_to_keep.update(
            [x.attrib.get(uid_key, "") for x in candidate_node.xpath("ancestor::*")]
        )
        # get descendants with max depth
        nodes_to_keep.update(
            [
                x.attrib.get(uid_key, "")
                for x in get_descendants(candidate_node, max_depth)
            ][:max_children]
        )
        # get siblings within range
        parent = candidate_node.getparent()
        if parent is not None:
            siblings = [x for x in parent.getchildren() if x.tag != "text"]
            if candidate_node not in siblings:
                continue

            idx_in_sibling = siblings.index(candidate_node)
            nodes_to_keep.update(
                [
                    x.attrib.get(uid_key, "")
                    for x in siblings[
                        max(0, idx_in_sibling - max_sibling) : idx_in_sibling
                        + max_sibling
                        + 1
                    ]
                ]
            )
    # clone the tree
    new_tree = deepcopy(dom_tree)
    # remove nodes not in nodes_to_keep
    for node in new_tree.xpath("//*")[::-1]:
        node: "lxml.html.HtmlElement"

        if node.tag != "text":
            is_keep = node.attrib.get(uid_key, "") in nodes_to_keep
            is_candidate = node.attrib.get(uid_key, "") in candidate_set
        else:
            is_keep = node.getparent().attrib.get(uid_key, "") in nodes_to_keep
            is_candidate = node.getparent().attrib.get(uid_key, "") in candidate_set
        if not is_keep and node.getparent() is not None:
            node.getparent().remove(node)
        else:
            if not is_candidate or node.tag == "text":
                node.attrib.pop(uid_key, None)
            if (
                len(node.attrib) == 0
                and not any([x.tag == "text" for x in node.getchildren()])
                and node.getparent() is not None
                and node.tag != "text"
                and len(node.getchildren()) <= 1
            ):
                # insert all children into parent
                for child in node.getchildren():
                    node.addprevious(child)
                node.getparent().remove(node)
    return new_tree


def clean_and_prune_tree(
    dom_tree, cands_turn, max_depth=1, max_children=5, max_sibling=2
):
    """
    This function will clean and prune the tree based on the candidates in the cands_turn. This
    is useful for removing any elements that are not candidates, and for removing any elements
    that are not needed for the ranking model.

    Parameters
    ----------
    dom_tree : lxml.html.HtmlElement
        The tree to clean and prune.

    cands_turn : list
        The list of candidates for the turn.

    max_depth : int, optional
        The maximum depth to prune the tree. Defaults to 1.

    max_children : int, optional
        The maximum number of children to keep for each candidate. Defaults to 5.

    max_sibling : int, optional
        The maximum number of siblings to keep for each candidate. Defaults to 2.

    Returns
    -------
    lxml.html.HtmlElement
        The cleaned and pruned tree.

    Raises
    ------
    ValueError
        If cands_turn is None.
    """
    if cands_turn is None:
        raise ValueError(
            "cands_turn cannot be None. The dom_tree cannot be pruned this way."
        )

    if cands_turn is not None:
        candidate_uids = [cand["uid"] for cand in cands_turn]
        dom_tree = prune_tree(
            dom_tree,
            set(candidate_uids),
            max_depth=max_depth,
            max_children=max_children,
            max_sibling=max_sibling,
        )
        remove_uid_when_not_candidate(dom_tree, candidate_uids=candidate_uids)

    remove_html_comments(dom_tree)
    sanitize_elem_attributes(dom_tree)

    return dom_tree
