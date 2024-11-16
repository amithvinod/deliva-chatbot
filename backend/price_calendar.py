
import requests
import datetime
import airport
from const import RAPIDAPI_HOST, RAPIDAPI_KEY


def get_price_calendar(from_iata_code, to_iata_code):
    # Setting up the URL and API headers
    url = "https://sky-scanner3.p.rapidapi.com/flights/price-calendar"
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": RAPIDAPI_HOST
    }
    
    # Calculate the departure date as today + 1 day
    start_date = datetime.date.today()
    depart_date = start_date.strftime("%Y-%m-%d")
    # Setup query parameters
    querystring = {
        "fromEntityId": from_iata_code,
        "toEntityId": to_iata_code,
        "departDate": depart_date,
        "market": "IN",
        "locale": "en-GB",
        "currency": "INR"
    }
    
    # Make the request
    response = requests.get(url, headers=headers, params=querystring)
    
    if response.status_code == 200:
        data = response.json().get("data", {}).get("flights", {}).get("days", [])
        
        # Prepare result for the next 30 days
        prices = []
        for day in data:  
            prices.append({
                "date": day["day"],
                "price": day["price"],
                "group": day["group"]
            })
        
        return prices
    
    else:
        print("Error:", response.status_code, response.text)
        return []
    
def get_sorted_prices(prices):
    # Sort the prices list by date in ascending order
    sorted_prices = sorted(prices, key=lambda x: x["date"])
    
    # Return the first 30 entries or fewer if there are less than 30
    return sorted_prices[:30]


def format_prices_for_dialogflow(prices,from_city,to_city, start_index=0):
    # Check if the start_index is valid
    
    if start_index+10 >= len(prices):
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["🚫 Error fetching price calendar(API request error)"]
                    }
                }
            ]
        }

    # Get the next 10 prices from the start index, or fewer if near the end of the list
    selected_prices = prices[start_index:start_index + 10]

    # Start building the response with emojis and formatting
    response = f"✈️ Here are the flight prices for the next few days from {from_city} to {to_city}:\n\n"
    for entry in selected_prices:
        date = entry["date"]
        price = entry["price"]
        price_group = entry["group"]

        # Adding emojis based on price group
        if price_group == "low":
            price_emoji = "💸"
        elif price_group == "medium":
            price_emoji = "💵"
        else:
            price_emoji = "💰"

        # Format each entry
        response += f"📅 Date: {date}\n{price_emoji} Price: ₹{price} ({price_group.capitalize()} category)\n\n"

    # Return the response in Dialogflow's fulfillment format
    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [response.strip()]  # Strip to remove any trailing whitespace
                }
            },
            
        ]
    }


async def price_calendar_results(from_airport,to_airport,index):
    try:
        from_iata_code = None
        to_iata_code = None
        from_airport_data = await airport.search_airport(from_airport)
        to_airport_data = await airport.search_airport(to_airport)
        from_success, from_code, from_title = airport.get_airport_code(from_airport_data)
        to_success, to_code, to_title = airport.get_airport_code(to_airport_data)
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
        if index==0:
            response = get_price_calendar(from_code,to_code)
            price_list = get_sorted_prices(response)
        return format_prices_for_dialogflow(price_list,from_title,to_title,index)
    except Exception as e:
        return {
                "fulfillmentText" : f"There was an arror fetching the price calendar , {str(e)}"
            }