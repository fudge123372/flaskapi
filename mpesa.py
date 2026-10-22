import requests
from datetime import datetime
import base64
from requests.auth import HTTPBasicAuth 
import math

consumer_key='vNLMJ2c8OUNKnYJruMrOB1eoAtPljq48lnqc3bw6uFnEL7sT'
consumer_secret='FWXiXQ5mESHcDEl2pxgbmnG8VHM68MnDpBroFUJD0oy8je08DaQUBUgx9oRwp0AU'
saf_api_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
saf_short_code='174379'
saf_pass_key='bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
saf_stkpush_api='https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
my_callback_url='https://ferret-sacrament-theater.ngrok-free.dev/saf-callback'



def generate_password_and_timestamp():
    timestamp=datetime.now().strftime("%Y%m%d%H%M%S")
    password_str = saf_short_code + saf_pass_key + timestamp
    password_bytes = password_str.encode()
    password=base64.b64encode(password_bytes).decode("utf-8")
    return password,timestamp

def get_access_token():
    try:
        res=requests.get(
            saf_api_url,
            auth=HTTPBasicAuth(consumer_key,consumer_secret),
            timeout=30
        )

        res.raise_for_status()# detects HTTP error,such as invalid credentials.
        return res.json()["access_token"]# returns the token when the request succeeds
    except Exception as e:
        print(str(e),"error getting access token")
        raise e #passes the error back to the code that called this function,so it can handle the failure

def make_stk_push(payload):
    amount = payload['amount']
    phone_number=payload['phone_number']
    sale_id=payload.get("sale_id")

    #dynamilly generate token and password on every push

    token = get_access_token()
    headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
    }

    password,timestamp = generate_password_and_timestamp()

    push_data = {
    "BusinessShortCode": saf_short_code,
    "Password": password,
    "Timestamp": timestamp,
    "TransactionType": "CustomerPayBillOnline",
    "Amount": math.ceil(float(amount)),
    "PartyA": phone_number,
    "PartyB": saf_short_code,
    "PhoneNumber": phone_number,
    "CallBackURL": my_callback_url,
    "AccountReference": str(sale_id),
    "TransactionDesc": "Sale payment"
    }

    response=requests.post(
        saf_stkpush_api,
        json=push_data,
        headers=headers,
        timeout=30
    )
    response.raise_for_status()# checks HTTP errors 
# attempts to read saf's response as JSON
    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:#handles response that cannot be decoded as JSON
        return{
            "Error":"response was not JSON",
            "status_code": response.status_code
        }

