"""Generate and validate the operational PostgreSQL logical and physical ERDs.

The physical metadata below is a faithful transcription of
platform/postgres/schema.sql.  The previews are rendered from the same model
that writes the editable Draw.io XML; they contain no embedded diagram image.
"""
from __future__ import annotations

from pathlib import Path
import json



OUT = Path(__file__).resolve().parent
FONT_DIR = Path("C:/Windows/Fonts")

TABLES = {
    "categories": [
        ("PK", "category_id", "bigint", "NN"),
        ("UK1", "category_name", "text", "NN"),
        ("FK/UK1", "parent_category_id", "bigint", "NULL"),
        ("", "description", "text", "NULL"),
    ],
    "brands": [
        ("PK", "brand_id", "bigint", "NN"), ("UK", "brand_name", "text", "NN"),
        ("", "manufacturer", "text", "NN"), ("", "partner_brand", "boolean", "NN DEFAULT false"),
        ("", "active", "boolean", "NN DEFAULT true"), ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"),
    ],
    "products": [
        ("PK", "product_id", "bigint", "NN"), ("FK", "category_id", "bigint", "NN"),
        ("FK/UK1", "brand_id", "bigint", "NN"), ("UK1", "product_name", "text", "NN"),
        ("", "description", "text", "NULL"), ("", "sugar_free", "boolean", "NN DEFAULT false"),
        ("", "active", "boolean", "NN DEFAULT true"), ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"),
    ],
    "skus": [
        ("PK", "sku_id", "bigint", "NN"), ("FK/UK2", "product_id", "bigint", "NN"),
        ("UK1", "sku_code", "text", "NN"), ("UK2", "flavor", "text", "NULL"),
        ("UK2", "package_type", "text", "NN"), ("UK2", "volume_ml", "integer", "NN"),
        ("", "units_per_case", "integer", "NN"), ("", "base_price", "numeric(12,2)", "NN"),
        ("", "standard_cost", "numeric(12,2)", "NN"), ("", "active", "boolean", "NN DEFAULT true"),
        ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"),
    ],
    "regions": [
        ("PK", "region_id", "bigint", "NN"), ("UK1", "region_name", "text", "NN"),
        ("UK1", "country", "text", "NN"),
    ],
    "stores": [
        ("PK", "store_id", "bigint", "NN"), ("UK", "external_store_code", "text", "NULL"),
        ("", "store_name", "text", "NN"), ("FK", "region_id", "bigint", "NN"),
        ("", "city", "text", "NN"), ("", "store_type", "text", "NN"),
        ("", "channel", "text", "NN"), ("", "floor_area_m2", "numeric(12,2)", "NULL"),
        ("", "active", "boolean", "NN DEFAULT true"), ("", "opened_at", "date", "NN"),
        ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"),
    ],
    "warehouses": [
        ("PK", "warehouse_id", "bigint", "NN"), ("UK", "warehouse_code", "text", "NN"),
        ("", "warehouse_name", "text", "NN"), ("FK", "region_id", "bigint", "NN"),
        ("", "city", "text", "NN"), ("", "capacity_units", "integer", "NULL"),
        ("", "active", "boolean", "NN DEFAULT true"),
    ],
    "promotions": [
        ("PK", "promotion_id", "bigint", "NN"), ("", "promotion_name", "text", "NN"),
        ("", "promotion_type", "text", "NN"), ("", "start_date", "date", "NN"),
        ("", "end_date", "date", "NN"), ("", "discount_type", "text", "NN"),
        ("", "discount_value", "numeric(12,2)", "NN"), ("", "description", "text", "NULL"),
        ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"),
    ],
    "promotion_skus": [("PK/FK", "promotion_id", "bigint", "NN"), ("PK/FK", "sku_id", "bigint", "NN")],
    "promotion_stores": [("PK/FK", "promotion_id", "bigint", "NN"), ("PK/FK", "store_id", "bigint", "NN")],
    "product_prices": [
        ("PK", "price_id", "bigint", "NN"), ("FK/UK1", "store_id", "bigint", "NN"),
        ("FK/UK1", "sku_id", "bigint", "NN"), ("UK1", "valid_from", "date", "NN"),
        ("", "valid_to", "date", "NN"), ("", "regular_price", "numeric(12,2)", "NN"),
        ("", "selling_price", "numeric(12,2)", "NN"), ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"),
    ],
    "orders": [
        ("PK", "order_id", "bigint", "NN"), ("UK", "order_code", "text", "NN"),
        ("FK", "store_id", "bigint", "NN"), ("", "order_date", "date", "NN"),
        ("", "requested_delivery_date", "date", "NN"), ("", "actual_delivery_date", "date", "NULL"),
        ("", "status", "order_status", "NN"), ("", "subtotal", "numeric(14,2)", "NN"),
        ("", "discount_amount", "numeric(14,2)", "NN"), ("", "total_amount", "numeric(14,2)", "NN"),
        ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"), ("", "external_source", "text", "NULL"),
        ("", "external_id", "text", "NULL"),
    ],
    "order_items": [
        ("PK", "order_item_id", "bigint", "NN"), ("FK/UK1", "order_id", "bigint", "NN"),
        ("FK/UK1", "sku_id", "bigint", "NN"), ("", "quantity", "integer", "NN"),
        ("", "unit_price", "numeric(12,2)", "NN"), ("", "discount_amount", "numeric(12,2)", "NN"),
        ("", "line_total", "numeric(14,2)", "GENERATED STORED"),
    ],
    "deliveries": [
        ("PK", "delivery_id", "bigint", "NN"), ("UK", "delivery_code", "text", "NN"),
        ("FK", "order_id", "bigint", "NULL"), ("FK", "warehouse_id", "bigint", "NN"),
        ("FK", "store_id", "bigint", "NN"), ("", "shipped_at", "timestamp", "NULL"),
        ("", "delivered_at", "timestamp", "NULL"), ("", "status", "delivery_status", "NN"),
    ],
    "delivery_items": [("PK/FK", "delivery_id", "bigint", "NN"), ("PK/FK", "sku_id", "bigint", "NN"), ("", "quantity", "integer", "NN")],
    "inventory": [
        ("PK", "inventory_id", "bigint", "NN"), ("UK1", "snapshot_date", "date", "NN"),
        ("FK/UK1", "warehouse_id", "bigint", "NN"), ("FK/UK1", "sku_id", "bigint", "NN"),
        ("", "opening_stock_quantity", "integer", "NN"), ("", "stock_quantity", "integer", "NN"),
        ("", "reserved_quantity", "integer", "NN"), ("", "available_quantity", "integer", "GENERATED STORED"),
        ("", "reorder_point", "integer", "NN"), ("", "safety_stock", "integer", "NN"),
        ("", "replenishment_quantity", "integer", "NN DEFAULT 0"), ("", "replenishment_ordered_quantity", "integer", "NN DEFAULT 0"),
        ("", "replenishment_lead_time_days", "integer", "NULL"), ("", "expected_replenishment_date", "date", "NULL"),
        ("", "demand_requested", "integer", "NN DEFAULT 0"), ("", "demand_fulfilled", "integer", "NN DEFAULT 0"),
        ("", "lost_sales_quantity", "integer", "NN DEFAULT 0"), ("", "adjustment_quantity", "integer", "NN DEFAULT 0"),
    ],
    "sales": [
        ("PK", "sale_id", "bigint", "NN"), ("UK1", "sale_date", "date", "NN"),
        ("FK/UK1", "store_id", "bigint", "NN"), ("FK/UK1", "sku_id", "bigint", "NN"),
        ("", "quantity_units", "integer", "NN"), ("", "unit_price", "numeric(12,2)", "NN"),
        ("", "gross_revenue", "numeric(14,2)", "NN"), ("", "discount_amount", "numeric(14,2)", "NN"),
        ("", "net_revenue", "numeric(14,2)", "NN"), ("", "unit_cost", "numeric(12,2)", "NN"),
        ("", "gross_profit", "numeric(14,2)", "NN"), ("FK", "promotion_id", "bigint", "NULL"),
        ("", "provenance", "provenance_kind", "NN DEFAULT synthetic"), ("", "external_source", "text", "NULL"),
        ("", "external_id", "text", "NULL"),
    ],
    "daily_demand": [
        ("PK", "demand_observation_id", "bigint", "NN"), ("UK1", "observation_date", "date", "NN"),
        ("FK/UK1", "store_id", "bigint", "NN"), ("FK/UK1", "sku_id", "bigint", "NN"),
        ("FK", "warehouse_id", "bigint", "NN"), ("", "requested_demand_units", "integer", "NN"),
        ("", "realized_sales_units", "integer", "NN"), ("", "lost_sales_units", "integer", "NN"),
        ("", "demand_censored_by_inventory", "boolean", "NN"), ("", "inventory_available_before", "integer", "NN"),
        ("FK", "promotion_id", "bigint", "NULL"),
    ],
}

