import os
import pandas as pd
import asyncpg


from const import DATABASE_URL

async def create_and_populate_airport_codes_table():
    conn = await asyncpg.connect(DATABASE_URL)
    

    # Create the airport_codes table if it doesn't exist
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS airport_codes (
        airport_name VARCHAR(255),
        city VARCHAR(100),
        state_ut VARCHAR(100),
        iata_code VARCHAR(10) PRIMARY KEY
    );
    """)

    # Load data from Excel file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "Deliva_db", "airport_codes.csv")
    data = pd.read_csv(file_path, encoding='latin1')

    # Insert data into the table
    for _, row in data.iterrows():
        await conn.execute("""
        INSERT INTO airport_codes (airport_name, city, state_ut, iata_code)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (iata_code) DO NOTHING;
        """, row['Airport'], row['City'], row['State / UT'], row['IATA Code'])

    await conn.close()


async def create_and_populate_booking_details_table():
    conn = await asyncpg.connect(DATABASE_URL)

    # Create the booking_details table if it doesn't exist
    await conn.execute("""
    CREATE TABLE IF NOT EXISTS booking_details (
        user_id VARCHAR PRIMARY KEY,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        phone_no VARCHAR NOT NULL,
        email_id VARCHAR NOT NULL
    );
    """)

    # Insert a sample row
    await conn.execute("""
    INSERT INTO booking_details (user_id, first_name, last_name, phone_no, email_id)
    VALUES ('User_1', 'Amith', 'Vinod', '1234567890', 'amith@example.com')
    ON CONFLICT (user_id) DO NOTHING;
    """)

    await conn.close()