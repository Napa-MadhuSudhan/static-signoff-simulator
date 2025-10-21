# pygraphwiz_build.py
# Usage:
#   1. Create an 'assets' folder and place Dshape.png inside it.
#   2. pip install graphviz
#   3. python3 pygraphwiz_build.py circuits.txt

import os, sys, subprocess
from shutil import copy2
from collections import defaultdict
from graphviz import Digraph

ASSETS_DIR = "assets"
OUT_DIR = "out"
FORMAT = os.environ.get("PYGRAPHWIZ_FORMAT", "svg")  # "svg" or "png"

# 🌟 UPDATED: Use the correct PNG filename
AND_GATE_IMAGE = "/Users/madhusudhan/Desktop/Static-SignOff-Simulator/Dshape.png" 
AND_GATE_SRC_PATH = os.path.join(ASSETS_DIR, AND_GATE_IMAGE)

# --------------------------------------------------------------------
#  Asset preparation
# --------------------------------------------------------------------
def ensure_assets():
    """Create the assets folder and check for the Dshape.png file."""
    os.makedirs(ASSETS_DIR, exist_ok=True)
    if not os.path.exists(AND_GATE_SRC_PATH):
         print(f"Error: Required image '{AND_GATE_SRC_PATH}' not found.")
         print("Please place your Dshape.png file into the 'assets' directory.")
         sys.exit(1)

def ensure_assets_out():
    """Copy Dshape.png to out/ folder so Graphviz can find it."""
    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, os.path.basename(AND_GATE_SRC_PATH))
    # Ensure the file is copied or updated
    if not os.path.exists(dst) or os.path.getmtime(AND_GATE_SRC_PATH) > os.path.getmtime(dst):
        copy2(AND_GATE_SRC_PATH, dst)

# --------------------------------------------------------------------
#  Parsing & helpers
# --------------------------------------------------------------------
def read_blocks(path):
    """Read circuits.txt into list of blocks."""
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
        if i >= n:
            break
        N = int(lines[i]); i += 1
        defs = []
        for _ in range(N):
            i = skip_blanks(i)
            parts = lines[i].split(); i += 1
            nid = int(parts[0]); k = int(parts[1])
            parents = list(map(int, parts[2:2+k]))
            if len(parents) != k:
                raise ValueError(f"Node {nid}: declared {k} inputs, got {len(parents)}")
            defs.append((nid, parents))
        blocks.append(defs)
    return blocks

def build_maps(defs):
    """Create parent and child adjacency lists."""
    parents = {nid: pr for nid, pr in defs}
    children = defaultdict(list)
    for nid, pr in defs:
        for p in pr:
            children[p].append(nid)
        children.setdefault(nid, children.get(nid, []))
    return parents, children

def levels(parents):
    """Compute depth (rank) for each node."""
    from functools import lru_cache
    @lru_cache(None)
    def depth(n):
        ps = parents.get(n, [])
        if not ps: return 0
        return 1 + max(depth(p) for p in ps)
    lvl = {n: depth(n) for n in parents}
    layers = defaultdict(list)
    for n, d in lvl.items():
        layers[d].append(n)
    for d in layers:
        layers[d].sort()
    return layers, max(layers.keys()), lvl

def var_labeler(inputs_sorted):
    """Label input nodes as A,B,C,..."""
    labels = {}
    letters = [chr(ord('A') + i) for i in range(26)]
    for idx, nid in enumerate(inputs_sorted):
        labels[nid] = letters[idx] if idx < len(letters) else f"I{nid}"
    return labels

# --------------------------------------------------------------------
#  Render each circuit block (FIXED: Using Dshape.png with Absolute Path)
# --------------------------------------------------------------------
def render_block(defs, idx):
    parents, children = build_maps(defs)
    layers, maxlvl, _ = levels(parents)
    inputs = sorted([n for n, _ in defs if len(parents.get(n, [])) == 0])
    input_name = var_labeler(inputs)
    
    # 🌟 FIX: Calculate the ABSOLUTE path to the image file in the OUT_DIR
    and_gate_path_in_out = os.path.abspath(os.path.join(OUT_DIR, os.path.basename(AND_GATE_SRC_PATH)))

    g = Digraph(f"circuit_{idx}", format=FORMAT)
    g.attr(rankdir="LR", splines="ortho", nodesep="0.4", ranksep="0.8", fontsize="12")
    g.attr("node", fontname="Helvetica", fontsize="12")
    g.attr(imagepath=OUT_DIR)  # images resolved from out/

    for d in range(maxlvl + 1):
        with g.subgraph(name=f"cluster_level_{d}") as s:
            s.attr(rank="same")
            for n in sorted(layers.get(d, [])):
                k = len(parents.get(n, []))
                is_output = (k == 1 and len(children.get(n, [])) == 0)
                if k == 0:
                    # Input triangle (point right)
                    s.node(f"n{n}", label=input_name[n], shape="triangle", orientation="90",
                           width="0.6", height="0.4")
                elif is_output:
                    # Output triangle (also point right)
                    s.node(f"n{n}", label=f"Y{n}", shape="triangle", orientation="90",
                           width="0.6", height="0.4")
                else:
                    # AND gate (image)
                    s.node(f"n{n}", label="", shape="none",
                           # 🌟 USING ABSOLUTE PATH TO THE PNG IS THE FIX
                           image=and_gate_path_in_out,
                           imagescale="true", fixedsize="true",
                           width="1.3", height="1.0")

    # Wires
    for n, pr in defs:
        for p in pr:
            g.edge(f"n{p}", f"n{n}", arrowsize="0.7")

    out_path = g.render(filename=f"block{idx}", directory=OUT_DIR, cleanup=True)
    return os.path.abspath(out_path)

# --------------------------------------------------------------------
#  Entry point
# --------------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Usage: python3 pygraphwiz_build.py circuits.txt")
        sys.exit(1)

    # 1. Ensure assets are created and copied
    ensure_assets()
    os.makedirs(OUT_DIR, exist_ok=True)
    ensure_assets_out()

    blocks = read_blocks(sys.argv[1])
    if not blocks:
        print("No circuits found.")
        return

    paths = []
    for i, defs in enumerate(blocks, 1):
        path = render_block(defs, i)
        print(f"[Block {i}] saved: {path}")
        paths.append(path)

    # macOS auto-open last SVG
    if sys.platform == "darwin" and paths:
        try:
            subprocess.run(["open", paths[-1]], check=False)
        except Exception:
            pass

if __name__ == "__main__":
    main()