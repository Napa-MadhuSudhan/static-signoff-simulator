# test1.py
from graphviz import Digraph
import os, subprocess, sys

# Circuit connections
inputs = ["A", "B", "C", "D"]
gates = [
    ("G1", "A", "B"),   # G1 = A AND B
    ("G2", "C", "D"),   # G2 = C AND D
    ("G3", "G1", "G2"), # Final AND
]
outputs = [("Y", "G3")]

# Output folder
os.makedirs("out", exist_ok=True)

g = Digraph("circuit", format="png")
g.attr(rankdir="LR", splines="ortho", nodesep="0.4", ranksep="0.7", fontsize="12")
g.attr("node", fontname="Helvetica", fontsize="12")

# Inputs — triangles
for i in inputs:
    g.node(i, label=i, shape="triangle", orientation="90", width="0.6", height="0.4")

# Gates — rectangles labeled only with "D"
for gate_name, *_ in gates:
    g.node(gate_name, label="D", shape="rectangle", width="0.8", height="0.5", style="rounded")

# Outputs — plain text box
for out_label, _ in outputs:
    g.node(out_label, label=out_label, shape="rectangle", width="0.6", height="0.4")

# Wires
for gate_name, *gate_inputs in gates:
    for src in gate_inputs:
        g.edge(src, gate_name, arrowsize="0.7")

for out_label, src in outputs:
    g.edge(src, out_label, arrowsize="0.7")

# Render and auto-open
out_path = g.render(filename="circuit", directory="out", cleanup=True)
abs_path = os.path.abspath(out_path)
print(f"✅ Generated: {abs_path}")
if sys.platform == "darwin":
    subprocess.run(["open", abs_path])
