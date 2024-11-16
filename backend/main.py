from fastapi import FastAPI, Request
from datetime import datetime
import airport
import requests
from typing import Dict, Any, Tuple

from alternate_check_flight import alternateCheckflight
from booking import bookFlight, bookFlight_followup_no, bookFlight_followup_yes, finalize_booking, handle_booking_confirmation_request, handle_passenger_details, sent_ticket
from check_flight import format_initial_search_response, handle_check_flight, search_flight
from db_setup import create_and_populate_airport_codes_table, create_and_populate_booking_details_table
import price_calendar
from user_details import get_user_details, saveUser, saveUserFollowup

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await create_and_populate_airport_codes_table()
    await create_and_populate_booking_details_table()


@app.post("/webhook")
async def dialogflow_webhook(request: Request):
    """
    Webhook endpoint for Dialogflow
    """
    try:
        body = await request.json()
        query_result = body.get("queryResult", {})
        intent = query_result.get("intent", {}).get("displayName", "")
        parameters = query_result.get("parameters", {})
        output_context = query_result.get("outputContexts",{})
      
        if intent == "search.airport":
            # Handle airport code search using PostgreSQL
            city = parameters.get("geo-city", [""])[0] if isinstance(parameters.get("geo-city", ""), list) else parameters.get("geo-city", "")

            if not city:
                return {
                    "fulfillmentText": "Please provide a city name to search for its airport code.",
                    "fulfillmentMessages": [{
                        "text": {
                            "text": ["Please provide a city name to search for its airport code."]
                        }
                    }]
                }

            airport_data = await airport.search_airport(city)
            return airport.format_airport_search_response(city, airport_data)
        
        elif intent == "check.flight":
            # Handle flight search using RapidAPI
            from_city = parameters.get("geo-city", [""])[0] if isinstance(parameters.get("geo-city", ""), list) else parameters.get("geo-city", "")
            to_city = parameters.get("geo-city1", [""])[0] if isinstance(parameters.get("geo-city1", ""), list) else parameters.get("geo-city1", "")
            date = parameters.get("date-time", "")
            
            if(from_city==to_city):
                return {
                    "fulfillmentText": "Source and Destination cannot be the same",
                    "fulfillmentMessages": [{
                        "text": {
                            "text": ["Source and Destination cannot be the same"]
                        }
                    }]
                }

            # Use RapidAPI to get flight data
            from_airport_data, to_airport_data = await search_flight(from_city, to_city, date)
            if(from_airport_data["iata_code"]==to_airport_data["iata_code"]):
                return {
                    "fulfillmentText": "Source and Destination cannot be the same",
                    "fulfillmentMessages": [{
                        "text": {
                            "text": ["Source and Destination cannot be the same"]
                        }
                    }]
                }

            # Return formatted confirmation message
            return format_initial_search_response(from_city, to_city, from_airport_data, to_airport_data, date)
        
        elif intent == "check.flight - yes":
            

    # Retrieve the stored airport codes and travel date from context
            for context in output_context:
                if "flight_search_context" in context["name"]:  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    from_iata_code = parameters.get("from_iata_code")
                    to_iata_code = parameters.get("to_iata_code")
                    travel_date = parameters.get("travel_date")
            #print(from_iata_code)
            #return await alternateCheckflight(from_iata_code,to_iata_code,travel_date)
            return handle_check_flight(from_iata_code,to_iata_code,travel_date)
        elif intent=="save.user":
            return saveUser(parameters)

        elif intent == "save.user-followup":
            user_response = query_result.get("queryText",{})
            out = await saveUserFollowup(user_response,output_context)
            return out
        
        elif intent == "book.flight":
            return bookFlight(parameters)

        elif intent == "book.flight - yes":
            
            for context in output_context:
                if "book-flight-intitiated" in context["name"]:  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    flight_num = parameters.get("flight-number","")
                    passenger_count = parameters.get("num_passengers","")
                    
            res = await bookFlight_followup_yes(flight_num,passenger_count)
            return res
        
        elif intent == "book.flight - no":
            return bookFlight_followup_no()
        
        elif intent == "collect.passengerDetails":
            
            for context in output_context:
                if ("booking_context" in context["name"]):  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    booking_id = parameters.get("booking_id","")
                    
            passenger_list =  parameters.get("passenger_list",{})
            #print("hi")
            return await handle_passenger_details(passenger_list,booking_id)
        
        elif intent == "final.confirmation":
            for context in output_context:
                if ("booking_context" in context["name"]):  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    booking_id = parameters.get("booking_id","")
            return await handle_booking_confirmation_request(booking_id)
        
        elif intent == "booking.payment.done":
            for context in output_context:
                if ("booking_context" in context["name"]):  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    booking_id = parameters.get("booking_id","")
            return await finalize_booking(booking_id)
        
        elif intent == "booking.payment.done - yes":
            for context in output_context:
                if ("booking_context" in context["name"]):  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    booking_id = parameters.get("booking_id","")
            return await sent_ticket(booking_id)
        
        elif intent == "get.user.details":
            return await get_user_details()
        
        elif intent == "price.calendar":
            from_city  = parameters.get("geo-city","")
            to_city = parameters.get("geo-city1","")
            return await price_calendar.price_calendar_results(from_city,to_city,0)
        
        elif intent == "price.calendar - more":
            for context in output_context:
                if ("pricecalendar-initiated" in context["name"]):  # Check for flight_search_context
                    parameters = context.get("parameters", {})
                    from_city = parameters.get("geo-city","")
                    to_city = parameters.get("geo-city1","")
            return await price_calendar.price_calendar_results(from_city,to_city,10)
        else:
            return {
                "fulfillmentText": "Sorry, I don't know how to handle that request.",
                "fulfillmentMessages": [{
                    "text": {
                        "text": ["Sorry, I don't know how to handle that request."]
                    }
                }]
            }

    except Exception as e:
        return {
            "fulfillmentText": f"Sorry, I encountered an error: {str(e)}",
            "fulfillmentMessages": [{
                "text": {
                    "text": [f"Sorry, I encountered an error: {str(e)}"]
                }
            }]
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
