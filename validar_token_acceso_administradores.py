import boto3
import json
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
TOKENS_TABLE = 'admin_tokens_acceso'
tokens_table = dynamodb.Table(TOKENS_TABLE)

def lambda_handler(event, context):
    try:
        token = event['queryStringParameters']['token']
        response = tokens_table.get_item(Key={'token': token})
        item = response.get('Item')

        if not item:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Token no válido'})
            }

        expires = datetime.strptime(item['expires'], '%Y-%m-%d %H:%M:%S')
        if datetime.utcnow() > expires:
            return {
                'statusCode': 403,
                'body': json.dumps({'error': 'Token expirado'})
            }

        return {'statusCode': 200, 'body': json.dumps({'message': 'Token válido'})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
