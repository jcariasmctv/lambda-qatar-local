import os 
import requests
import json
import boto3


S3_BUCKET = os.environ['S3_BUCKET']
LANDING_PAGE = os.environ['LANDING_PAGE']
MEDIASTREAM_ID = os.environ['MEDIASTREAM_ID']
SECRET_NAME = os.environ['SECRET_NAME']
REGION = "us-east-1"



def hello(event, context):
    
    access_token = get_token()
    file_content = get_s3_content()
    
    body = file_content.replace('CCCCCCCCCCCCCCC',MEDIASTREAM_ID)
    body = body.replace('XXXXXXXXXXXXXXX',access_token)
    #body = body.replace('partidos.gol.caracoltv.com','caracol-test-bucket.s3.amazonaws.com')
    
    
    response = {
        'statusCode': 200,
        'headers': {"Content-Type": "text/html",},
        'body': body
    }
    
    return response


def get_s3_content():
    
    s3_client = boto3.client("s3")
    file_content = s3_client.get_object(
      Bucket=S3_BUCKET, Key=LANDING_PAGE)["Body"].read().decode("utf-8")
      
     
    return file_content  
    


def get_secret():
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=REGION
    )   
    
    get_secret_value_response = client.get_secret_value(
        SecretId = SECRET_NAME
    )

    secret_response = get_secret_value_response['SecretString']
    secret_response_json = json.loads(secret_response)
    
    return secret_response_json['api-authorization-token']
 
    

def get_token():
    
    authorization_token = get_secret()
    url = 'https://platform.mediastre.am/api/access/issue'
    payload = {'id': MEDIASTREAM_ID, 'type': 'live', 'token': authorization_token, 'max_use': '1' } # for post

    response = requests.post(url, json=payload)


    if response.status_code == 200:
        response_json = response.json()
        access_token = response_json['access_token']
        
        print(response_json)
        
        return access_token
        