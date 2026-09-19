SET search_path TO fmcg, public;
INSERT INTO categories(category_name, description) VALUES
 ('Carbonated Soft Drinks','Synthetic portfolio category'),('Energy Drinks','Synthetic portfolio category'),
 ('Juice','Synthetic portfolio category'),('Water','Synthetic portfolio category'),
 ('RTD Tea','Synthetic portfolio category'),('Coffee','Synthetic portfolio category');
INSERT INTO brands(brand_name,manufacturer,partner_brand,provenance) VALUES
 ('Northstar Cola','FMCG Demo Company',false,'synthetic'),('Volt','FMCG Demo Company',false,'synthetic'),
 ('Orchard','FMCG Demo Company',false,'synthetic'),('ClearSpring','FMCG Demo Company',false,'synthetic'),
 ('Leafline','FMCG Demo Company',false,'synthetic'),('RoastGo','FMCG Demo Company',false,'synthetic');

