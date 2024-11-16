import json
from datetime import datetime, timezone
import re
from generate_pdf import generate_pdf_content
from price_calculate import fetch_ticket_price
from const import Booking, gpay, phonepay
import requests

import asyncio

from db import add_passenger_details, add_temp_booking, create_passenger_details_table, create_permanent_booking_table, create_permanent_passenger_details_table, create_temp_booking_table, fetch_booking_details, fetch_passenger_info, get_booking_details, get_passenger_count, retrieve_pdf_from_db, store_pdf_in_database, transfer_data_from_temp_to_permanent
from save_pdf_to_cloud import upload_pdf_to_google_cloud


def bookFlight(params):
    flight_number = params.get("flight-number","")
    travel_date = params.get("date","")
    num_passengers = params.get("num_passengers","")
    print(type(travel_date))
    # Parse the timestamp
    date_part = datetime.fromisoformat((travel_date)).date()

    # Convert it to a string if needed
    date_str = date_part.strftime('%Y-%m-%d')


    response_text = (
        f"Got it! Here’s what I have for your booking:\n\n"
        f"- Flight: {flight_number}\n"
        f"- Date: {date_str}\n"
        f"- Passengers: {int(num_passengers)}\n\n"
        
    )

    # Create the JSON response
    response = {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [response_text]
                }
            },
            {
                "quickReplies": {
                    "title": "Would you like me to proceed with booking these tickets?",
                    "quickReplies": ["Yes", "No"]
                }
            }
        ]
    }

    # Return JSON response
    return response

def verify_flight_number(flight_number: str) -> bool:
    # Basic regex to check if flight number format is valid (e.g., two letters followed by 3-4 digits)
    if not re.match(r"^[A-Z0-9]{2}\d{3,4}$", flight_number):
        return False
    return True

# def findDuration(departure_time,arrival_time):
#     # Convert the strings to datetime objects
#     departure_dt = datetime.fromisoformat(departure_time.replace("Z", "+00:00"))  # Handle UTC time
#     arrival_dt = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))

#     # Calculate the duration
#     duration = arrival_dt - departure_dt

#     # Get the total seconds from the duration and convert to hours and minutes
#     duration_seconds = int(duration.total_seconds())
#     hours = duration_seconds // 3600
#     minutes = (duration_seconds % 3600) // 60

#     # Format the duration
#     formatted_duration = f"{hours}h {minutes}min"
#     return formatted_duration

def formattedDatetime(departure_time,arrival_time):
    departure_dt = datetime.fromisoformat(departure_time.replace("Z", "+00:00"))
    arrival_dt = datetime.fromisoformat(arrival_time.replace("Z", "+00:00"))

    # Extract the date for display
    depDate = departure_dt.strftime("%Y-%m-%d")  # Format: "2024-11-03"
    arrDate = arrival_dt.strftime("%Y-%m-%d")
    # Format the times to display only hours and minutes
    formatted_departure_time = departure_dt.strftime("%H:%M %p")  # e.g., "14:30 PM"
    formatted_arrival_time = arrival_dt.strftime("%H:%M %p") 
    return depDate,formatted_departure_time,arrDate,formatted_arrival_time

def parse_datetime(date_str):
    dt = datetime.fromisoformat(date_str)
    # Convert naive datetime to UTC-aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

def findDuration(departure_time, arrival_time):
    # Convert the strings to UTC-aware datetime objects
    departure_dt = parse_datetime(departure_time)
    arrival_dt = parse_datetime(arrival_time)

    # Calculate the duration
    duration = arrival_dt - departure_dt

    # Get the total seconds from the duration and convert to hours and minutes
    duration_seconds = int(duration.total_seconds())
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60

    # Format the duration
    formatted_duration = f"{hours}h {minutes}min"
    return formatted_duration

