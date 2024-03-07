import glob
import json
import ast
from textwrap import dedent

from pathlib import Path

def keep_front_matter(content):
    """
    This function keeps the front matter of a markdown file. We will keep everything
    between the first two "---" delimiters (or any length greater than 2).
    """
    # Find the first two delimiters
    first_delim = content.find("---")

    if first_delim == -1:
        return ""
    
    second_delim = content.find("---", first_delim + 1)

    if second_delim == -1:
        return ""

    # Now, we keep everything between the first two delimiters
    front_matter = content[first_delim:second_delim + 3]
    return front_matter + "\n"

def recursive_infer_attribute_ast(obj: ast.Attribute):
    lst = []

    while isinstance(obj, ast.Attribute):
        lst.append(obj.attr)
        obj = obj.value

    lst.append(obj.id)
    return reversed(lst)


def get_default(obj):
    if isinstance(obj, ast.Num):
        return obj.n
    if isinstance(obj, ast.Str):
        # First, need to ensure that the string's \n and \t are properly escaped
        obj.s = obj.s.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")
        return f'"{obj.s}"'
    if isinstance(obj, ast.NameConstant):
        return str(obj.value)
    elif isinstance(obj, ast.Name):
        return obj
    elif isinstance(obj, ast.Attribute):
        ".".join(recursive_infer_attribute_ast(obj))
    elif isinstance(obj, ast.Tuple):
        return tuple(get_default(e) for e in obj.elts)
    # Handle ast.Call
    elif isinstance(obj, ast.Call):
        return get_default(obj.func) 
    # handle ast.List
    elif isinstance(obj, ast.List):
        return [get_default(e) for e in obj.elts]
    else:
        raise ValueError(f"Unexpected default value: {obj}")


def line_is_delim(i, lines, delim="-"):
    if i == len(lines):
        return False
    return lines[i].startswith(delim) and all(c == delim for c in lines[i])


def extract_content_from_ast(node: ast.FunctionDef, remove_self=False):
    """
    This extracts the information from a function or method definition node in the AST.

    It returns a dictionary with the following keys:
    - docstring: the docstring of the function/method
    - args: a dictionary where the keys are the names of the arguments and the values are:
        - name: the name of the argument
        - type: the type of the argument
        - default: the default value of the argument
    """
    docstring = ast.get_docstring(node, clean=True)

    arg_list = []
    for arg in node.args.args:
        annot = arg.annotation
        if hasattr(annot, "id"):
            type_ = arg.annotation.id
        elif hasattr(annot, "s"):
            type_ = arg.annotation.s
        elif annot is None:
            type_ = None
        elif isinstance(annot, ast.Attribute):
            type_ = ".".join(recursive_infer_attribute_ast(annot))
        elif isinstance(annot, ast.Subscript):
            type_ = ".".join(recursive_infer_attribute_ast(annot.value))
        else:
            raise AttributeError(f"No annotations for {arg.annotation}")

        arg_list.append({"name": arg.arg, "type": type_})

    defaults = [get_default(arg) for arg in node.args.defaults]
    defaults = [None] * (len(arg_list) - len(defaults)) + defaults

    for arg, default in zip(arg_list, defaults):
        arg["default"] = default

    args = {arg["name"]: arg for arg in arg_list}

    if remove_self:
        args.pop("self")

    return {"docstring": docstring, "args": args}


def parse_docstring(content: str, parse_params=True, parse_returns=True):
    """
    This parses a docstring formatted using the pandas docstring format.
    """
    lines = content.splitlines()
    key = "Description"
    content = {key: []}

    for i, line in enumerate(lines):
        if line_is_delim(i + 1, lines):
            key = line
            content[key] = []
        elif not line_is_delim(i, lines):
            content[key].append(line)

    if parse_params and "Parameters" in content:
        content["Parameters"] = parse_docstring_params(content["Parameters"])

    if parse_returns and "Returns" in content:
        content["Returns"] = parse_docstring_params(content["Returns"])

    return content


def infer_default_in_description(line: str):
    """
    This function tries to infer the default value from the description
    of a parameter.
    """
    line = line.replace(",optional", ", optional").replace(",default", ", default")
    default = None

    if line.endswith(", optional"):
        line = line.replace(", optional", "").strip()

    elif "default" in line:
        line, default = line.split(", default", maxsplit=1)
        line = line.strip()
        default = default.strip()

    return line, default


def parse_docstring_params(lines: "list[str]"):
    """
    This parses a docstring formatted using the pandas docstring format.
    """
    params = {}
    varname = None

    for line in lines:
        if line == "":
            continue

        if line.startswith(" "):
            if varname is None:
                raise ValueError("Unexpected line in docstring: " + line)
            params[varname]["description"].append(line)

        else:
            if ":" in line:
                varname, line = line.split(":", maxsplit=1)
                varname = varname.strip()
                line = line.strip()
                type_name, default = infer_default_in_description(line)

            else:
                type_name = None
                varname, default = infer_default_in_description(line)

            params[varname] = {"type": type_name, "default": default, "description": []}

    for key, value in params.items():
        params[key]["description"] = dedent("\n".join(value["description"]))

    return params


