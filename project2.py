### Required Libraries ###
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import boto3
import requests
### Functionality Helper Functions ###
def parse_int(n):
    """
    Securely converts a non-integer value to integer.
    """
    try:
        return int(n)
    except ValueError:
        return float("nan")
def build_validation_result(is_valid, violated_slot, message_content):
    """
    Define a result message structured as Lex response.
    """
    if message_content is None:
        return {"isValid": is_valid, "violatedSlot": violated_slot}
    return {
        "isValid": is_valid,
        "violatedSlot": violated_slot,
        "message": {"contentType": "PlainText", "content": message_content},
    }

def get_btcprice():
    """
    Retrieves the current price of bitcoin in dollars from the alternative.me Crypto API.
    """
    bitcoin_api_url = "https://api.alternative.me/v2/ticker/bitcoin/?convert=USD"
    response = requests.get(bitcoin_api_url)
    response_json = response.json()
  #  price_dollars = parse_float(response_json["data"]["1"]["quotes"]["USD"]["price"])
    return response_json["data"]["1"]["quotes"]["USD"]["price"]
    
    # Get the current price of bitcoin in dolars and make the conversion from dollars to bitcoin.
def convert_to_dollar(): 
    btc_value = parse_float(dollars) / get_btcprice()
    btc_value = round(btc_value, 4)
    
### Dialog Actions Helper Functions ###
def get_slots(intent_request):
    """
    Fetch all the slots and their values from the current intent.
    """
    return intent_request["currentIntent"]["slots"]
    
def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    print(message)
    """
    Defines an elicit slot type response.
    """
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "ElicitSlot",
            "intentName": intent_name,
            "slots": slots,
            "slotToElicit": slot_to_elicit,
            "message": message,
        },
    }
def delegate(session_attributes, slots):
    """
    Defines a delegate slot type response.
    """
    return {
        "sessionAttributes": session_attributes,
        "dialogAction": {"type": "Delegate", "slots": slots},
    }
def close(session_attributes, fulfillment_state, message):
    """
    Defines a close slot type response.
    """
    response = {
        "sessionAttributes": session_attributes,
        "dialogAction": {
            "type": "Close",
            "fulfillmentState": fulfillment_state,
            "message": message,
        },
    }
    return response
def pricedifference(initial_investment):
    currrentbtcprice = float(get_btcprice())
    print(initial_investment)
    initial_investment = float(initial_investment)
    return currrentbtcprice -  initial_investment
### Intents Handlers ###
def recommend_portfolio(intent_request):
    """
    Performs dialog management and fulfillment for recommending a portfolio.
    """
    first_name = get_slots(intent_request)["firstName"]
    age = get_slots(intent_request)["age"]
    initial_investment = get_slots(intent_request)["initialAmount"]
    risk_level = get_slots(intent_request)["riskLevel"]
    riskType = get_slots(intent_request)["riskType"]
    source = intent_request["invocationSource"]
    validation_result = validate_data(age, initial_investment, intent_request)
    current_price = get_btcprice()
    print(current_price)
    if initial_investment is not None and riskType is None:
        return loss(initial_investment,intent_request) 
    if riskType is not None:
        return riskEval(pricedifference(initial_investment), riskType, intent_request)
    if source == "DialogCodeHook":
        #if type(risk_level) is not None and type(initial_investment) is not None:
         #   return elicit_slot({}, 'DCA_investment', get_slots(intent_request), 'riskLevel',  str(get_btcprice()) )
        # Perform basic validation on the supplied input slots.
        # Use the elicitSlot dialog action to re-prompt
        # for the first violation detected.
        slots = get_slots(intent_request)
        if not validation_result["isValid"]:
            return elicit_slot(
                intent_request["sessionAttributes"],
                intent_request["currentIntent"]["name"],
                slots,
                validation_result["violatedSlot"],
                validation_result["message"],
            )
        # Fetch current session attibutes
        output_session_attributes = intent_request["sessionAttributes"]
        return delegate(output_session_attributes, get_slots(intent_request))
    #risk_level = loss(initial_investment,intent_request) 
    print(risk_level)
    # Get the initial investment recommendation
    riskLevel = {"simple": "10% DCA purchases monthly",
    "steady": "20% DCA investments monthly",
    "low": "30% DCA investments monthly",
    "medium": "40% DCA investments weekly",
    "high": "50% DCA investments daily",
    "yolo": "exceed 50% DCA investments daily"}
    initial_recommendation = riskLevel[risk_level.lower()]
    
    #Risk level peramiters  
    # "simple = 365"
    #"steady = 120"
    #"medium = 60"
    #"high = 30"
    #"Yolo = 1"
     
