import re
import pandas as pd
import json
from openpyxl.utils import get_column_letter

INPUT  = "toexcel.txt"
OUTPUT = "entities_with_attributes1.xlsx"
JSON_OUTPUT = "entities.json"

def parse_entities(txt):
    lines = [l.rstrip() for l in txt.splitlines()]
    blocks, current = [], []
    for line in lines:
        if re.match(r"^[a-z_]+?\.[a-z0-9_]+", line) and current:
            blocks.append(current); current = [line]
        else:
            if line or current:
                current.append(line)
    if current:
        blocks.append(current)

    out = []
    for blk in blocks:
        ent = {"Entity ID": blk[0], "Friendly Name": blk[1] if len(blk)>1 else ""}
        for ln in blk[2:]:
            if ":" in ln:
                k, v = ln.split(":",1)
                ent[k.strip()] = v.strip()
        out.append(ent)
    return out

def main():
    txt = open(INPUT, encoding="utf-8").read()
    entities = parse_entities(txt)
    df  = pd.DataFrame(entities)
    df["Domain"] = df["Entity ID"].str.split(pat=".", n=1).str[0]

    # Save as JSON for frontend use
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(entities, f, ensure_ascii=False, indent=2)

    with pd.ExcelWriter(OUTPUT, engine="openpyxl") as writer:
        for domain, group in df.groupby("Domain"):
            sheet = domain[:31]
            sub = group.drop(columns="Domain").sort_values("Entity ID")
            sub.to_excel(writer, sheet_name=sheet, index=False)

            ws = writer.book[sheet]
            # verberg kolommen waar ALLE waarden NaN zijn
            for idx, col in enumerate(sub.columns, start=1):
                if sub[col].isna().all():
                    ws.column_dimensions[get_column_letter(idx)].hidden = True

    print(f"Klaar: {OUTPUT} en {JSON_OUTPUT}")

if __name__ == "__main__":
    main()