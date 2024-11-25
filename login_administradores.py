import boto3
import hashlib
import uuid
import os
import json
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        email = body.get('email')
        password = body.get('password')

        if not email or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing email or password'})
            }

        hashed_password = hash_password(password)
        dynamodb = boto3.resource('dynamodb')
        admins_table = dynamodb.Table(os.environ['ADMINS_TABLE'])
        tokens_table = dynamodb.Table('admin_tokens_acceso')

        response = admins_table.scan(FilterExpression=Attr('email').eq(email))
        items = response.get('Items', [])

        if not items:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Admin not found'})
            }

        item = items[0]
        if hashed_password == item['passwordHash']:
            token = str(uuid.uuid4())
            fecha_hora_exp = datetime.utcnow() + timedelta(minutes=60)
            tokens_table.put_item(Item={
                'token': token,
                'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S'),
                'user_id': item['userID']
            })
            return {'statusCode': 200, 'body': json.dumps({'token': token})}
        else:
            return {'statusCode': 403, 'body': json.dumps({'error': 'Password incorrecto'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
