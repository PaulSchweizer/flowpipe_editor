import imp
import inspect
import textwrap
import os

import flowpipe.node


NODE_PATHS = [
    os.path.join(os.path.dirname(__file__), "nodes")
]


def dedent_doc(doc):
    lines = doc.split("\n")
    return "{0}\n{1}".format(lines[0], textwrap.dedent("\n".join(lines[1:])))


def discover_nodes(paths=NODE_PATHS):
    nodes = []
    for path in paths:
        path = os.path.normpath(path)
        if not os.path.isdir(path):
            continue

        for fname in os.listdir(path):
            if fname.startswith("_"):
                continue

            abspath = os.path.join(path, fname)

            if not os.path.isfile(abspath):
                continue

            mod_name, mod_ext = os.path.splitext(fname)

            if not mod_ext == ".py":
                continue

            module = imp.load_source(mod_name, abspath)

            for node in _nodes_from_module(module):
                if inspect.isclass(node):
                    nodes.append({
                        "name": node.__name__,
                        "file": node.__module__,
                        "node": node
                    })
                else:
                    nodes.append({
                        "name": node.name,
                        "file": module.__file__,
                        "node": node
                    })
    return nodes


def _nodes_from_module(module):
    nodes = []

    for name in dir(module):

        if name.startswith("_"):
            continue

        # It could be anything at this point
        obj = getattr(module, name)

        if not callable(obj):
            continue
        if not issubclass(obj, flowpipe.node.INode) and not issubclass(type(obj), flowpipe.node.FunctionNode):
            continue
        if obj == flowpipe.node.INode:
            continue
        nodes.append(obj)

    return nodes
