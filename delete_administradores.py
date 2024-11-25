import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
ADMINS_TABLE = os.environ['ADMINS_TABLE']
table = dynamodb.Table(ADMINS_TABLE)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        user_id = body['userID']

        response = table.delete_item(Key={'userID': user_id})

        return {
            'statusCode': 204,
            'body': 'Admin eliminado'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
