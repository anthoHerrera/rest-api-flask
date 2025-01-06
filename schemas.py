"""Schemas for the items"""

from marshmallow import Schema, fields


class PlainItemSchema(Schema):
    """Plain item schema"""

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)


class PlainStoreSchema(Schema):
    """Plain store schema"""

    id = fields.Str(dump_only=True)
    name = fields.Str()


class PlainTagSchema(Schema):
    """Plain tag schema"""

    id = fields.Str(dump_only=True)
    name = fields.Str()


class ItemSchema(PlainItemSchema):
    """Schema for items"""

    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class ItemUpdateSchema(Schema):
    """Schema for updating items"""

    name = fields.Str()
    price = fields.Float()


class StoreSchema(PlainStoreSchema):
    """Schema for stores"""

    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)


class TagSchema(PlainTagSchema):
    """Schema for tags"""

    store_id = fields.Int(required=True, load_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)


class TagAndItemSchema(Schema):
    """Schema for tag and item"""

    message = fields.Str()
    item = fields.Nested(ItemSchema)
    tag = fields.Nested(TagSchema)


class UserSchema(Schema):
    """Schema for users"""

    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)
