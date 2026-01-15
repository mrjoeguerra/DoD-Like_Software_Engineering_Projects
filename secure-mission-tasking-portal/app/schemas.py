from marshmallow import Schema, fields, validate


class LoginSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1, max=80))
    password = fields.Str(required=True, validate=validate.Length(min=8, max=128))


class TaskCreateSchema(Schema):
    title = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    priority = fields.Str(required=False, validate=validate.OneOf(["low", "medium", "high"]))
    assigned_to = fields.Str(required=False, allow_none=True, validate=validate.Length(max=80))


class TaskUpdateSchema(Schema):
    title = fields.Str(required=False, validate=validate.Length(min=3, max=200))
    description = fields.Str(required=False, allow_none=True, validate=validate.Length(max=5000))
    priority = fields.Str(required=False, validate=validate.OneOf(["low", "medium", "high"]))
    status = fields.Str(required=False, validate=validate.OneOf(["open", "in_progress", "closed"]))
    assigned_to = fields.Str(required=False, allow_none=True, validate=validate.Length(max=80))
