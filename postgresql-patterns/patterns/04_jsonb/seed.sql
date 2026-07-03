-- Seed products with varied JSONB metadata to exercise every operator.

INSERT INTO products (name, category, metadata) VALUES
  ('Mechanical Keyboard', 'peripherals', '{
      "brand": "Keychron",
      "switches": "brown",
      "wireless": true,
      "price_usd": 109.99,
      "tags": ["productivity", "mechanical"],
      "dimensions": {"width_cm": 35, "depth_cm": 12}
  }'),
  ('Noise-Cancelling Headphones', 'audio', '{
      "brand": "Sony",
      "model": "WH-1000XM5",
      "wireless": true,
      "price_usd": 349.00,
      "tags": ["travel", "focus"],
      "dimensions": {"weight_g": 250}
  }'),
  ('USB-C Hub', 'accessories', '{
      "brand": "Anker",
      "ports": 7,
      "wireless": false,
      "price_usd": 49.99,
      "tags": ["connectivity"],
      "dimensions": {"length_cm": 11}
  }'),
  ('Standing Desk Mat', 'furniture', '{
      "brand": "Topo",
      "material": "foam",
      "wireless": false,
      "price_usd": 99.00,
      "tags": ["ergonomics", "productivity"],
      "dimensions": {"width_cm": 76, "depth_cm": 53}
  }'),
  ('Webcam 4K', 'peripherals', '{
      "brand": "Logitech",
      "resolution": "4K",
      "wireless": false,
      "price_usd": 199.99,
      "tags": ["video", "remote-work"],
      "dimensions": {"weight_g": 345}
  }');