def param_dict_to_markdown_table(params: dict, args: dict):
    """
    This converts the output of parse_docstring_params to a markdown table.
    """
    markdown = ""
    markdown += "| Name | Type | Default | Description |\n"
    markdown += "| ---- | ---- | ------- | ----------- |\n"

    for varname, p in params.items():
        type_ = p["type"]
        default = p["default"]
        description = p["description"].replace("\n", " ")
        try:
            sig_type_ = args[varname]["type"]
        except:
            breakpoint()
        sig_default = args[varname]["default"]

        if type_ is None and sig_type_ is not None:
            type_ = sig_type_
        elif sig_type_ is not None and type_ != sig_type_:
            type_ += f" ({sig_type_})"

        if default is None and sig_default is not None:
            default = sig_default
        elif sig_default is not None and default != sig_default:
            default += f" ({sig_default})"

        if type_ is None:
            type_ = ""
        else:
            type_ = f"`{type_}`"

        if default is None:
            default = ""
        else:
            default = f"`{default}`"

        markdown += f"| `{varname}` | {type_} | {default} | {description} |\n"

    return markdown


def md_header(text, level):
    return "#" * level + f" {text}\n\n"


def signature_list_from_args(args):
    signature = []
    for name in args:
        if args[name]["default"] is not None:
            signature.append(f"{name}={args[name]['default']}")
        else:
            signature.append(f"{name}")
    return signature


def format_docstring_to_markdown(
    node_content: dict, node_name, module_prefix=None, level=3
):
    """
    Formats the content of a node extracted from extract_information
    with the docstring parsed by parse_docstring.
    """

    if node_name is None:
        node_name = node_content["name"]

    if module_prefix is not None and module_prefix != "":
        full_node_name = module_prefix + "." + node_name

    doc_str_dict = node_content["docstring"]
    args = node_content["args"]
    signature_lst = signature_list_from_args(args)

    markdown = md_header(f"`{node_name}`", level=level)
    markdown += f"```\n{full_node_name}({', '.join(signature_lst)})\n```\n\n"

    if doc_str_dict is None:
        return markdown

    for key, value in doc_str_dict.items():
        markdown += md_header(key, level=max(4, level + 1))

        if key == "Parameters":
            markdown += param_dict_to_markdown_table(value, args)

        elif key == "Returns":
            if len(value) == 1:
                k, v = list(value.items())[0]
                markdown += f"```\n{k}\n```\n\n{v['description']}"
            else:
                markdown += param_dict_to_markdown_table(value, args)

        elif key == "Examples":
            markdown += "```\n"
            markdown += "\n".join(value)
            markdown += "\n```\n\n"

        elif isinstance(value, str):
            markdown += value

        elif isinstance(value, list):
            markdown += "\n".join(value)

        else:
            raise ValueError(f"Unexpected value for key {key}: {value}")

        markdown += "\n\n"

    return markdown


def format_module_from_content(node_contents: dict, module_prefix: str = None):
    formatted_page = ""

    if module_prefix is not None:
        formatted_page += md_header(f"Reference for `{module_prefix}`", level=2)

    for name, node_content in node_contents.items():
        if node_content["docstring"] is not None:
            node_content["docstring"] = parse_docstring(node_content["docstring"])

        if "class" in node_content and node_content["class"] != name:
            level = 4
        else:
            level = 3

        formatted = format_docstring_to_markdown(
            node_content, node_name=name, module_prefix=module_prefix, level=level
        )
        formatted_page += formatted

    return formatted_page


def parse_content_from_ast(tree: ast.Module) -> dict:
    node_contents = {}

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            name = node.name
            if node.name.startswith("_"):
                continue

            node_contents[name] = extract_content_from_ast(node)

        if isinstance(node, ast.ClassDef):
            cls_ = node
            for node in cls_.body:
                if not isinstance(node, ast.FunctionDef):
                    continue

                if node.name.startswith("_") and not node.name.endswith("__"):
                    continue

                if node.name == "__init__":
                    name = cls_.name
                    remove_self = True
                else:
                    name = f"{cls_.name}.{node.name}"
                    remove_self = False

                node_contents[name] = extract_content_from_ast(
                    node, remove_self=remove_self
                )
                node_contents[name]["class"] = cls_.name

    return node_contents


def build_globed_sources(sources):
    sources_globed = []
    for s in sources:
        sources_globed.extend(glob.glob(s))
    sources_globed = sorted(sources_globed)
    return sources_globed


def build_docs(sources_globed):
    doc_page = ""

    for source in sources_globed:
        source = Path(source)
        with open(source, "r") as f:
            tree = ast.parse(f.read())

        node_contents = parse_content_from_ast(tree)
        module_prefix = (
            ".".join(source.parts).replace(".py", "").replace(".__init__", "")
        )
        doc_page_part = format_module_from_content(
            node_contents, module_prefix=module_prefix
        )
        doc_page += doc_page_part

    return doc_page


if __name__ == "__main__":
    cur_dir = Path(__file__).parent
    with open(cur_dir / "render_paths.json", "r") as f:
        render_paths = json.load(f)

    for target, source_lst in render_paths.items():
        target = Path(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        sources_globed = build_globed_sources(source_lst)

        print("Target doc file:", target)
        print("Parsing python files:", sources_globed)
        print("-" * 50)

        doc_page = build_docs(sources_globed)

        # First, we keep the front matter of the target file
        with open(target, "r") as f:
            target_content = f.read()
        front_matter = keep_front_matter(target_content)
        
        # Now, we write the new content to the target file
        doc_page = front_matter + doc_page

        with open(target, "w") as f:
            f.write(doc_page)
