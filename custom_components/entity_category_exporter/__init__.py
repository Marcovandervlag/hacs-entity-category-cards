import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType
import os
import pandas as pd
import json
from openpyxl.utils import get_column_letter

DOMAIN = "entity_category_exporter"

CONFIG_SCHEMA = vol.Schema({}, extra=vol.ALLOW_EXTRA)

INPUT_FILE = "toexcel.txt"
OUTPUT_XLSX = "entities_with_attributes1.xlsx"
OUTPUT_JSON = "entities.json"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async def handle_export(call: ServiceCall):
        base = hass.config.path()
        input_path = os.path.join(base, INPUT_FILE)
        xlsx_path = os.path.join(base, OUTPUT_XLSX)
        json_path = os.path.join(base, OUTPUT_JSON)
        if not os.path.exists(input_path):
            logging.error(f"Input file {input_path} not found.")
            return
        with open(input_path, encoding="utf-8") as f:
            txt = f.read()
        entities = parse_entities(txt)
        df = pd.DataFrame(entities)
        df["Domain"] = df["Entity ID"].str.split(pat=".", n=1).str[0]
        with open(json_path, "w", encoding="utf-8") as fjson:
            json.dump(entities, fjson, ensure_ascii=False, indent=2)
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            for domain, group in df.groupby("Domain"):
                sheet = domain[:31]
                sub = group.drop(columns="Domain").sort_values("Entity ID")
                sub.to_excel(writer, sheet_name=sheet, index=False)
                ws = writer.book[sheet]
                for idx, col in enumerate(sub.columns, start=1):
                    if sub[col].isna().all():
                        ws.column_dimensions[get_column_letter(idx)].hidden = True
        logging.info(f"Entity export done: {xlsx_path} and {json_path}")

    def parse_entities(txt):
        import re
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

    hass.services.async_register(DOMAIN, "export_entities", handle_export)
    return True
