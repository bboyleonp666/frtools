import os
import json
import pickle
import argparse
import networkx as nx

import r2pipe


class FCGParser:
    def __init__(self, path, flags=[], tmpdir='tmp/'):
        self.path   = path
        self.name   = os.path.splitext(os.path.basename(path))[0]
        self.flags  = flags
        self.tmpdir = tmpdir
        os.makedirs(tmpdir, exist_ok=True)

        self.r2 = r2pipe.open(self.path, flags=self.flags)
        self.r2.cmd('aaa')
    
    def parse(self):
        edges = self.edges()
        nodes = self.nodes()

        fcg = self.to_networkx(nodes, edges)
        return fcg
        
    def edges(self):
        fcg = self.r2.cmdj('agCj')
        edge_pairs = []
        for call in fcg:
            src = call['name']
            for tgt in call['imports']:
                edge_pairs.append([src, tgt])
        return edge_pairs
    
    def nodes(self):
        asmpath = os.path.join(self.tmpdir, self.name) + '_asm'
        self.r2.cmdj('pifj @@f > ' + asmpath)

        with open(asmpath, 'r') as asmfile:
            functions = [json.loads(line) for line in asmfile]

        blocks = []
        for func in functions:
            func_name = func['name']
            asm = [[ops['offset'], ops['disasm']] for ops in func['ops']]
            blocks.append({'bName': func_name, 'x': asm})
        
        os.remove(asmpath)
        return blocks
    
    def to_networkx(self, nodes, edges):
        attrs = {node['bName']: node for node in nodes}

        G = nx.DiGraph()
        G.add_nodes_from(attrs.keys())
        G.add_edges_from(edges)
        nx.set_node_attributes(G, attrs)

        ## remove nodes that do not match
        # Some nodes such as
        # 
        #   {'unk.0x38': {}, 'rflags': {}}
        #
        # do not match when building a graph (inconsistence between
        # node attributes & edge pairs), so remove them iteratively.
        for node, attrs in dict(G.nodes(data=True)).items():
            if attrs == {}:
                G.remove_node(node)
        
        return G


def read_pickle(path):
    with open(path, 'rb') as f:
        output = pickle.load(f)
    return output


def write_pickle(obj, path):
    with open(path, 'wb') as f:
        pickle.dump(obj, f)


def parse_args():
    parser = argparse.ArgumentParser(description='FCGParser')
    parser.add_argument('-f', '--file-path', type=str, required=True, metavar='<path>', 
                        help='path to the binary file')
    parser.add_argument('-o', '--output-dir', type=str, required=False, default='FCGs/', metavar='<directory>', 
                        help='directory to save FCG files')
    args = parser.parse_args()

    return args


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    parser = FCGParser(path=args.file_path)
    fcg = parser.parse()
    
    dump_path = os.path.join(args.output_dir, os.path.basename(args.file_path)) + '.pickle'
    write_pickle(obj=fcg, path=dump_path)


if __name__ == '__main__':
    main()