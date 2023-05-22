from marshmallow import Schema, fields


class TicketSchema(Schema):
    id = fields.Integer(required=True)
    quantity = fields.Integer(default=1)
    price = fields.Float(allow_none=True)


class OrderAmountInputSchema(Schema):
    tickets = fields.Nested(TicketSchema, many=True)
    discount_code = fields.Integer(load_from='discount-code')
    amount = fields.Float(allow_none=True)
