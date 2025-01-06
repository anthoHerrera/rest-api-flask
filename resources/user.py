"""User resource"""

from flask.views import MethodView
from flask_smorest import abort, Blueprint
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from schemas import UserSchema
from models import UserModel
from db import db
from blocklist import BLOCKLIST


blp = Blueprint("users", __name__, description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    """Register a user"""

    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Register a user"""
        if UserModel.query.filter(UserModel.username == user_data["username"]).first():
            abort(
                400,
                message="A user with that username already exists.",
            )
        user = UserModel(
            username=user_data["username"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )
        try:
            db.session.add(user)
            db.session.commit()
            return {"message": "User created successfully."}, 201
        except IntegrityError:
            abort(400, message="A user with that username already exists.")
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the user.")


@blp.route("/login")
class UserLogin(MethodView):
    """Login a user"""

    @blp.arguments(UserSchema)
    def post(self, user_data):
        """Login a user"""
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        abort(
            401,
            message="Invalid credentials.",
        )


@blp.route("/logout")
class UserLogout(MethodView):
    """Logout a user"""

    @jwt_required()
    def post(self):
        """Logout a user"""
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


@blp.route("/user/<int:user_id>")
class User(MethodView):
    """Get a user"""

    @blp.response(200, UserSchema)
    def get(self, user_id):
        """Get a user"""
        user = UserModel.query.get_or_404(user_id)
        return user

    def delete(self, user_id):
        """Delete a user"""
        user = UserModel.query.get_or_404(user_id)
        try:
            db.session.delete(user)
            db.session.commit()
            return {"message": "User deleted."}, 200
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the user.")


@blp.route("/refresh")
class TokenRefresh(MethodView):
    """Refresh a user's access token"""
    @jwt_required(refresh=True)
    def post(self):
        """Refresh a user's access token"""
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"access_token": new_token}, 200