# child, parent, child FK, optional child-to-parent
FKS = [
    ("categories", "categories", "parent_category_id", True),
    ("products", "categories", "category_id", False), ("products", "brands", "brand_id", False),
    ("skus", "products", "product_id", False), ("stores", "regions", "region_id", False),
    ("warehouses", "regions", "region_id", False),
    ("promotion_skus", "promotions", "promotion_id", False), ("promotion_skus", "skus", "sku_id", False),
    ("promotion_stores", "promotions", "promotion_id", False), ("promotion_stores", "stores", "store_id", False),
    ("product_prices", "stores", "store_id", False), ("product_prices", "skus", "sku_id", False),
    ("orders", "stores", "store_id", False), ("order_items", "orders", "order_id", False),
    ("order_items", "skus", "sku_id", False), ("deliveries", "orders", "order_id", True),
    ("deliveries", "warehouses", "warehouse_id", False), ("deliveries", "stores", "store_id", False),
    ("delivery_items", "deliveries", "delivery_id", False), ("delivery_items", "skus", "sku_id", False),
    ("inventory", "warehouses", "warehouse_id", False), ("inventory", "skus", "sku_id", False),
    ("sales", "stores", "store_id", False), ("sales", "skus", "sku_id", False),
    ("sales", "promotions", "promotion_id", True), ("daily_demand", "stores", "store_id", False),
    ("daily_demand", "skus", "sku_id", False), ("daily_demand", "warehouses", "warehouse_id", False),
    ("daily_demand", "promotions", "promotion_id", True),
]

