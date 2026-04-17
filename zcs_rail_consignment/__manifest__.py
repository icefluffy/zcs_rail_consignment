{
    "name": "Rail Consignment Validator",
    "version": "1.0",
    "category": "Inventory/Shipments",
    "summary": "Validate rail vehicles and containers identification numbers",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "data/rail_company_codes.csv",  # From PDF extracted CSV coming from uic.org
        "data/rail_company_data.xml",   # NEW to structure CSV data
        "views/rail_consignment_views.xml",
    ],
    "installable": True,
    "application": False,
}
