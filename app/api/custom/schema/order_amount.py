from marshmallow import Schema, fields


class TicketSchema(Schema):
    id = fields.Integer(required=True)
    quantity = fields.Integer(default=1)
    quantity_discount = fields.Integer(allow_none=True)
    price = fields.Float(allow_none=True)


class OrderAmountInputSchema(Schema):
    tickets = fields.Nested(TicketSchema, many=True)
    discount_code = fields.Integer(load_from='discount-code')
    access_code = fields.Integer(load_from='access-code')
    amount = fields.Float(allow_none=True)
    discount_verify = fields.Boolean(
        required=False, default=True, load_from='discount-verify'
    )
