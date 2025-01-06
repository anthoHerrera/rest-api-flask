"""Item resource"""

from flask.views import MethodView
from flask_smorest import abort, Blueprint
from flask_jwt_extended import jwt_required, get_jwt
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import ItemSchema, ItemUpdateSchema
from db import db
from models import ItemModel

blp = Blueprint("items", __name__, description="Operations on items")


@blp.route("/item/<string:item_id>")
class Item(MethodView):
    """Item operations"""

    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id):
        """Get a specific item"""
        item = ItemModel.query.get_or_404(item_id)
        return item

    @jwt_required()
    def delete(self, item_id):
        """Delete an item"""
        jwt = get_jwt()
        if not jwt.get("is_admin"):
            abort(401, message="Admin privilege required.")
        item = ItemModel.query.get_or_404(item_id)
        try:
            db.session.delete(item)
            db.session.commit()
            return {"message": "Item deleted."}, 200
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the item.")

    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id):
        """Update an item"""
        item = ItemModel.query.get_or_404(item_id)

        if item:
            item.price = item_data["price"]
            item.name = item_data["name"]
        else:
            item = ItemModel(id=item_id, **item_data)

        try:
            db.session.add(item)
            db.session.commit()
            return item
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the item.")


@blp.route("/item")
class ItemList(MethodView):
    """Item list operations"""

    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """Get all items"""
        return ItemModel.query.all()

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        """Create a new item in a store"""
        item = ItemModel(**item_data)
        try:
            db.session.add(item)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message=f"An item with name '{item_data['name']}' already exists.",
            )

        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")
        return item