CHECKS = {
    "skus": ["volume_ml > 0", "units_per_case > 0", "0 <= standard_cost <= base_price"],
    "promotions": ["end_date >= start_date", "discount percentage <= 100"],
    "product_prices": ["valid_to >= valid_from", "0 <= selling_price <= regular_price"],
    "orders": ["delivery dates >= order_date", "total_amount = subtotal - discount_amount"],
    "order_items": ["quantity > 0", "line_total >= 0"],
    "deliveries": ["delivered_at >= shipped_at when both set"],
    "delivery_items": ["quantity > 0"],
    "inventory": ["non-negative stock/demand fields", "requested = fulfilled + lost", "stock flow reconciliation"],
    "sales": ["net_revenue = gross_revenue - discount", "gross_profit = net_revenue - quantity * cost"],
    "daily_demand": ["requested = realized + lost", "censored = (lost > 0)"],
}

LOGICAL = {
    "Category": ["Category ID", "Name", "Parent Category", "Description"],
    "Brand": ["Brand ID", "Name", "Manufacturer", "Partner Brand", "Active"],
    "Product": ["Product ID", "Name", "Category", "Brand", "Sugar Free", "Active"],
    "SKU": ["SKU ID", "SKU Code", "Flavor", "Package / Volume", "Case Size", "Base Price", "Standard Cost"],
    "Region": ["Region ID", "Name", "Country"],
    "Store": ["Store ID", "External Code", "Name", "City", "Type / Channel", "Opened Date"],
    "Warehouse": ["Warehouse ID", "Code", "Name", "City", "Capacity", "Active"],
    "Promotion": ["Promotion ID", "Name", "Type", "Date Range", "Discount"],
    "Product Price": ["Price ID", "Effective Period", "Regular Price", "Selling Price"],
    "Order": ["Order ID", "Order Code", "Order / Delivery Dates", "Status", "Amounts"],
    "Order Item": ["Order Item ID", "Quantity", "Unit Price", "Discount", "Line Total"],
    "Delivery": ["Delivery ID", "Delivery Code", "Shipment Times", "Status"],
    "Delivery Item": ["Quantity"],
    "Inventory Snapshot": ["Inventory ID", "Snapshot Date", "Stock / Reserved / Available", "Reorder / Safety Stock", "Replenishment", "Demand / Lost Sales"],
    "Sale": ["Sale ID", "Sale Date", "Quantity", "Price / Cost", "Revenue / Profit", "Applied Promotion"],
    "Demand Observation": ["Observation ID", "Date", "Requested / Realized / Lost", "Inventory Before", "Inventory Censored", "Applied Promotion"],
}

