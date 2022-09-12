from flask import Blueprint, jsonify, request, current_app
from marshmallow import ValidationError

from app.auth import require_auth
from app.todo.schema import TodoSchema
from app.todo.todos import create_todo, delete_todo, get_todo, get_user_todos, update_todo


todo = Blueprint('todo', __name__)

todo_schema = TodoSchema()
todos_schema = TodoSchema(many=True)

@todo.route('/todos', methods=['GET'])
@require_auth
def fetch_user_todos(user, **kwargs):
    user_id = user['sub']
    todos = get_user_todos(user_id)
    todo_items = todos_schema.dump(todos)

    response = jsonify({'items': todo_items})
    response.status_code = 200
    current_app.logger.info("Fetched todos for user: %s", user_id)
    return response

@todo.route('/todos/<string:todo_id>', methods=['GET'])
@require_auth
def fetch_todo(user, **kwargs):
    user_id = user['sub']
    todo_id = kwargs['todo_id']
    todo = get_todo(user_id, todo_id)

    todo_item = todo_schema.dump(todo)

    response = jsonify({'item': todo_item})
    response.status_code = 200
    return response

@todo.route('/todos', methods=['POST'])
@require_auth
def add_todo(user, **kwargs):
    user_id = user['sub']
    json_data = request.get_json()
    try:
        todo_data = todo_schema.load(json_data)
    except ValidationError as err:
        current_app.logger.error("Validation error %s", err.messages)
        return err.messages, 422

    todo = create_todo(user_id, todo_data)
    todo_item = todo_schema.dump(todo)

    response = jsonify({'item': todo_item})
    response.status_code = 200
    return response

@todo.route('/todos/<string:todo_id>', methods=['PATCH'])
@require_auth
def patch_todo(user, **kwargs):
    user_id = user['sub']
    todo_id = kwargs['todo_id']
    json_data = request.get_json()
    try:
        todo_data = todo_schema.load(json_data)
    except ValidationError as err:
        current_app.logger.error("Validation error %s", err.messages)
        return err.messages, 422

    todo = update_todo(user_id, todo_id, todo_data)
    todo_item = todo_schema.dump(todo)

    response = jsonify({'item': todo_item})
    response.status_code = 200
    return response

@todo.route('/todos/<string:todo_id>', methods=['DELETE'])
@require_auth
def remove_todo(user, **kwargs):
    user_id = user['sub']
    todo_id = kwargs['todo_id']
    todo = delete_todo(user_id, todo_id)
    todo_item = todo_schema.dump(todo)

    response = jsonify({'item': todo_item})
    response.status_code = 200
    return response