def riskEval(pricedifference,riskType,intent_request):
    message = ""
    if riskType == "1":
        message = "Would you like to make this payment once every 1 days."
    if riskType == "30":
        message = "Would you like to make this payment once every 30 days."
    if riskType == "60":
        message = "Would you like to make this payment once every 60 days."
    if riskType == "120":
        message = "Would you like to make this payment once every 120 days."
    if riskType == "365":
        message = "Would you like to make this payment once every 365 days."
    DCAcalc = pricedifference/float(riskType)
    DCAmessage =""" Here is your DCA calculation.
    {}{} 
    """.format(str(DCAcalc),message)
    return close(
        intent_request["sessionAttributes"],
       "Fulfilled",
        {"contentType": "PlainText", "content": DCAmessage})
        
        
        
     

def riskLevel(loss,intent_request):
     
     
    slots = get_slots(intent_request)
    risk_level = get_slots(intent_request)["riskLevel"]
    message =""" 
    {} Here is the difference what risk level would you like to use to break even?
    """.format(str(pricedifference))
    str(pricedifference)
    if currrentbtcprice > initial_investment:
        message = "Please use application when you are at a loss"
    return elicit_slot(
        intent_request["sessionAttributes"],
        intent_request["currentIntent"]["name"],
        slots,
       'riskType',
        {"contentType": "PlainText", "content": message})
         
         
         
   # currrentbtcprice = get_btcprice()
    #pricedifference = currrentbtcprice -  initial_investment
    #if currrentbtcprice < float(initial_investment):
       # return close(intent_request["sessionAttributes"], 'Fulfilled',
          #  {
               # "contentType": "PlainText",
               # "content": "Good job, please use this app when you're at a loss.",
           # }
       # )
    ### YOUR FINAL INVESTMENT RECOMMENDATION CODE ENDS HERE ###
    # Return a message with the initial recommendation based on the risk level.
    return close(
        intent_request["sessionAttributes"],
        "Fulfilled",
        {
            "contentType": "PlainText",
            "content": """{} thank you for your information;
            based on the risk level you defined, my recommendation is to choose an investment portfolio with {}
            """.format(
                first_name, initial_recommendation
            ),
        },
    )
def loss(initial_investment,intent_request):
    slots = get_slots(intent_request)
    risk_level = get_slots(intent_request)["riskLevel"]
    message =""" 
        {} Here is the difference what risk level would you like to use to break even?
    """.format(str(pricedifference(initial_investment)))
    currrentbtcprice = float(get_btcprice())
    if currrentbtcprice > float(initial_investment):
        message = "Please use application when you are at a loss"
    return elicit_slot(
            intent_request["sessionAttributes"],
            intent_request["currentIntent"]["name"],
            slots,
           'riskType',
            {"contentType": "PlainText", "content": message})
            
        ### YOUR DATA VALIDATION CODE STARTS HERE ###
def validate_data(age, investment_amount, intent_request):
    if age:
        age = int(age)
    if age is not None:
        if age < 0 or age > 65:
            return build_validation_result(
                False,
                "age",
                "You must be under 65 to use this service."
                "Please try again."
            )
    if investment_amount is not None:
        investment_amount = float(
            investment_amount
            )
        if investment_amount < 1000:
            return build_validation_result(
                False,
                "investmentAmount",
                "The amount to invest should be greater than $1000 USD."
                "Please provide a correct amount in USD to begin the DCA process.",
                )
    return build_validation_result(True, None, None)
    
    
### Intents Dispatcher ###

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """
    intent_name = intent_request["currentIntent"]["name"]
    # Dispatch to bot's intent handlers
    if intent_name == "DCA_investment":
        return recommend_portfolio(intent_request)
    raise Exception("Intent with name " + intent_name + " not supported")
### Main Handler ###
def lambda_handler(event, context):
    print(event)
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    return dispatch(event)