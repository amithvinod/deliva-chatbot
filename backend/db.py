from datetime import datetime, timezone
import asyncpg
from const import DATABASE_URL
async def userDetails_to_db(details):
    fname = details["first_name"]
    lname = details["last_name"]
    phone_no = details["phone_no"]
    email_id = details["email_id"]
    
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Get the next user ID
        row_count = await conn.fetchval("SELECT COUNT(*) FROM booking_details;")
        user_id = f"User_{row_count + 1}"

        sql = """
        INSERT INTO booking_details (user_id, first_name, last_name, phone_no, email_id)
        VALUES ($1, $2, $3, $4, $5);
        """
        
        await conn.execute(sql, user_id, fname, lname, phone_no, email_id)
        return True, "success"
    except Exception as e:
        return False, str(e)
    finally:
        await conn.close()



async def create_temp_booking_table():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS temp_bookings (
                booking_id SERIAL PRIMARY KEY,
                flight_number VARCHAR(10) NOT NULL,
                passenger_count INT,
                from_airport VARCHAR(100),
                to_airport VARCHAR(100),
                departure_time TIMESTAMPTZ,
                arrival_time TIMESTAMPTZ,
                duration VARCHAR(20),
                price DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
    finally:
        await conn.close()



   
async def add_temp_booking(flight_number,passenger_count, from_airport, to_airport, departure_time, arrival_time, duration, price):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        sql = """
        INSERT INTO temp_bookings 
        (flight_number,passenger_count, from_airport, to_airport, departure_time, arrival_time, duration, price)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        RETURNING booking_id;
        """
        
        # Insert booking and capture booking_id
        booking_id = await conn.fetchval(
            sql, flight_number,passenger_count, from_airport, to_airport, departure_time, arrival_time, duration, price, 
        )
        return booking_id  # Return the booking ID for later use
    finally:
        await conn.close()

async def get_passenger_count(flight_number):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Query to get the passenger count for the specified flight number
        result = await conn.fetchrow('''
            SELECT passenger_count 
            FROM temp_bookings 
            WHERE flight_number = $1
        ''', flight_number)

        # Check if result is not None and return the passenger count
        if result:
            return result['passenger_count']
        else:
            return None  # or return 0 if you prefer that for no records found
    except Exception as e:
        print(f"Error in get_passenger_count: {e}")
        return None
    finally:
        await conn.close()


async def fetch_passenger_info(user_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        sql = """
        SELECT first_name, last_name, phone_no, email_id
        FROM booking_details
        WHERE user_id = $1;
        """
        result = await conn.fetchrow(sql, user_id)
        if result:
            return {
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "phone_no": result["phone_no"],    
                "email_id": result["email_id"]
            }
        else:
            return None
    except Exception as e:
        return None
    finally:
        await conn.close()


async def get_passenger_count(booking_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Query to retrieve passenger_count using booking_id
        sql = """
        SELECT passenger_count 
        FROM temp_bookings 
        WHERE booking_id = $1;
        """
        
        # Execute the query and fetch the result
        result = await conn.fetchval(sql, booking_id)
        
        # Check if a result was found
        if result is not None:
            return result  # Return the passenger count
        else:
            return None  # Return 0 or None if no matching booking found
    except Exception as e:
        print(f"Error fetching passenger count: {e}")
        return None
    finally:
        await conn.close()


async def create_passenger_details_table():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # SQL command to create the table if it doesn't already exist
        sql = """
        CREATE TABLE IF NOT EXISTS passenger_details (
            id SERIAL PRIMARY KEY,
            booking_id INTEGER REFERENCES temp_bookings(booking_id) ON DELETE CASCADE,
            user_id VARCHAR(20) NOT NULL,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            phone_no VARCHAR(15),
            email_id VARCHAR(50)
        );
        """
        await conn.execute(sql)
        print("Table 'passenger_details' created successfully or already exists.")
    except Exception as e:
        print(f"Error creating passenger_details table: {e}")
    finally:
        await conn.close()

async def add_passenger_details(booking_id, passengers):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        sql = """
        INSERT INTO passenger_details (booking_id, user_id, first_name, last_name, phone_no, email_id)
        VALUES ($1, $2, $3, $4, $5, $6);
        """
        
        # Insert each passenger's details
        for passenger in passengers:
            await conn.execute(
                sql,
                booking_id,
                passenger["user_id"],
                passenger["first_name"],
                passenger["last_name"],
                passenger["phone_no"],
                passenger["email_id"]
            )
    finally:
        await conn.close()


# Function to fetch booking and passenger details from the database
async def fetch_booking_details(booking_id):
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Fetch booking details
        booking_query = """
        SELECT flight_number, from_airport, to_airport, departure_time, arrival_time, duration, price, passenger_count
        FROM temp_bookings
        WHERE booking_id = $1;
        """
        booking_result = await conn.fetchrow(booking_query, booking_id)
        
        if not booking_result:
            return None, "Booking not found. Please verify the booking ID."

        # Fetch passenger details
        passenger_query = """
        SELECT user_id, first_name, last_name, phone_no, email_id
        FROM passenger_details
        WHERE booking_id = $1;
        """
        passenger_results = await conn.fetch(passenger_query, booking_id)

        return booking_result, passenger_results
    
    except Exception as e:
        print(f"Error fetching booking details: {e}")
        return None, "An error occurred while retrieving booking details."
    finally:
        await conn.close()
        
    
    
#permanent booking details 

async def create_permanent_booking_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS permanent_booking (
        booking_id SERIAL PRIMARY KEY,
        flight_number TEXT,
        from_airport TEXT,
        to_airport TEXT,
        departure_time TIMESTAMPTZ,
        arrival_time TIMESTAMPTZ,
        duration TEXT,
        price NUMERIC,
        passenger_count INT,
        ticket_pdf BYTEA 
    );
    """
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(create_table_query)
    finally:
        await conn.close()
        

async def create_permanent_passenger_details_table():
    create_table_query = """
    CREATE TABLE IF NOT EXISTS permanent_passenger_details (
        passenger_id SERIAL PRIMARY KEY,
        booking_id INT REFERENCES permanent_booking(booking_id),
        first_name TEXT,
        last_name TEXT,
        phone_no TEXT,
        email_id TEXT
    );
    """
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        await conn.execute(create_table_query)
    finally:
        await conn.close()
        
#transferring from temp to permanent 


async def transfer_data_from_temp_to_permanent(booking_id):
    # Step 1: Fetch booking details from the temp_bookings table
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        # Fetch booking details from temp_bookings table
        temp_booking_query = """
        SELECT * FROM temp_bookings WHERE booking_id = $1;
        """
        temp_booking_data = await conn.fetchrow(temp_booking_query, booking_id)

        if not temp_booking_data:
            raise ValueError(f"No booking found with ID: {booking_id}")

        # Insert into permanent_booking table
        insert_booking_query = """
        INSERT INTO permanent_booking (booking_id,flight_number, from_airport, to_airport, 
            departure_time, arrival_time, duration, price, passenger_count)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING booking_id;
        """
        booking_id_result = await conn.fetchrow(
            insert_booking_query,
            booking_id,
            temp_booking_data['flight_number'], 
            temp_booking_data['from_airport'],
            temp_booking_data['to_airport'],
            temp_booking_data['departure_time'],
            temp_booking_data['arrival_time'],
            temp_booking_data['duration'],
            temp_booking_data['price'],
            temp_booking_data['passenger_count']
        )

        permanent_booking_id = booking_id

        # Step 2: Fetch passenger details from temp_passenger_details table
        temp_passenger_query = """
        SELECT * FROM passenger_details WHERE booking_id = $1;
        """
        temp_passenger_data = await conn.fetch(temp_passenger_query, booking_id)

        # Insert each passenger into the permanent_passenger_details table
        for passenger in temp_passenger_data:
            insert_passenger_query = """
            INSERT INTO permanent_passenger_details (booking_id, first_name, last_name, phone_no, email_id)
            VALUES ($1, $2, $3, $4, $5);
            """
            await conn.execute(
                insert_passenger_query,
                permanent_booking_id,
                passenger['first_name'],
                passenger['last_name'],
                passenger['phone_no'],
                passenger['email_id']
            )
    finally:
        await conn.close()


async def store_pdf_in_database(booking_id, pdf_content):
    """
    Stores the given PDF binary content in the database for the specified booking ID.
    """
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        update_pdf_query = """
        UPDATE permanent_booking
        SET ticket_pdf = $1
        WHERE booking_id = $2;
        """
        # Insert the binary PDF data into the table
        await conn.execute(update_pdf_query, pdf_content, booking_id)
    except Exception as e:
        print(str(e))
    finally:
        await conn.close()



async def get_booking_details(booking_id):
    conn = await asyncpg.connect(DATABASE_URL)
    
    try:
        # Fetch booking details from the permanent booking table
        booking_query = """
        SELECT booking_id, flight_number, from_airport, departure_time, 
               to_airport, arrival_time, price
        FROM permanent_booking
        WHERE booking_id = $1;
        """
        booking_row = await conn.fetchrow(booking_query, booking_id)
        
        if not booking_row:
            return None, f"Booking not found.{booking_id}"

        # Fetch passenger details from the passenger_details table
        passengers_query = """
        SELECT first_name, last_name, phone_no, email_id
        FROM permanent_passenger_details
        WHERE booking_id = $1;
        """
        passengers = await conn.fetch(passengers_query, booking_id)
        
        # Build booking information dictionary
        booking_info = {
            "Booking ID": str(booking_row["booking_id"]),
            "Flight Number": booking_row["flight_number"],
            "Departure": f"{booking_row['from_airport']} at {booking_row['departure_time'].strftime('%I:%M %p')} on {booking_row['departure_time'].date()}",
            "Arrival": f"{booking_row['to_airport']} at {booking_row['arrival_time'].strftime('%I:%M %p')} on {booking_row['arrival_time'].date()}",
            "Price": f"${booking_row['price']}",
            "Passengers": [
                {
                    "Name": f"{passenger['first_name']} {passenger['last_name']}",
                    "Phone": passenger["phone_no"],
                    "Email": passenger["email_id"]
                } for passenger in passengers
            ]
        }

        return booking_info, None

    except Exception as e:
        return None, f"Error retrieving booking details: {e}"
    finally:
        await conn.close()


async def retrieve_pdf_from_db(booking_id):
    """Fetch the PDF binary data from the database using the booking ID."""
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        query = "SELECT ticket_pdf FROM permanent_booking WHERE booking_id = $1"
        result = await conn.fetchval(query, booking_id)
        return result  # PDF binary data
    finally:
        await conn.close()
        
        
#saved passenger info for all the passengers

async def fetch_all_passenger_info():
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        sql = """
        SELECT user_id, first_name, last_name, phone_no, email_id
        FROM booking_details;
        """
        results = await conn.fetch(sql)
        all_passenger_info = [
            {
                "user_id": result["user_id"],
                "first_name": result["first_name"],
                "last_name": result["last_name"],
                "phone_no": result["phone_no"],
                "email_id": result["email_id"]
            }
            for result in results
        ]
        return all_passenger_info
    except Exception as e:
        print(f"Error fetching passenger info: {e}")
        return []
    finally:
        await conn.close()