import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
ADMINS_TABLE = os.environ['ADMINS_TABLE']
table = dynamodb.Table(ADMINS_TABLE)

def lambda_handler(event, context):
    try:
        # Obtener el userID desde los parámetros de consulta
        user_id = event['queryStringParameters']['userID']

        if not user_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Falta el userID en los parámetros de consulta'})
            }

        # Buscar al usuario administrador por su userID
        response = table.get_item(Key={'userID': user_id})
        admin = response.get('Item')

        if not admin:
            return {
                'statusCode': 404,
                'body': json.dumps({'error': 'Administrador no encontrado'})
            }

        # Devolver los datos del administrador
        return {
            'statusCode': 200,
            'body': json.dumps(admin)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
