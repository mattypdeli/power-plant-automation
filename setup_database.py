import sqlite3
import os

DB_FILE = "erp_database.db"

# Delete the old database file if it exists
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

# Connect to the SQLite database (this will create the file)
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# --- Create Tables ---

# Power Plants (Customers)
cursor.execute('''
CREATE TABLE power_plants (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT,
    capacity_mw REAL
)
''')

# Equipment
cursor.execute('''
CREATE TABLE equipment (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    manufacturer TEXT,
    type TEXT -- e.g., Turbine, Generator, Transformer
)
''')

# Bids
cursor.execute('''
CREATE TABLE bids (
    id INTEGER PRIMARY KEY,
    plant_id INTEGER,
    bid_date TEXT,
    bid_amount REAL,
    status TEXT, -- e.g., Won, Lost, Pending
    FOREIGN KEY (plant_id) REFERENCES power_plants (id)
)
''')

# Bid Items (linking Bids and Equipment)
cursor.execute('''
CREATE TABLE bid_items (
    bid_id INTEGER,
    equipment_id INTEGER,
    quantity INTEGER,
    price_per_unit REAL,
    FOREIGN KEY (bid_id) REFERENCES bids (id),
    FOREIGN KEY (equipment_id) REFERENCES equipment (id),
    PRIMARY KEY (bid_id, equipment_id)
)
''')


# --- Insert Mock Data ---

# Power Plants
cursor.execute("INSERT INTO power_plants (name, location, capacity_mw) VALUES ('Riverbend Generating Station', 'North Carolina, USA', 1200)")
cursor.execute("INSERT INTO power_plants (name, location, capacity_mw) VALUES ('Midlands Power Plant', 'Lincolnshire, UK', 850)")
cursor.execute("INSERT INTO power_plants (name, location, capacity_mw) VALUES ('Gascoyne Power Facility', 'Western Australia', 240)")

# Equipment
cursor.execute("INSERT INTO equipment (name, manufacturer, type) VALUES ('GE 7HA.02 Gas Turbine', 'General Electric', 'Turbine')")
cursor.execute("INSERT INTO equipment (name, manufacturer, type) VALUES ('Siemens SGT-800', 'Siemens Energy', 'Turbine')")
cursor.execute("INSERT INTO equipment (name, manufacturer, type) VALUES ('ABB Pro-Gen 5000', 'ABB', 'Generator')")
cursor.execute("INSERT INTO equipment (name, manufacturer, type) VALUES ('WEG Main Transformer', 'WEG S.A.', 'Transformer')")

# Bids
cursor.execute("INSERT INTO bids (plant_id, bid_date, bid_amount, status) VALUES (1, '2024-05-15', 750000.00, 'Won')")
cursor.execute("INSERT INTO bids (plant_id, bid_date, bid_amount, status) VALUES (2, '2024-06-01', 120000.00, 'Pending')")
cursor.execute("INSERT INTO bids (plant_id, bid_date, bid_amount, status) VALUES (1, '2024-06-20', 45000.50, 'Pending')")


# Bid Items
# Bid 1 for Riverbend
cursor.execute("INSERT INTO bid_items (bid_id, equipment_id, quantity, price_per_unit) VALUES (1, 1, 1, 650000.00)") # GE Turbine
cursor.execute("INSERT INTO bid_items (bid_id, equipment_id, quantity, price_per_unit) VALUES (1, 3, 1, 100000.00)") # ABB Generator

# Bid 2 for Midlands
cursor.execute("INSERT INTO bid_items (bid_id, equipment_id, quantity, price_per_unit) VALUES (2, 2, 2, 60000.00)") # 2x Siemens Turbines

# Bid 3 for Riverbend
cursor.execute("INSERT INTO bid_items (bid_id, equipment_id, quantity, price_per_unit) VALUES (3, 4, 1, 45000.50)") # WEG Transformer

# Commit the changes and close the connection
conn.commit()
conn.close()

print(f"Database '{DB_FILE}' created successfully with mock data.")