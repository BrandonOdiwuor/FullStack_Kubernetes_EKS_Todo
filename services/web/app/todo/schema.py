from marshmallow import Schema, fields

class TodoSchema(Schema):
    todoId = fields.Str(dump_only=True) # sort(range) key
    userId = fields.Str(dump_only=True) # partition(hash) key

    name = fields.Str(required=True)
    dueDate = fields.Str(required=True)
    done = fields.Bool(required=True)

    attachmentUrl = fields.URL(dump_only=True)

    createdAt = fields.Str(dump_only=True)