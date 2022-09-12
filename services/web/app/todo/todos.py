from uuid import uuid4
from boto3 import resource
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key
from flask import current_app

TABLE_NAME = 'Todos-dev'

dynamodb = resource('dynamodb')
dynamodb_table = dynamodb.Table(TABLE_NAME)

def get_user_todos(user_id):
    try:
        response = dynamodb_table.query(
            KeyConditionExpression=Key('userId').eq(user_id)
        )
    except ClientError as err:
        current_app.logger.error(
            "Couldn't get todos for user %s from table %s. Here's why: %s: %s",
            user_id, dynamodb_table.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as ex:
        current_app.logger.error(
            "Couldn't get todos for user %s from table %s. Here's why: %s: ",
            user_id, dynamodb_table.name, ex)
        raise
    else:
        return response['Items']

def get_todo(user_id, todo_id):
    try:
        response = dynamodb_table.get_item(Key={'userId': user_id, 'todoId': todo_id})
    except ClientError as err:
        current_app.logger.error(
            "Couldn't get todos for user %s with id: %s from table %s. Here's why: %s: %s",
            user_id, todo_id, dynamodb_table.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as ex:
        current_app.logger.error(
            "Couldn't get todos for user %s from table %s. Here's why: %s: ",
            user_id, dynamodb_table.name, ex)
        raise
    else:
        return response['Item']

def create_todo(user_id, todo_data):
    todo_id = uuid4()
    try:
        todo_item = {
            'userId': user_id, 
            'todoId': str(todo_id),
            **todo_data
        }
        dynamodb_table.put_item(Item=todo_item)
    except ClientError as err:
        current_app.logger.error(
            "Couldn't add todo for user %s to table %s. Here's why: %s: %s",
            user_id, dynamodb_table.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as ex:
        current_app.logger.error(
            "Couldn't add todo for user %s to table %s. Here's why: %s: ",
            user_id, dynamodb_table.name, ex)
        raise
    else:
        return todo_item

def update_todo(user_id, todo_id, todo_data):
    try:
        response = dynamodb_table.update_item(
            Key={'userId': user_id, 'todoId': todo_id},
            UpdateExpression="set #name=:name, #dueDate=:dueDate, #done=:done",
            ExpressionAttributeNames={
                "#name": "name",
                "#dueDate": "dueDate",
                "#done": "done",
            },
            ExpressionAttributeValues={
                ':name': todo_data['name'],
                ':dueDate': todo_data['dueDate'],
                ':done': todo_data['done']
            },
            ReturnValues='UPDATED_NEW'
        )
    except ClientError as err:
        current_app.logger.error(
            "Couldn't update todo for user %s to table %s. Here's why: %s: %s",
            user_id, dynamodb_table.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as ex:
        current_app.logger.error(
            "Couldn't update todo for user %s to table %s. Here's why: %s: ",
            user_id, dynamodb_table.name, ex)
        raise
    else:
        return response['Attributes']

def delete_todo(user_id, todo_id):
    try:
        response = dynamodb_table.delete_item(
            Key={'userId': user_id, 'todoId': todo_id},
            ReturnValues='ALL_OLD'
        )
    except ClientError as err:
        current_app.logger.error(
            "Couldn't delete todo for user %s to table %s. Here's why: %s: %s",
            user_id, dynamodb_table.name,
            err.response['Error']['Code'], err.response['Error']['Message'])
        raise
    except Exception as ex:
        current_app.logger.error(
            "Couldn't delete todo for user %s to table %s. Here's why: %s: ",
            user_id, dynamodb_table.name, ex)
        raise
    else:
        return response['Attributes']