LOGICAL_LINKS = [
    ("Category", "Category", "parent of", "0..1", "0..N"), ("Category", "Product", "classifies", "1", "0..N"),
    ("Brand", "Product", "owns", "1", "0..N"), ("Product", "SKU", "offered as", "1", "0..N"),
    ("Region", "Store", "contains", "1", "0..N"), ("Region", "Warehouse", "contains", "1", "0..N"),
    ("Promotion", "SKU", "eligible", "0..N", "0..N"), ("Promotion", "Store", "eligible", "0..N", "0..N"),
    ("Store", "Product Price", "sets", "1", "0..N"), ("SKU", "Product Price", "priced by", "1", "0..N"),
    ("Store", "Order", "places", "1", "0..N"), ("Order", "Order Item", "contains", "1", "0..N"),
    ("SKU", "Order Item", "ordered as", "1", "0..N"), ("Order", "Delivery", "fulfilled by", "0..1", "0..N"),
    ("Warehouse", "Delivery", "dispatches", "1", "0..N"), ("Store", "Delivery", "receives", "1", "0..N"),
    ("Delivery", "Delivery Item", "contains", "1", "0..N"), ("SKU", "Delivery Item", "delivered as", "1", "0..N"),
    ("Warehouse", "Inventory Snapshot", "holds", "1", "0..N"), ("SKU", "Inventory Snapshot", "counted in", "1", "0..N"),
    ("Store", "Sale", "records", "1", "0..N"), ("SKU", "Sale", "sold as", "1", "0..N"),
    ("Promotion", "Sale", "applied to", "0..1", "0..N"), ("Store", "Demand Observation", "observes", "1", "0..N"),
    ("SKU", "Demand Observation", "demanded as", "1", "0..N"), ("Warehouse", "Demand Observation", "supplies", "1", "0..N"),
    ("Promotion", "Demand Observation", "associated with", "0..1", "0..N"),
]



def main():
    from audit_schema import audit
    from erd_layout import logical, physical
    model=audit()
    assert set(TABLES)==set(model['tables'])
    actual_fks=[]
    for name,t in model['tables'].items():
        assert [(n,typ) for _,n,typ,_ in TABLES[name]]==[(c['name'],c['type']) for c in t['columns']],name
        assert set(t['primary_key'])=={n for key,n,_,_ in TABLES[name] if 'PK' in key},name
        for c,(_,n,_,null) in zip(t['columns'],TABLES[name]):
            assert c['nullable']==('NN' not in null),(name,n)
        actual_fks.extend((name,f['parent'],f['column'],f['optional']) for f in t['foreign_keys'])
    assert set(actual_fks)==set(FKS)
    assert len(actual_fks)==29
    results=[logical(LOGICAL,LOGICAL_LINKS),physical(model)]
    report={'source_of_truth':model['source'],'schema_sha256':model['sha256'],
        'schema_table_column_type_PK_FK_nullability_match':'PASS',
        'physical_tables':18,'columns':model['counts']['columns'],'foreign_keys':29,
        'unique_constraints':model['counts']['unique_constraints'],'check_constraints':model['counts']['checks'],
        'logical_entities':16,'logical_relationships':27,'logical_junctions_collapsed':['promotion_skus','promotion_stores'],
        'nullable_foreign_keys':[f'{n}.{f["column"]}' for n,t in model['tables'].items() for f in t['foreign_keys'] if f['optional']],
        'streaming_schema_excluded':list(model['technical_tables_excluded']),
        'warehouse_models_excluded':True,'live_database_mutations':False,'documents':results}
    (OUT/'fmcg_erd_validation.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
