import requests
import base64
import json
from datetime import datetime
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class MpesaClient:
    def __init__(self):
        # Check for required settings
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', None)
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', None)
        self.paybill = getattr(settings, 'MPESA_PAYBILL', None)
        self.passkey = getattr(settings, 'MPESA_PASSKEY', None)
        self.callback_url = getattr(settings, 'MPESA_CALLBACK_URL', None)
        
        # Base URLs
        self.base_url = "https://sandbox.safaricom.co.ke"
        
        # Validate required settings
        if not all([self.consumer_key, self.consumer_secret, self.paybill, self.passkey]):
            raise ImproperlyConfigured(
                "Missing M-Pesa configuration. Please ensure MPESA_CONSUMER_KEY, "
                "MPESA_CONSUMER_SECRET, MPESA_PAYBILL, and MPESA_PASSKEY are set in your settings."
            )
        
        try:
            self.access_token = self.get_access_token()
        except Exception as e:
            raise ImproperlyConfigured(
                f"Failed to get M-Pesa access token. Please check your credentials. Error: {str(e)}"
            )

    def get_access_token(self):
        """Get M-Pesa access token"""
        try:
            # Create auth string and encode it to base64
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_string.encode('ascii')
            encoded_auth = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                'Authorization': f'Basic {encoded_auth}',
                'Content-Type': 'application/json'
            }

            url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
            
            response = requests.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}: {response.text}")
            
            result = response.json()
            
            if 'access_token' not in result:
                raise Exception(f"Invalid response format: {result}")
            
            return result['access_token']
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to M-Pesa API: {str(e)}")
        except (KeyError, json.JSONDecodeError) as e:
            raise Exception(f"Invalid response from M-Pesa API: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}")

    def generate_password(self, timestamp):
        """Generate M-Pesa password"""
        data_to_encode = f"{self.paybill}{self.passkey}{timestamp}"
        return base64.b64encode(data_to_encode.encode()).decode()

    def initiate_stk_push(self, phone_number, amount, account_reference):
        """Initiate STK push payment"""
        if not self.callback_url:
            raise ImproperlyConfigured(
                "MPESA_CALLBACK_URL is not set. Please configure it in your settings."
            )
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            password = self.generate_password(timestamp)
            
            # Format phone number to required format (254XXXXXXXXX)
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            elif phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]
            elif not phone_number.startswith('254'):
                phone_number = '254' + phone_number
            
            payload = {
                "BusinessShortCode": self.paybill,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(float(amount)),
                "PartyA": phone_number,
                "PartyB": self.paybill,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": account_reference,
                "TransactionDesc": f"Payment for {account_reference}"
            }

            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }

            url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if 'ResponseCode' not in result:
                raise Exception(f"Invalid response format: {result}")
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to initiate M-Pesa payment: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid response from M-Pesa API: {str(e)}")
        except Exception as e:
            raise Exception(f"Unexpected error: {str(e)}") 