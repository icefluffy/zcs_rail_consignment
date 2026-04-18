{
    "name": "Rail Consignment Validator",
    "version": "1.0",
    "category": "Inventory/Shipments",
    "summary": "Validate rail vehicles and containers identification numbers",
    "depends": ["base"],
    "data": [
        "data/rail_company_code.csv",  # From PDF extracted CSV coming from uic.org        
        "security/ir.model.access.csv",
        "views/rail_consignment_views.xml",
    ],
    "installable": True,
    "application": False,
}