async def bookFlight_followup_yes(flight_number,passenger_count):
    flight_number = flight_number.replace(" ", "")
    
    # Verify the flight number
    if not verify_flight_number(flight_number):
        return {
            "fulfillmentText": "Flight number is invalid. Please provide a valid flight number"
        } 
    
    try:
        url = Booking.AVIATION_STACK_URL
        params = {
            "access_key": Booking.AVIATION_STACK_KEY,
            "flight_iata": flight_number
        }

        response = requests.get(url, params=params)
        if response.status_code != 200:
            return {"fulfillmentText": "Failed to fetch flight details. Please try again."}

        data = response.json()
        
        for flight in data.get("data", []):
            if flight["flight"]["iata"] == flight_number:
                from_airport = flight["departure"].get("airport")
                from_code = flight["departure"].get("iata")
                to_airport = flight["arrival"].get("airport")
                to_code = flight["arrival"].get("iata")
                departure_time = flight["departure"].get("scheduled")
                arrival_time = flight["arrival"].get("scheduled")
                # duration = findDuration(departure_time, arrival_time)
                duration = "6h 32min"
                datetime = formattedDatetime(departure_time, arrival_time)

                # Immediate Dialogflow response
                response_text = (
                    f"Here are the details for flight {flight_number}:\n"
                    f"Departure: {from_airport} ({from_code}) at {datetime[1]} on {datetime[0]}\n"
                    f"Arrival: {to_airport} ({to_code}) at {datetime[3]} on {datetime[2]}\n"
                    f"Duration: {duration}\n"
                    
                )

                # Start the background tasks
                await create_temp_booking_table()
                
                # Fetch price in a background task
                price = fetch_ticket_price(flight_number)
                
                dep_time= parse_datetime(departure_time)
                arr_time = parse_datetime(arrival_time)

                # Add booking details with fetched price asynchronously
                booking_id = await add_temp_booking(
                    flight_number,passenger_count, from_airport, to_airport, 
                    dep_time, arr_time, duration, price
                )
                # Check if booking_id was successfully returned
                if not booking_id:
                    return {"fulfillmentText": "Failed to create a booking. Please try again."}

                return {
                    
                    "fulfillmentMessages":[
                        {
                            "text" : {
                                "text":[response_text]
                            }
                            },
                        {
                            "text" : {
                                "text":[f"Temporary booking created with ID {booking_id}. "]
                            }
                            },
                        {
                        "quickReplies": {
                            "title": "Please confirm if these details are correct.",
                            "quickReplies": ["Confirm", "Cancel"]
                        }
                        }
                    ],
                    "outputContexts": [
            {
                "name": "projects/{project-id}/agent/sessions/{session-id}/contexts/booking_context",
                "lifespanCount": 7,
                "parameters": {
                    "booking_id": booking_id  # Pass booking_id for use in the next intent
                }
            }
        ]
                }
                
    except Exception as e:
        print(f"Error in bookFlight_followup_yes: {e}")
        return {"fulfillmentText": "An error occurred. Please try again."}


def bookFlight_followup_no():
    return {
            "fulfillmentText": "If any of the details are correct please try again.",
            "followupEventInput": {
                "name": "RETRY_BOOK_FLIGHT",
                "parameters": {}
            }
        }
    
    
async def handle_passenger_details(passenger_list,booking_id):
    
    passenger_count = await get_passenger_count(booking_id)
    
    
    if passenger_count is None:
        return {"fulfillmentText": "Could not retrieve passenger count for the booking."}
    
    if len(passenger_list) != passenger_count:
        return {
            "fulfillmentText": f"You provided {len(passenger_list)} names, but the booking requires {passenger_count} passengers. Please provide the correct number of names.",
            "followupEventInput": {
                "name": "PROMPT_PASSENGER_NAMES",
                "parameters": {}
            }
        }
    # Step 2: Retrieve passenger details from the database
    passenger_details = []
    for name in passenger_list:
        name = name.replace(" ","_")
        passenger_info = await fetch_passenger_info(name)
        if passenger_info:
            passenger_details.append({
                "user_id" : name,
                "first_name": passenger_info["first_name"],
                "last_name": passenger_info["last_name"],
                "phone_no": passenger_info["phone_no"],
                "email_id" : passenger_info["email_id"]
            })
        else:
            return {
                "fulfillmentText": f"Passenger details for '{name}' were not found in the database. Please provide valid names."
            }
    
    #store in db
    await create_passenger_details_table()
    
    await add_passenger_details(booking_id,passenger_details)
    
    print("no error")
    # Step 3: Generate a response for user confirmation
    confirmation_text = "Here are the passenger details for your booking:\n"
    for idx, passenger in enumerate(passenger_details, start=1):
        confirmation_text += f"- Passenger {idx}: {passenger['first_name']} {passenger['last_name']} Ph : {passenger['phone_no']} Email: {passenger['email_id']}\n"

    confirmation_text += "Please confirm if these details are correct."
    
    return {
        "fulfillmentText" : confirmation_text,
        "fulfillmentMessages":[
            {
                "text":{
                    "text" : [confirmation_text]
                }
                },
            {
                        "quickReplies": {
                            "title": "Please confirm if these details are correct.",
                            "quickReplies": ["Confirm", "Cancel"]
                        }
                        }
        ],
        "outputContexts": [
            {
                "name": "projects/{project-id}/agent/sessions/{session-id}/contexts/booking_context",
                "lifespanCount": 5,
                "parameters": {
                    "booking_id": booking_id  # Pass booking_id for use in the next intent
                }
            }
        ]
    }
    
