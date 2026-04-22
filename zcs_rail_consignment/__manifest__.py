{
    "name": "Rail Consignment Validator",
    "summary": "Validate rail vehicles and containers identification numbers",
    "version": "18.0.1.0",
    "category": "Field Service",
    "author": "IceFluffy & Sebas",
    "website": "https://github.com/icefluffy/zcs_rail_consignment/",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/rail_uic_wagon_views.xml",
        "views/menu.xml",
    ],
    "post_init_hook": "post_init_load_rail_company_codes",
    "installable": True,
    "application": True,
}
