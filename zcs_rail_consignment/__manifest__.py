{
    "name": "Rail Consignment Validator",
    "version": "1.0",
    "category": "Inventory/Shipments",
    "summary": "Validate rail vehicles and containers identification numbers",
    "depends": ["base"],
    "data": [        
        "security/ir.model.access.csv",
        "views/rail_consignment_views.xml",
    ],
    "post_init_hook": "post_init_load_rail_company_codes",
    "installable": True,
    "application": False,
}