async def handle_booking_confirmation_request(booking_id):
    # Fetch booking details from the database
    try:
        booking_result, passenger_results = await fetch_booking_details(booking_id)
        price = booking_result['price']

        booking_info = (
            f"Booking ID: {booking_id}\n"
            f"Flight: {booking_result['flight_number']}\n"
            f"From: {booking_result['from_airport']}\n"
            f"To: {booking_result['to_airport']}\n"
            f"Departure: {booking_result['departure_time']}\n"
            f"Arrival: {booking_result['arrival_time']}\n"
            f"Duration: {booking_result['duration']}\n"
            f"Price: {booking_result['price']}\n"
            f"Passenger Count: {booking_result['passenger_count']}\n\n"
            f"Passengers:\n"
        )

        # Format the passenger details
        for passenger in passenger_results:
            booking_info += (
                f"- {passenger['first_name']} {passenger['last_name']} "
                f"(Phone: {passenger['phone_no']}, Email: {passenger['email_id']})\n"
            )

        # Build the response
        # Assuming you already have these variables


        response = {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            f"Here are your booking details:\n\n{booking_info}\n\n"
                            f"The total cost for your journey is ₹{price}. Please confirm to proceed with payment."
                            "If you wish to cancel click on the cancel booking button."
                        ]
                    }
                },
                
                {
                    "card": {
                        "title": "Select Payment Method",
                        "buttons": [
                            {
                                "text": "Pay with GPay",
                                "postback": gpay(price)
                            },
                            {
                                "text": "Pay with PhonePe",
                                "postback": phonepay(price)
                            },
                            {
                                "text": "Cancel Booking",
                                "postback": "CANCEL_BOOKING"
                            }
                        ]
                    }
                }
            ],
            "outputContexts": [
            {
                "name": "projects/{project-id}/agent/sessions/{session-id}/contexts/booking_context",
                "lifespanCount": 3,
                "parameters": {
                    "booking_id": booking_id  # Pass booking_id for use in the next intent
                }
            }
        ]
        }


    except Exception as e:
        response = {
            "fulfillmentText": (
                f"There was an error fetching booking details . {str(e)}"
            )
        }
    return response

#final setp 

async def finalize_booking(booking_id):
    try:
        # Step 1: Create tables if they do not exist
        await create_permanent_booking_table()
        await create_permanent_passenger_details_table()

        # Step 2: Transfer data from temp tables to permanent tables
        await transfer_data_from_temp_to_permanent(booking_id)
        print("transfer done")
        booking_info,msg = await get_booking_details(booking_id)
        
        if not booking_info:
            return {
                "fulfillmentText": f"Failed to fetch Booking details. {msg}",
            }
        
        pdf_generated = generate_pdf_content(booking_info)
        
        #print(pdf_generated)
        
        await store_pdf_in_database(booking_id,pdf_generated)
        
        return {
            "fulfillmentText" : f"Ticket Booking for Booking ID:{booking_id} Successful.Do you want your ticket send in this chat?"
        }
        
    except Exception as e:
        return {
            "fulfillmentText" : f"There was an error while generating the ticket.{str(e)}"
        }
    
    
async def sent_ticket(booking_id):
    pdf = await retrieve_pdf_from_db(booking_id)
    if not pdf:
        response = f"Error fetching ticket from database . Please check booking id:{booking_id}"
        return {
            "fulfillmentText" : response
        }
    
        
    file_name = f"ticket {booking_id}"
    url = upload_pdf_to_google_cloud(pdf,file_name)
    print(url)
    
    if not url:
        response = f"Error uploading ticket to cloud"
        return {
            "fulfillmentText" : response
        }
    response = f"Here is your ticket url {url}"
    
    return {
            "fulfillmentText" : response
        }