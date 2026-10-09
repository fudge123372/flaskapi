import requests
from datetime import datetime
import base64
from requests.auth import HTTPBasicAuth 
import mathgit status
git init

consumer_key='vNLMJ2c8OUNKnYJruMrOB1eoAtPljq48lnqc3bw6uFnEL7sT'
consumer_secret='FWXiXQ5mESHcDEl2pxgbmnG8VHM68MnDpBroFUJD0oy8je08DaQUBUgx9oRwp0AU'
saf_api_url='https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type-client_credentials'
saf_short_code='174379'
saf_pass_key='bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
saf_stkpush_api='https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
my_callback_url='https://ferret-sacrament-theater.ngrok-free.dev/saf-callback'



def generate_password_and_timestamp():
    timestamp=datetime.now().strftime("%Y%m%d%H%M%S")
    password-str=saf_short_code + saf_pass_key +timestamp
    password_bytes=password_str.encode()
    password=base64.b64encode(password_bytes).decode("utf-8")
    return password,timestamp

def get_access_token():
    try:
        res=requests.get(
            saf_api_url,
            auth=HTTPBasicAuth(consumer_key,consumer_secret),
        )
        return res.json()["access_token"]
    except Exception as e:
        print(str(e),"error getting access token")
        raise e

def make_stk_push(payload):
    amount = payload['amount']
    phone_number=payload['phone_number']
    sale_id=payload.get(sale_id)

    #dynamilly generate token and password on every push

    token = get_mpesa_access_token()
    headers ={
        "Authorization ":f"Bearer{token}",
        "Content-Type":"Application/json"
    }

    password,timestamp = generate_password_and_timestamp()

    push_data = {
        "BussinessShotCode": saf_short_code,
        "Password":password,
        "Timestamp":timestamp,
        "TransactionType":"CustomerPayBillOnline",
        "Amount":math.ceil(float(amount)),
        "PartyA":phone_number,
        "PartyB":saf_short_code,
        "PhoneNumber":phone_number,
        "CallBackUrl":my_callback_url,
        "AcoountReference":str(payload.get('sale_id')),
        "TransactionDesc":"description of transaction"
    }

    response=requests.post(
        saf_stkpush_api,
        json=push_data,
        headers=headers)
    return response.json()

