import json
from datetime import datetime

from const import BOOKINGCOM_API_KEY, BOOKINGCOM_HOST

def get_url(from_airport,to_airport,departureDate):
    base_url = "https://www.gotogate.com/air/"
    date_obj = datetime.strptime(departureDate, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d%b").upper()
    url = base_url + f"{from_airport}{to_airport}{formatted_date}"
    print(url)
    return url

async def get_flight_data(from_airport,to_airport,departureDate,page="1",cabinClass="ECONOMY",numberOfStops="all"):
    import requests

    url = "https://booking-com18.p.rapidapi.com/flights/search-oneway"

    querystring = {"fromId":from_airport,"toId":to_airport,"departureDate":departureDate,"page":page,"cabinClass":cabinClass,"numberOfStops":numberOfStops}

    headers = {
        "x-rapidapi-key": BOOKINGCOM_API_KEY,
        "x-rapidapi-host": BOOKINGCOM_HOST
    }

    response = await requests.get(url, headers=headers, params=querystring)

    
    return response.json()



def parse_flight_data(response):
    flights = response['data']['flights']
    flight_details = []

    for flight in flights:
        flight_info = {
            
            "Flight ID": flight['id'],
            "Type": flight['type'],
            "Trip ID": flight['tripId'],
            "Trip Type": flight['type'],
            "Url" : flight["shareableUrl"],
            
            "Segments": []
        }

        for bound in flight['bounds']:
            for segment in bound['segments']:
                if segment['__typename'] == "TripSegment":
                    segment_info = {
                        "Flight Number": segment['flightNumber'],
                        "Aircraft Type": segment['equipmentCode'],
                        "Cabin Class": segment['cabinClassName'],
                        "Departure": {
                            "Location": segment['origin']['name'],
                            "Airport Code": segment['origin']['airportCode'],
                            "Time": datetime.fromisoformat(segment['departuredAt']).strftime("%Y-%m-%d %H:%M")
                        },
                        "Arrival": {
                            "Location": segment['destination']['name'],
                            "Airport Code": segment['destination']['airportCode'],
                            "Time": datetime.fromisoformat(segment['arrivedAt']).strftime("%Y-%m-%d %H:%M")
                        },
                        "Duration (Hours)": segment['duration'] / (1000 * 60 * 60),
                        
                    }
                    flight_info["Segments"].append(segment_info)

        flight_details.append(flight_info)
        
    
    return flight_details

# resp= get_flight_data("COK","CNN","2024-11-14")
# det = parse_flight_data(resp)
# print(det[0]["Url"])

def format_flight_details(flight_details):
    
    formatted_message = "Here are the available flight details:\n\n"
    
    for idx, flight in enumerate(flight_details, start=1):
        flight_text = (
            f"Flight {idx}:\n"
            f"✈️ Flight ID: {flight['Flight ID']}\n"
            f"🔗 Flight URL: {flight['Url']}\n"
            f"🗂 Type: {flight['Type']}\n"
            f"🎟 Trip ID: {flight['Trip ID']} ({flight['Trip Type']})\n\n"
        )

        for segment in flight['Segments']:
            flight_text += (
                
                f"🔹 Flight Number: {segment['Flight Number']}\n"
                f"🛫 Departure: {segment['Departure']['Location']} ({segment['Departure']['Airport Code']}) at {segment['Departure']['Time']}\n"
                f"🛬 Arrival: {segment['Arrival']['Location']} ({segment['Arrival']['Airport Code']}) at {segment['Arrival']['Time']}\n"
                f"🕒 Duration: {round(segment['Duration (Hours)'], 2)} hours\n"
                f"🛩 Aircraft Type: {segment['Aircraft Type']}\n"
                f"👔 Cabin Class: {segment['Cabin Class']}\n"
                
            )

        formatted_message += flight_text + "\n\n"
        
    return formatted_message


async def alternateCheckflight(from_airport,to_airport,departureDate):
    try:
        formatted_departureDate = datetime.fromisoformat(departureDate).strftime("%Y-%m-%d")
        response =await get_flight_data(from_airport,to_airport,formatted_departureDate)
        flight_details = parse_flight_data(response)
        message = format_flight_details(flight_details)
        url = get_url(from_airport,to_airport,formatted_departureDate)
        intro = f"To get more details about flights visit {url}"
        message = intro + message
    except Exception as e:
        message = f"An error occured while fetching flight details.{str(e)}"
    finally:
        return {
            "fulfillmentMessages" : [{
                "text" : {
                    "text" : [message]
                }
            }]
        }