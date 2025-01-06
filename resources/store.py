"""Store resource"""

from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import StoreSchema
from models import StoreModel
from db import db

blp = Blueprint("stores", __name__, description="Operations on stores")


@blp.route("/store/<string:store_id>")
class Store(MethodView):
    """Store resource"""

    @blp.response(200, StoreSchema)
    def get(self, store_id):
        """Get a specific store"""
        store = StoreModel.query.get_or_404(store_id)
        return store

    def delete(self, store_id):
        """Delete a store"""
        store = StoreModel.query.get_or_404(store_id)
        try:
            db.session.delete(store)
            db.session.commit()
            return {"message": "Store deleted."}, 200
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the store.")


@blp.route("/store")
class StoreList(MethodView):
    """Store list resource"""

    @blp.response(200, StoreSchema(many=True))
    def get(self):
        """Get all stores"""
        return StoreModel.query.all()

    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        """Create a new store"""
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message=f"A store with name '{store_data['name']}' already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the store.")
        return store
