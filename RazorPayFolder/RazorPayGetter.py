import requests
import razorpay
from simple_salesforce import Salesforce as sf
class razorPayConnector:
    def __init__(self, key_id, key_secret):
        self.key_id = key_id
        self.key_secret = key_secret
    
    def getEmiDetails(self, payment_id):
        # Implement the logic to connect to Razorpay API and fetch EMI details for the given payment_id
        # You can use the Razorpay Python SDK or make direct API calls using requests library
        end_point = f"https://api.razorpay.com/v1/payments/{payment_id}"
        
        json_details = {}
        try:
            client = razorpay.Client(auth=(self.key_id, self.key_secret))
        
            response = client.payment.fetch("pay_JqLHMVryzMEafT",{"expand[]":"emi"})
            
            print('response', response)
            return response
            response.raise_for_status()  # Check if the request was successful``
            
            
            respone_json = response.json()
            
            if respone_json:
                json_details['id'] = respone_json.get('id')
                # Check for currentl
                if respone_json.get('currency') == 'INR':
                    json_details['Recieved_Amount__c'] = respone_json.get('amount_captured') /100 # Convert from paise to rupees
                else:
                    pass
                json_details['Emi_Issuer__c'] = respone_json.get('emi').get('issuer')
                json_details['Tenure__c'] = respone_json.get('emi').get('duration')
                json_details['Actual_Fee'] = respone_json.get('notes').get('Actual_Fee')
                json_details['Interest_Amount__c'] = json_details.get('Actual_Fee') - json_details.get( 'Recieved_Amount__c')
                json_details['Interest_Percentage__c'] = (json_details.get('Interest_Amount__c') /  json_details.get('Actual_Fee'))* 100
                json_details['Card_Type__c'] = respone_json.get('emi').get('card_type')
            
            return json_details
                
        except requests.exceptions.RequestException as e:
            print(f"Error fetching EMI details: {e}")
            

key_id = 'rzp_live_AsYUw4vcV3qqtt'
key_secret  =   'mgJFOjUmDvTkL1zTifVV0d3m'
razorPayConnector(key_id, key_secret).getEmiDetails('pay_3M9n2sH8qj5v1X')
            
    
    
        
        
    