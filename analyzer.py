import json, pandas as pd

with open("example_design.json") as f:
    design = json.load(f)

nodes = {n["name"]: n for n in design["nodes"]}
edges = design["edges"]
sync_pairs = {(s["src"], s["dst"]) for s in design["synchronizers"]}

records = []
for e in edges:
    src, dst = e["src"], e["dst"]
    sclk, dclk = nodes[src]["clock"], nodes[dst]["clock"]
    srst, drst = nodes[src]["reset"], nodes[dst]["reset"]

    if sclk != dclk:
        if (src, dst) in sync_pairs:
            status, typ = "Safe", "CDC"
        else:
            status, typ = "Unsafe", "CDC"
    elif srst != drst:
        status, typ = "Unsafe", "RDC"
    else:
        status, typ = "OK", "Intra-domain"

    records.append({
        "Source": src, "Dest": dst,
        "SrcClock": sclk, "DstClock": dclk,
        "SrcReset": srst, "DstReset": drst,
        "Type": typ, "Status": status
    })

df = pd.DataFrame(records)
df.to_csv("report.csv", index=False)
print(df)
print("\n✅ Report written to report.csv")
