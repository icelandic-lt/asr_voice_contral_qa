import itertools
import os
import openfst_python as fst
from string import Formatter
from itertools import product
from collections import defaultdict, namedtuple
from random import random


def load_variables(fname, source=""):
    if isinstance(fname, list):
        return [str(i) for i in fname]
    else:
        with open(os.path.join(source, fname), "r") as f:
            return [line.strip() for line in f]



def get_tokens(pattern):
    format_tokens = Formatter().parse(pattern)
    for token in format_tokens:
        if token[0] != "":
            yield token[0]
        if token[1]:
            yield token[1]


def create_sentence(f, start, sentences, sentence, variable_nodes, tokenmap):
    one = fst.Weight.One(f.weight_type())
    end = f.add_state()
    for pattern in sentences[sentence]:
        tokens = list(get_tokens(pattern))
        nodes = [start]
        for token in tokens:
            if token in sentences:
                current_node = create_sentence(f, nodes[-1], sentences, token, variable_nodes, tokenmap)
                nodes.append(current_node)
            else:
                nodes.append(f.add_state())
                for symbol in variable_nodes[token]:
                    f.add_arc(nodes[-2], fst.Arc(tokenmap[symbol], tokenmap[symbol], one, nodes[-1]))
        f.add_arc(nodes[-1], fst.Arc(0, 0, one, end))
    return end


def create_fst(variables, sentences, output):
    f = fst.Fst()
    s0 = f.add_state()  # Start state

    ist = fst.SymbolTable()
    ost = fst.SymbolTable()
    ist.add_symbol("<eps>")
    ost.add_symbol("<eps>")

    # Create all the nodes for the variables
    variable_nodes = defaultdict(list)

    for variable, fname in variables.items():
        for token in load_variables(fname):
            variable_nodes[variable].append(token)
    for sentence in sentences.values():
        for pattern in sentence:
            for token in get_tokens(pattern):
                if token not in variable_nodes:
                    variable_nodes[token].append(token)

    tokens = set(itertools.chain.from_iterable(variable_nodes.values()))
    tokenmap = {"<esp>": 0}
    for i, token in enumerate(tokens):
        token_id = i + 1
        tokenmap[token] = token_id
        ist.add_symbol(token, token_id)
        ost.add_symbol(token, token_id)

    one = fst.Weight.One(f.weight_type())
    current_node = s0
    current_node = create_sentence(f, current_node, sentences, output, variable_nodes, tokenmap)

    f.set_start(s0)
    f.set_final(current_node, one)
    f.set_input_symbols(ist)
    f.set_output_symbols(ost)

    return f, ist, ost


def generate(f, n=10):
    for _ in range(n):
        g = fst.randgen(f, 1, seed=random()*n*n)
        g = [l.split("\t") for l in str(g).split("\n")]
        print("".join([t[3] for t in g if len(t) == 4 and t[3] != "<eps>"]))