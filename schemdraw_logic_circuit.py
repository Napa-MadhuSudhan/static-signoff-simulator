# pip install schemdraw pillow
import os, sys, subprocess
from schemdraw.parsing import logicparse

os.makedirs("out", exist_ok=True)

d = logicparse('((a xor b) and (b or c) and (d or e)) or ((w and x) or (y and z))',
               outlabel=r'$\overline{Q}$')   # optional output label

out_file = "out/logic_diagram.png"
d.save(out_file)     # PNG requires Pillow
print("Saved:", out_file)

# macOS: auto-open
if sys.platform == "darwin":
    subprocess.run(["open", out_file], check=False)
