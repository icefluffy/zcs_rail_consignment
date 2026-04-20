# -*- coding: utf-8 -*-
import csv
import os

from odoo.modules.module import get_module_resource


def post_init_load_rail_company_codes(env):
    CompanyCode = env["rail.company.code"]

    csv_path = get_module_resource(
        "zcs_rail_consignment",
        "data",
        "rail_company_code.csv",
    )

    if not csv_path or not os.path.exists(csv_path):
        return

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            code = (row.get("code") or "").strip()
            if not code:
                continue

            existing = CompanyCode.search([("code", "=", code)], limit=1)
            vals = {
                "code": code,
                "short_name": (row.get("short_name") or "").strip(),
                "full_name": (row.get("full_name") or "").strip(),
                "country": (row.get("country") or "").strip(),
                "date1": (row.get("date1") or "").strip(),
                "date2": (row.get("date2") or "").strip(),
                "url": (row.get("url") or "").strip(),
            }

            if existing:
                existing.write(vals)
            else:
                CompanyCode.create(vals)
