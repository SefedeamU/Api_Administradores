import boto3
import uuid
import datetime
import hashlib
import os
import json
import logging
from boto3.dynamodb.conditions import Attr

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
ADMINS_TABLE = os.environ['ADMINS_TABLE']
table = dynamodb.Table(ADMINS_TABLE)
TOKENS_TABLE = 'admin_tokens_acceso'
tokens_table = dynamodb.Table(TOKENS_TABLE)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def lambda_handler(event, context):
    try:
        logger.info("Received event: %s", json.dumps(event))
        body = json.loads(event['body'])
        email = body.get('email')
        nombre = body.get('nombre')
        password = body.get('password')

        if not email or not nombre or not password:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Missing email, nombre, or password'})
            }

        response = table.scan(FilterExpression=Attr('email').eq(email))
        if response['Items']:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Email already exists'})
            }

        password_hash = hash_password(password)
        user_id = str(uuid.uuid4())
        fecha_creacion = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')

        admin = {
            'userID': user_id,
            'fechaCreacion': fecha_creacion,
            'nombre': nombre,
            'email': email,
            'passwordHash': password_hash,
            'ultimoAcceso': fecha_creacion
        }

        table.put_item(Item=admin)

        token = str(uuid.uuid4())
        fecha_hora_exp = datetime.datetime.utcnow() + datetime.timedelta(minutes=60)
        token_data = {
            'token': token,
            'expires': fecha_hora_exp.strftime('%Y-%m-%d %H:%M:%S'),
            'user_id': user_id
        }
        tokens_table.put_item(Item=token_data)

        return {
            'statusCode': 201,
            'body': json.dumps({
                'message': 'Admin creado',
                'userID': user_id,
                'fechaCreacion': fecha_creacion,
                'token': token
            })
        }
    except Exception as e:
        logger.error("Error creating admin: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
