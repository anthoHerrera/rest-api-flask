"""Tags resource"""

from flask.views import MethodView
from flask_smorest import abort, Blueprint
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from schemas import TagSchema, TagAndItemSchema
from db import db
from models import TagModel, StoreModel, ItemModel

blp = Blueprint("tags", __name__, description="Operations on tags")


@blp.route("/store/<string:store_id>/tag")
class TagsInStore(MethodView):
    """Tags in store"""

    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        """Get all tags in a store"""
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all()

    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        """Create a new tag in a store"""
        if TagModel.query.filter(
            TagModel.name == tag_data["name"], TagModel.store_id == store_id
        ).first():
            abort(
                400,
                message=f"A tag with name '{tag_data['name']}' already exists.",
            )
        tag = TagModel(**tag_data, store_id=store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except IntegrityError:
            abort(
                400,
                message=f"A tag with name '{tag_data['name']}' already exists.",
            )
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag


@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView):
    """Link tags to an item"""

    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        """Link a tag to an item"""
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag

    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        """Unlink a tag from an item"""
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return {"message": "Item unlinked from tag", "item": item, "tag": tag}


@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    """Tag resource"""

    @blp.response(200, TagSchema)
    def get(self, tag_id):
        """Get a specific tag"""
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(
        202,
        description="Deletes a tag if no item is tagged with it",
        example={"message": "Tag deleted"},
    )
    @blp.alt_response(404, description="Tag not found")
    @blp.alt_response(
        400,
        description="Returned if the tag is assigned to one or more items. "
        "In this case, the tag is not deleted",
    )
    def delete(self, tag_id):
        """Delete a tag"""
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted"}
        abort(
            400,
            message="The tag is assigned to one or more items. Therefore, it cannot be deleted.",
        )
