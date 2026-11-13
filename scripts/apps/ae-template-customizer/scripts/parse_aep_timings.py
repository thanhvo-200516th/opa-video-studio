import re
import sys

REPORT_PATH = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Public\OPA-AE-20261021\T5-REPORT-DECODED.txt"
MASTER_COMP = sys.argv[2] if len(sys.argv) > 2 else "Final_4k (3840 x 2160)"

with open(REPORT_PATH, "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

comps = {}
cur_comp = None
cur_layer = None
for line in lines:
    line_s = line.rstrip("\r\n")
    if line_s.startswith("COMP\t"):
        parts = line_s.split("\t")
        cid = parts[1]
        cname = parts[2]
        dur = float(parts[5].split("=")[1])
        fps = float(parts[6].split("=")[1])
        comps[cname] = {"id": cid, "name": cname, "dur": dur, "fps": fps, "layers": []}
        cur_comp = comps[cname]
        cur_layer = None
    elif line_s.startswith("  LAYER\t") and cur_comp is not None:
        parts = line_s.split("\t")
        lidx = int(parts[1])
        ltype = parts[2]
        lname = parts[3]
        src = parts[4].split("=")[1].split("#")[0]
        en = parts[5].split("=")[1] == "true"
        inp = float(parts[7].split("=")[1])
        outp = float(parts[8].split("=")[1])
        st = float(parts[9].split("=")[1])
        cur_layer = {
            "idx": lidx,
            "type": ltype,
            "name": lname,
            "src": src,
            "en": en,
            "in": inp,
            "out": outp,
            "st": st,
            "props": [],
        }
        cur_comp["layers"].append(cur_layer)
    elif line_s.startswith("    ") and cur_layer is not None:
        if "keys=" in line_s and "keys=0" not in line_s:
            cur_layer["props"].append(line_s.strip())


def shift_keys(prop_str, offset, fps=30.0):
    def repl(m):
        t = float(m.group(1))
        gt = t + offset
        gf = int(round(gt * fps))
        return f"{gt:.2f}s(f{gf},loc={t:.2f}s):"

    return re.sub(r"(-?\d+\.\d+)s:", repl, prop_str)


final = comps[MASTER_COMP]
fps = final["fps"]
print(f"=== {MASTER_COMP} SCENE TIMINGS ({fps:.0f} fps, dur={final['dur']:.2f}s) ===")
for l in sorted(final["layers"], key=lambda x: x["in"]):
    if l["en"] and "_Scene" in l["name"]:
        sname = l["name"]
        s_in = l["in"]
        s_out = l["out"]
        s_st = l["st"]
        print("\n==========================================")
        print(
            f">>> {sname}: Global IN={s_in:.2f}s (f{int(round(s_in*fps))}) -> OUT={s_out:.2f}s (f{int(round(s_out*fps))}), ST={s_st:.2f}s"
        )
        sc = comps.get(sname)
        if sc:
            for sl in sc["layers"]:
                g_in = s_st + sl["in"]
                g_out = s_st + sl["out"]
                g_st = s_st + sl["st"]
                print(
                    f"  L{sl['idx']} [{sl['type']}] {sl['name']} (src={sl['src']}) en={sl['en']} | GLOBAL in={g_in:.2f}s(f{int(round(g_in*fps))})..{g_out:.2f}s(f{int(round(g_out*fps))}), st={g_st:.2f}s"
                )
                for p in sl["props"]:
                    print(f"      {shift_keys(p, s_st, fps)}")
                sub = comps.get(sl["src"])
                if sub and sub["name"] not in ["Camera_Control"]:
                    for subl in sub["layers"]:
                        if subl["props"] or subl["src"] in comps:
                            sg_in = g_st + subl["in"]
                            sg_out = g_st + subl["out"]
                            sg_st = g_st + subl["st"]
                            print(
                                f"      -> SUB {sub['name']} / L{subl['idx']} {subl['name']} (src={subl['src']}) | GLOBAL in={sg_in:.2f}s(f{int(round(sg_in*fps))})..{sg_out:.2f}s"
                            )
                            for sp in subl["props"]:
                                print(f"          {shift_keys(sp, g_st, fps)}")
                            sub2 = comps.get(subl["src"])
                            if sub2:
                                for sub2l in sub2["layers"]:
                                    if sub2l["props"]:
                                        print(f"          --> SUB2 {sub2['name']} / L{sub2l['idx']} {sub2l['name']}")
                                        for s2p in sub2l["props"]:
                                            print(f"              {shift_keys(s2p, sg_st, fps)}")
