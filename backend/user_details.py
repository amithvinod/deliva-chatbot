
import asyncpg

from const import DATABASE_URL
from db import fetch_all_passenger_info, userDetails_to_db


def saveUser(params):
    first_name = params.get("first_name","")
    last_name = params.get("last_name","")
    phone = params.get("phone_no","")
    email = params.get("email_id","")
    
    return {
        
  


        "fulfillmentMessages":[
            {
            "text":{
                "text" : ["Please confirm your details\n",
                          f"First Name : {first_name}",
                          f"Last Name : {last_name}",
                          f"Phone Number : {phone}",
                          f"Email : {email}",
                          ]
            }
        },
            {
                "quickReplies": {
                    "title": "Is the details correct?",
                    "quickReplies": ["Yes", "No"]
                }
            }
           
        ]
    }



async def saveUserFollowup(response,output_context):
    resp = response.lower()
    if resp == "yes":
        print("hi")
        first_name = None
        last_name = None
        phone_no = None
        email = None

        for context in output_context:
            if "save-user-details" in context["name"]:
                para = context.get("parameters", {})
                first_name = para.get("first_name")
                last_name = para.get("last_name")
                phone_no = para.get("phone_no")
                email = para.get("email_id")
                break  
        print(first_name,last_name,phone_no,email)
# Check if any required parameter is missing
        if not all([first_name, last_name, phone_no, email]):
            return {
            "fulfillmentText": "I could not complete the action."
        }

            
            
        else:
            # Call the function if all parameters are present
            params = {
                "first_name": first_name,
                "last_name": last_name,
                "phone_no": phone_no,
                "email_id": email,
            }
        status, res = await userDetails_to_db(params)
        
        if(status):
            response_text = "Your details are successfully saved."
        else:
            response_text = f"Sorry I encountered an error {res}"  
        
        return {
            "fulfillmentText": response_text
        }
    elif resp == "no":
        return {
            "fulfillmentText": "Please try saving your details again."
        }
    else:
        print("else")
        return {
                "fulfillmentText": "Sorry, I don't know how to handle that request.",
                "fulfillmentMessages": [{
                    "text": {
                        "text": ["Sorry, I don't know how to handle that request."]
                    }
                }]
            }
        
        
async def get_user_details():
    users = await fetch_all_passenger_info()  # Fetch all users from the database
    if not users:
        return {
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": ["No user details found."]
                    }
                }
            ]
        }

    # Formatting user details for Dialogflow response
    user_details = [
    f"🆔 User ID: {user['user_id']}\n"
    f"👤 Name: {user['first_name']} {user['last_name']}\n"
    f"📞 Phone: {user['phone_no']}\n"
    f"✉️ Email: {user['email_id']}\n"
    "───────────────────"  # Divider for readability
    for user in users
]
    
    # Join each user's details with a separator for readability
    details_text = "\n\n".join(user_details)

    return {
        "fulfillmentMessages": [
            {
                "text": {
                    "text": [
                        "Here are the details of all users:\n\n" + details_text
                    ]
                }
            },
            
        ]
    }
