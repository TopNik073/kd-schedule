CREATE OR REPLACE FUNCTION get_ip_part() RETURNS TEXT AS $$
	BEGIN
		RETURN floor(random() * 256)::text;
	END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION create_ip_address() RETURNS INET AS $$
	BEGIN
		RETURN (get_ip_part() || '.' || get_ip_part() || '.' || get_ip_part() || '.' || get_ip_part())::inet;
	END;
$$ LANGUAGE plpgsql;

INSERT INTO developers (name, department, geolocation, last_known_ip, is_available)
SELECT 
	(ARRAY['James', 'Mary', 'John', 'Patricia', 'Robert'])[floor(random() * 5) + 1] || ' ' ||
  (ARRAY['Smith', 'Johnson', 'Williams', 'Brown', 'Jones'])[floor(random() * 5) + 1] AS name,

	(ARRAY['backend', 'frontend', 'ios', 'android'])[floor(random() * 4) + 1] AS department,

	point(
        random() * 360 - 180,
        random() * 180 - 90
    ) AS geolocation,

	create_ip_address() AS last_known_ip,

	random() < 0.3 AS is_available
	
	FROM generate_series(1, 1000)