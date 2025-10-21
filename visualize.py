import pygraphviz as pgv
import pandas as pd

df = pd.read_csv("report.csv")
G = pgv.AGraph(strict=False, directed=True, rankdir="LR")
G.graph_attr.update(label="Static Sign-Off View", fontsize="20")

# cluster nodes by clock
clusters = {}
def get_cluster(clk):
    if clk not in clusters:
        c = pgv.AGraph(name=f"cluster_{clk}", label=clk)
        c.graph_attr.update(style="filled,rounded", color="lightgrey")
        clusters[clk] = c
    return clusters[clk]

for _, row in df.iterrows():
    for n, clk in [(row.Source, row.SrcClock), (row.Dest, row.DstClock)]:
        get_cluster(clk).add_node(n, shape="box")

for c in clusters.values():
    G.add_subgraph(c)

colors = {"Safe": "green", "Unsafe": "red", "OK": "black"}
for _, row in df.iterrows():
    G.add_edge(row.Source, row.Dest,
               color=colors.get(row.Status, "black"),
               label=f"{row.Type}:{row.Status}")

G.layout("dot")
G.draw("signoff_graph.png")
print("🖼  Diagram saved as signoff_graph.png")
