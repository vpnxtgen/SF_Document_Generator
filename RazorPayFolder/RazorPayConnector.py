import razorpay
from simple_salesforce import Salesforce as sf
import json
class RazorPayConnector:
    def __init__(self, key_id, key_secret):
        self.key_id = key_id
        self.key_secret = key_secret
        self.client = razorpay.Client(auth=(self.key_id, self.key_secret))

    def get_emi_details(self, payment_id):
        if not payment_id.startswith("pay_"):
            raise ValueError(f"Invalid payment_id format: {payment_id}")

        json_details = {}

        try:
            # Fix 1: Razorpay SDK's fetch() doesn't support expand[] via params dict.
            # Use requests directly with the param hardcoded in the URL to avoid %5B%5D encoding.
            import requests
            endpoint = f"https://api.razorpay.com/v1/payments/{payment_id}?expand"+"[" + "]" +"=emi"
            response = requests.get(endpoint, auth=(self.key_id, self.key_secret))

            if not response.ok:
                print(f"Status: {response.status_code}, Error: {response.text}")
                response.raise_for_status()

            response_json = response.json()

            # Fix 2: Removed unreachable code (you had `return` before `raise_for_status`)
            if response_json:
                json_details['id'] = response_json.get('id')

                # Fix 3: Default to 0 to avoid TypeError in math operations
                if response_json.get('currency') == 'INR':
                    json_details['Recieved_Amount__c'] = response_json.get('amount_captured', 0) / 100
                else:
                    json_details['Recieved_Amount__c'] = 0  # Fix 4: bare `pass` left key undefined
                    return

                # Fix 5: Guard against missing 'emi' key
                emi = response_json.get('emi') or {}
                json_details['Emi_Issuer__c'] = emi.get('issuer')
                json_details['Tenure__c'] = emi.get('duration')
                json_details['Card_Type__c'] = emi.get('type')
                json_details['Payment_Method__c'] = 'No Cost EMI'

                # Fix 6: Guard against missing 'notes' key + safely cast to float
                notes = response_json.get('notes') or {}
                try:
                    actual_fee = float(notes.get('Actual_Fee', 0))
                except (TypeError, ValueError):
                    actual_fee = 0.0

                json_details['Actual_Fee'] = actual_fee
                received = json_details.get('Recieved_Amount__c', 0)

                # Fix 7: Guard against ZeroDivisionError
                if actual_fee > 0:
                    json_details['Interest_Amount__c'] = round(actual_fee - received, 2)
                    json_details['Interest_Percentage__c'] = round(json_details['Interest_Amount__c'] / actual_fee * 100, 2)
                else:
                    json_details['Interest_Amount__c'] = 0
                    json_details['Interest_Percentage__c'] = 0

            return json_details

        except Exception as e:
            print(f"Error fetching EMI details: {e}")
            return {}
        


class salesForceConnector:
    connection = None
    def __init__(self, username, password, security_token):
        self.username = username
        self.password = password
        self.security_token = security_token
        # Initialize Salesforce connection here (e.g., using simple_salesforce library)
        
   
    def connect(self):
        """Establishes the connection to Salesforce."""
        username = self.username #os.getenv(const.SF_VIK_1)
        password = self.password #os.getenv(const.SF_PASS_1)
        security_token = self.security_token #  os.getenv(const.SF_TOKEN_1)
        print("Attempting to connect to Salesforce..." + username)
        try:
            self.connection = sf(
                username=username, 
                password=password, 
                security_token=security_token
            )
            print("Connected to Salesforce successfully.")
        except Exception as e:
            print(f"Failed to connect: {e}")
    
    def upsertDataIntoSf(self, json_data):
        """Upserts data. Note: json_data should be a single dict for standard upsert."""
        # Ensure we have a connection before proceeding
        if not self.connection:
            self.connect()

        try:
            # simple-salesforce upsert returns a status code (e.g., 201 or 204)
            # and potentially a body, but it doesn't return a list to iterate over 
            # unless you are using the Bulk API.
            
            for key,value in json_data.items():
                ext_id = key
                sf_record = json_data.get(ext_id)
                sf_record.pop('Actual_Fee')
                sf_record.pop('id')
                if not ext_id:
                    print("Skipping record with missing ID")
                    continue
                
                result = self.connection.Payment__c.upsert( f'Payment_ID__c/{ext_id}', sf_record)
                
            
            # For standard REST API upsert:
            # 201 = Created, 204 = Updated
            if 200 <= result <= 299:
                print(f"Upsert successful. Status Code: {result}")
            else:
                print(f"Upsert returned unexpected status: {result}")
                
        except Exception as e:
            print(f"Upsert failed: {e}")
        
        


# Never hardcode credentials — use environment variables instead
import os
key_id = 'RAZORPAY_KEY_ID'
key_secret = "RAZORPAY_KEY_SECRET"


payment_ids = [
    "pay_SXk1Lm2oZuwysj",
    "pay_SXkTZ8pvPpAbj2",
    "pay_SXjjRrK6LuJSnQ",
    "pay_SXj2SQBZX987DT",
    "pay_SXgG4CH9aCtjJ9",
    "pay_SXeygl1qwewqwi",
    "pay_SXjh9kmAosVplf",
    "pay_SXYdDvUATC24dC",
    "pay_SXise4qUyd9qxo",
    "pay_SXjsfd8XTvJeWy",
    "pay_SXipflcNQa4heR"
]


json_details = {}
for i in range(len(payment_ids)):
    connector = RazorPayConnector(key_id, key_secret)
    result = connector.get_emi_details(payment_ids[i])
    if result.get('id') == payment_ids[i] : 
        json_details[payment_ids[i]] = result
        print(result.get('id'))


sfc = salesForceConnector('passUserName','password','securitytoken')
sfc.upsertDataIntoSf(json_details)

