# pygraphwiz_build.py
# Usage:
#   pip install graphviz
#   python3 pygraphwiz_build.py circuits.txt
#
# circuits.txt format (repeatable blocks; blank line between):
#   N
#   <node_id> <#inputs> <in1> <in2> ...
#   ... (N lines)

import os, sys, subprocess
from graphviz import Digraph
from collections import defaultdict

ASSETS_DIR = "assets"
OUT_DIR = "out"
AND_SVG = os.path.join(ASSETS_DIR, "and_gate.svg")
FORMAT = os.environ.get("PYGRAPHWIZ_FORMAT", "svg") 

AND_SVG_CONTENT = """<svg xmlns="http://www.w3.org/2000/svg" width="160" height="120" viewBox="0 0 160 120">
  <g fill="none" stroke="black" stroke-width="6">
    <path d="M20,20 L80,20"/><path d="M20,100 L80,100"/><path d="M20,20 L20,100"/>
    <path d="M80,20 A40,40 0 0,1 80,100"/>
    <path d="M120,60 L150,60"/>
  </g>
  <!-- input pins (just visual, edges will connect to image bbox) -->
  <g stroke="black" stroke-width="6"><path d="M-10,40 L20,40"/><path d="M-10,80 L20,80"/></g>
</svg>
"""

# add at top
from shutil import copy2
def ensure_assets():
    os.makedirs("assets", exist_ok=True)

def ensure_assets_out():
    os.makedirs(OUT_DIR, exist_ok=True)
    # copy and_gate.svg into out/ so the browser finds it
    dst = os.path.join(OUT_DIR, os.path.basename(AND_SVG))
    if not os.path.exists(dst):
        copy2(AND_SVG, dst)

def read_blocks(path):
    with open(path, "r") as f:
        lines = [ln.strip() for ln in f]
    blocks, i = [], 0
    n = len(lines)

    def skip_blanks(j):
        while j < n and lines[j] == "":
            j += 1
        return j

    while True:
        i = skip_blanks(i)
        if i >= n: break
        try:
            N = int(lines[i])
        except ValueError:
            raise ValueError(f"Expected N at line {i+1}, got {lines[i]!r}")
        i += 1
        defs = []
        for _ in range(N):
            i = skip_blanks(i)
            parts = lines[i].split()
            i += 1
            nid = int(parts[0]); k = int(parts[1]); parents = list(map(int, parts[2:2+k]))
            if len(parents) != k:
                raise ValueError(f"Node {nid}: declared {k} inputs, got {len(parents)}")
            defs.append((nid, parents))
        blocks.append(defs)
    return blocks

def build_maps(defs):
    parents = {nid: pr for nid, pr in defs}
    children = defaultdict(list)
    for nid, pr in defs:
        for p in pr:
            children[p].append(nid)
        children.setdefault(nid, children.get(nid, []))
    return parents, children

def levels(parents):
    from functools import lru_cache
    @lru_cache(None)
    def depth(n):
        ps = parents.get(n, [])
        if not ps: return 0
        return 1 + max(depth(p) for p in ps)
    lvl = {n: depth(n) for n in parents}
    layers = defaultdict(list)
    for n, d in lvl.items(): layers[d].append(n)
    for d in layers: layers[d].sort()
    return layers, max(layers.keys()), lvl

def var_labeler(inputs_sorted):
    # map 0-input node ids to A,B,C,... order by id
    labels = {}
    letters = [chr(ord('A')+i) for i in range(26)]
    for idx, nid in enumerate(inputs_sorted):
        labels[nid] = letters[idx] if idx < len(letters) else f"I{nid}"
    return labels

def render_block(defs, idx):
    parents, children = build_maps(defs)
    layers, maxlvl, lvl = levels(parents)
    inputs = sorted([n for n, pr in defs if len(parents.get(n, [])) == 0])
    sinks  = sorted([n for n, pr in defs if len(children.get(n, [])) == 0])
    input_name = var_labeler(inputs)

    g = Digraph(f"circuit_{idx}", format=FORMAT)
    g.attr(rankdir="LR", splines="ortho", nodesep="0.4", ranksep="0.8", fontsize="12")
    g.attr("node", fontname="Helvetica", fontsize="12")
    g.attr(imagepath=ASSETS_DIR)  # <-- tell dot where images live

    # Build nodes per level (same-rank subgraphs help alignment)
    for d in range(maxlvl+1):
        with g.subgraph(name=f"cluster_level_{d}") as s:
            s.attr(rank="same")
            for n in layers.get(d, []):
                k = len(parents.get(n, []))
                is_output = (k == 1 and len(children.get(n, [])) == 0)
                if k == 0:
                    s.node(f"n{n}", label=input_name[n], shape="triangle", orientation="90",
                           width="0.6", height="0.4")
                elif is_output:
                    s.node(f"n{n}", label=f"Y{n}", shape="rectangle", width="0.8", height="0.5")
                else:
                    # Use the AND gate image by basename; dot will look in imagepath
                    s.node(f"n{n}", label="", shape="none",
                    image=os.path.basename(AND_SVG),
                    imagescale="true", fixedsize="true", width="1.3", height="1.0")


    # Wires
    for n, pr in defs:
        for p in pr:
            g.edge(f"n{p}", f"n{n}", arrowsize="0.7")

    out_path = g.render(filename=f"block{idx}", directory=OUT_DIR, cleanup=True)
    return os.path.abspath(out_path)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pygraphwiz_build.py <circuits.txt>")
        sys.exit(1)
    ensure_assets_out()
    os.makedirs(OUT_DIR, exist_ok=True)
    ensure_assets_out()   # <-- add this line
    blocks = read_blocks(sys.argv[1])
    if not blocks:
        print("No circuits found.")
        return
    paths = []
    for i, defs in enumerate(blocks, 1):
        path = render_block(defs, i)
        print(f"[Block {i}] saved: {path}")
        paths.append(path)

    # macOS auto-open last image
    if sys.platform == "darwin" and paths:
        try: subprocess.run(["open", paths[-1]], check=False)
        except Exception: pass

if __name__ == "__main__":
    main()
