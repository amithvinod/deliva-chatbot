# Function for flight search using RapidAPI
from datetime import datetime
from typing import Any, Dict
import requests

import airport
from const import RAPIDAPI_HOST, RAPIDAPI_KEY


async def search_flight(from_city: str, to_city: str, date: str) -> Dict[str, Any]:
    from_data  = await airport.search_airport(from_city)
    to_data  = await airport.search_airport(to_city)
    return from_data,to_data

def format_initial_search_response(from_city: str, to_city: str, from_data: Dict[str, Any], 
                                   to_data: Dict[str, Any], date: str) -> Dict[str, Any]:
    """
    Format the initial response with confirmation message including airport codes
    """
    # Get airport codes
    from_success, from_code, from_title = airport.get_airport_code(from_data)
    to_success, to_code, to_title = airport.get_airport_code(to_data)
    parsed_date = datetime.fromisoformat(date)
    formatted_date = parsed_date.strftime("%B %d, %Y")
    
    if not (from_success and to_success):
        error_message = "Could not find airport codes for one or both cities."
        return {
            
            "fulfillmentMessages": [{
                "text": {
                    "text": [error_message]
                }
            },
            
            ]
        }

    # Create confirmation message
    confirmation_message = (
        f"Do you want to check flights from {from_title} to {to_title} on {formatted_date}"
        
    )
    
   
    
    return {
        
        "fulfillmentMessages": [{
            "text": {
                "text": [confirmation_message]
            }
        },
        {
                "quickReplies": {
                    
                    "quickReplies": ["Yes", "No"]
                }
            }
                                ],
        "outputContexts": [
        {
            "name": "projects/{project-id}/agent/sessions/{session-id}/contexts/flight_search_context",
            "lifespanCount": 5,
            "parameters": {
                "from_iata_code": from_code,
                "to_iata_code": to_code,
                "travel_date": date  # Assuming you already extracted the date
            }
        }
    ]
        
    }
    

def handle_check_flight(from_iata_code,to_iata_code,travel_date):
    # Assuming `request` contains the necessary context
    
    depart_date = datetime.fromisoformat(travel_date).date().isoformat() 
    # API request to SkyScanner
    url = "https://sky-scanner3.p.rapidapi.com/flights/search-one-way"
    querystring = {
        "fromEntityId": from_iata_code,
        "toEntityId": to_iata_code,
        "departDate": depart_date,
        "market": "IN",
        "locale": "en-GB",
        "currency": "INR",
        "cabinClass": "economy",
        "adults": "1"
    }
    
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    try:

    # Make the API request
        response = requests.get(url, headers=headers, params=querystring)

        # Check if the request was successful
        if response.status_code == 200:
            flight_data = response.json()
            
            # Extract flight itineraries
            itineraries = flight_data.get("data", {}).get("itineraries", [])
            
            # Prepare the output
            output = []
            for itinerary in itineraries[:5]:  # Limit to the first 10 results
                price = itinerary.get("price", {}).get("formatted", "N/A")
                legs = itinerary.get("legs", [])
                for leg in legs:
                    airline = leg.get("carriers", {}).get("marketing", [{}])[0].get("name", "N/A")
                    flight_number = leg.get("segments", [{}])[0].get("flightNumber", "N/A")
                    departure_time = leg.get("departure", "N/A")
                    arrival_time = leg.get("arrival", "N/A")
                    duration = leg.get("durationInMinutes", "N/A")

                    output.append({
                        "airline": airline,
                        "flight_number": flight_number,
                        "duration": f"{duration} minutes",
                        "departure_time": departure_time,
                        "arrival_time": arrival_time,
                        "price": price
                    })

            # Format the output for the response
            formatted_output = "\n\n".join(
        [
            f"✈️ Flight {index + 1}:\n"
            f"   Airline: {item['airline']}\n"
            f"   Flight Number: {item['flight_number']}\n"
            f"   Duration: {item['duration']} minutes\n"
            f"   Departure: {datetime.fromisoformat(item['departure_time']).strftime('%I:%M %p on %b %d, %Y')}\n"
            f"   Arrival: {datetime.fromisoformat(item['arrival_time']).strftime('%I:%M %p on %b %d, %Y')}\n"
            f"   Price: ₹{item['price']}"
            for index, item in enumerate(output)
        ]
    )
            print(formatted_output)

            response_text = f"Here are the available flights:\n{formatted_output}"

        else:
            response_text = "Sorry, I couldn't retrieve flight details at this time."

        return {
            
            "fulfillmentMessages": [{
                            "text": {
                                "text": [response_text]
                            }
                        }]
        }
    except Exception as e:
        print(f"Sorry an error occured {str(e)}")
        return {
            
            "fulfillmentMessages": [{
                            "text": {
                                "text": f"Sorry an error occured {str(e)}"
                            }
                        }]
        }