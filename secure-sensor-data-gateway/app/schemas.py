from marshmallow import Schema, fields, validate

class IngestSchema(Schema):
    type = fields.Str(required=True, validate=validate.OneOf(["position", "status", "telemetry"]))
    payload = fields.Dict(required=True)
