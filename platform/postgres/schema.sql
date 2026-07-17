CREATE SCHEMA IF NOT EXISTS fmcg;
SET search_path TO fmcg, public;

CREATE TYPE provenance_kind AS ENUM ('public_factual','transformed_external','synthetic');
CREATE TYPE order_status AS ENUM ('created','confirmed','shipped','delivered','cancelled');
CREATE TYPE delivery_status AS ENUM ('planned','shipped','delivered','failed','cancelled');

CREATE TABLE categories (
 category_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 category_name text NOT NULL,
 parent_category_id bigint REFERENCES categories(category_id),
 description text,
 UNIQUE (category_name, parent_category_id)
);
CREATE TABLE brands (
 brand_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 brand_name text NOT NULL UNIQUE, manufacturer text NOT NULL,
 partner_brand boolean NOT NULL DEFAULT false, active boolean NOT NULL DEFAULT true,
 provenance provenance_kind NOT NULL DEFAULT 'synthetic'
);
CREATE TABLE products (
 product_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 category_id bigint NOT NULL REFERENCES categories(category_id),
 brand_id bigint NOT NULL REFERENCES brands(brand_id),
 product_name text NOT NULL, description text,
 sugar_free boolean NOT NULL DEFAULT false, active boolean NOT NULL DEFAULT true,
 provenance provenance_kind NOT NULL DEFAULT 'synthetic',
 UNIQUE (brand_id, product_name)
);
CREATE TABLE skus (
 sku_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 product_id bigint NOT NULL REFERENCES products(product_id),
 sku_code text NOT NULL UNIQUE, flavor text, package_type text NOT NULL,
 volume_ml integer NOT NULL CHECK (volume_ml > 0),
 units_per_case integer NOT NULL CHECK (units_per_case > 0),
 base_price numeric(12,2) NOT NULL CHECK (base_price >= 0),
 standard_cost numeric(12,2) NOT NULL CHECK (standard_cost >= 0 AND standard_cost <= base_price),
 active boolean NOT NULL DEFAULT true, provenance provenance_kind NOT NULL DEFAULT 'synthetic',
 UNIQUE(product_id, package_type, volume_ml, flavor)
);
CREATE TABLE regions (
 region_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 region_name text NOT NULL, country text NOT NULL,
 UNIQUE(country, region_name)
);
CREATE TABLE stores (
 store_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 external_store_code text UNIQUE, store_name text NOT NULL,
 region_id bigint NOT NULL REFERENCES regions(region_id), city text NOT NULL,
 store_type text NOT NULL, channel text NOT NULL,
 floor_area_m2 numeric(12,2) CHECK (floor_area_m2 > 0),
 active boolean NOT NULL DEFAULT true, opened_at date NOT NULL,
 provenance provenance_kind NOT NULL DEFAULT 'synthetic'
);
CREATE TABLE warehouses (
 warehouse_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 warehouse_code text NOT NULL UNIQUE, warehouse_name text NOT NULL,
 region_id bigint NOT NULL REFERENCES regions(region_id), city text NOT NULL,
 capacity_units integer CHECK(capacity_units > 0), active boolean NOT NULL DEFAULT true
);
CREATE TABLE promotions (
 promotion_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 promotion_name text NOT NULL, promotion_type text NOT NULL,
 start_date date NOT NULL, end_date date NOT NULL CHECK(end_date >= start_date),
 discount_type text NOT NULL CHECK(discount_type IN ('percentage','fixed')),
 discount_value numeric(12,2) NOT NULL CHECK(discount_value >= 0 AND (discount_type <> 'percentage' OR discount_value <= 100)), description text,
 provenance provenance_kind NOT NULL DEFAULT 'synthetic'
);
CREATE TABLE promotion_skus (
 promotion_id bigint REFERENCES promotions(promotion_id) ON DELETE CASCADE,
 sku_id bigint REFERENCES skus(sku_id) ON DELETE CASCADE,
 PRIMARY KEY(promotion_id, sku_id)
);
CREATE TABLE promotion_stores (
 promotion_id bigint REFERENCES promotions(promotion_id) ON DELETE CASCADE,
 store_id bigint REFERENCES stores(store_id) ON DELETE CASCADE,
 PRIMARY KEY(promotion_id, store_id)
);
CREATE TABLE product_prices (
 price_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 store_id bigint NOT NULL REFERENCES stores(store_id), sku_id bigint NOT NULL REFERENCES skus(sku_id),
 valid_from date NOT NULL, valid_to date NOT NULL CHECK(valid_to >= valid_from),
 regular_price numeric(12,2) NOT NULL CHECK(regular_price >= 0),
 selling_price numeric(12,2) NOT NULL CHECK(selling_price >= 0 AND selling_price <= regular_price),
 provenance provenance_kind NOT NULL DEFAULT 'synthetic',
 UNIQUE(store_id, sku_id, valid_from)
);
CREATE TABLE orders (
 order_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 order_code text NOT NULL UNIQUE, store_id bigint NOT NULL REFERENCES stores(store_id),
 order_date date NOT NULL, requested_delivery_date date NOT NULL CHECK(requested_delivery_date >= order_date),
 actual_delivery_date date CHECK(actual_delivery_date IS NULL OR actual_delivery_date >= order_date), status order_status NOT NULL,
 subtotal numeric(14,2) NOT NULL CHECK(subtotal >= 0),
 discount_amount numeric(14,2) NOT NULL CHECK(discount_amount >= 0 AND discount_amount <= subtotal),
 total_amount numeric(14,2) NOT NULL CHECK(total_amount = subtotal - discount_amount),
 provenance provenance_kind NOT NULL DEFAULT 'synthetic', external_source text, external_id text
);
CREATE TABLE order_items (
 order_item_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 order_id bigint NOT NULL REFERENCES orders(order_id) ON DELETE CASCADE,
 sku_id bigint NOT NULL REFERENCES skus(sku_id), quantity integer NOT NULL CHECK(quantity > 0),
 unit_price numeric(12,2) NOT NULL CHECK(unit_price >= 0),
 discount_amount numeric(12,2) NOT NULL CHECK(discount_amount >= 0 AND discount_amount <= quantity * unit_price),
 line_total numeric(14,2) GENERATED ALWAYS AS ((quantity * unit_price) - discount_amount) STORED CHECK(line_total >= 0),
 UNIQUE(order_id, sku_id)
);
CREATE TABLE deliveries (
 delivery_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 delivery_code text NOT NULL UNIQUE, order_id bigint REFERENCES orders(order_id),
 warehouse_id bigint NOT NULL REFERENCES warehouses(warehouse_id), store_id bigint NOT NULL REFERENCES stores(store_id),
 shipped_at timestamp, delivered_at timestamp CHECK(delivered_at IS NULL OR shipped_at IS NULL OR delivered_at >= shipped_at),
 status delivery_status NOT NULL
);
CREATE TABLE delivery_items (
 delivery_id bigint REFERENCES deliveries(delivery_id) ON DELETE CASCADE,
 sku_id bigint REFERENCES skus(sku_id), quantity integer NOT NULL CHECK(quantity > 0),
 PRIMARY KEY(delivery_id, sku_id)
);
CREATE TABLE inventory (
 inventory_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 snapshot_date date NOT NULL, warehouse_id bigint NOT NULL REFERENCES warehouses(warehouse_id),
 sku_id bigint NOT NULL REFERENCES skus(sku_id), opening_stock_quantity integer NOT NULL CHECK(opening_stock_quantity >= 0), stock_quantity integer NOT NULL CHECK(stock_quantity >= 0),
 reserved_quantity integer NOT NULL CHECK(reserved_quantity >= 0 AND reserved_quantity <= stock_quantity),
 available_quantity integer GENERATED ALWAYS AS (stock_quantity - reserved_quantity) STORED,
 reorder_point integer NOT NULL CHECK(reorder_point >= 0), safety_stock integer NOT NULL CHECK(safety_stock >= 0),
 replenishment_quantity integer NOT NULL DEFAULT 0 CHECK(replenishment_quantity >= 0),
 replenishment_ordered_quantity integer NOT NULL DEFAULT 0 CHECK(replenishment_ordered_quantity >= 0),
 replenishment_lead_time_days integer CHECK(replenishment_lead_time_days > 0), expected_replenishment_date date,
 demand_requested integer NOT NULL DEFAULT 0 CHECK(demand_requested >= 0),
 demand_fulfilled integer NOT NULL DEFAULT 0 CHECK(demand_fulfilled >= 0),
 lost_sales_quantity integer NOT NULL DEFAULT 0 CHECK(lost_sales_quantity >= 0),
 adjustment_quantity integer NOT NULL DEFAULT 0,
 CHECK(demand_requested = demand_fulfilled + lost_sales_quantity),
 CHECK(stock_quantity = opening_stock_quantity + replenishment_quantity - demand_fulfilled + adjustment_quantity),
 UNIQUE(snapshot_date, warehouse_id, sku_id)
);
CREATE TABLE sales (
 sale_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 sale_date date NOT NULL, store_id bigint NOT NULL REFERENCES stores(store_id), sku_id bigint NOT NULL REFERENCES skus(sku_id),
 quantity_units integer NOT NULL CHECK(quantity_units >= 0), unit_price numeric(12,2) NOT NULL CHECK(unit_price >= 0),
 gross_revenue numeric(14,2) NOT NULL CHECK(gross_revenue >= 0), discount_amount numeric(14,2) NOT NULL CHECK(discount_amount >= 0 AND discount_amount <= gross_revenue),
 net_revenue numeric(14,2) NOT NULL CHECK(net_revenue = gross_revenue - discount_amount),
 unit_cost numeric(12,2) NOT NULL CHECK(unit_cost >= 0),
 gross_profit numeric(14,2) NOT NULL CHECK(gross_profit = net_revenue - quantity_units * unit_cost),
 promotion_id bigint REFERENCES promotions(promotion_id),
 provenance provenance_kind NOT NULL DEFAULT 'synthetic', external_source text, external_id text,
 UNIQUE(sale_date, store_id, sku_id)
);
CREATE TABLE daily_demand (
 demand_observation_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 observation_date date NOT NULL, store_id bigint NOT NULL REFERENCES stores(store_id),
 sku_id bigint NOT NULL REFERENCES skus(sku_id), warehouse_id bigint NOT NULL REFERENCES warehouses(warehouse_id),
 requested_demand_units integer NOT NULL CHECK(requested_demand_units >= 0),
 realized_sales_units integer NOT NULL CHECK(realized_sales_units >= 0),
 lost_sales_units integer NOT NULL CHECK(lost_sales_units >= 0),
 demand_censored_by_inventory boolean NOT NULL,
 inventory_available_before integer NOT NULL CHECK(inventory_available_before >= 0),
 promotion_id bigint REFERENCES promotions(promotion_id),
 CHECK(requested_demand_units = realized_sales_units + lost_sales_units),
 CHECK(demand_censored_by_inventory = (lost_sales_units > 0)),
 UNIQUE(observation_date, store_id, sku_id)
);
