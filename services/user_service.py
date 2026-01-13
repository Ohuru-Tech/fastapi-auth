from fastapi import HTTPException

from repositories.user_repository import UserRepository
from schemas.user import (
    UserJWTResponseSchema,
    UserPasswordLoginSchema,
    UserSignupSchema,
)
from settings import Settings
from utils.jwt import generate_jwt_token
from utils.password import verify_password


class UserService:
    def __init__(self, repository: UserRepository, settings: Settings):
        self.repository = repository
        self.settings = settings

    async def social_login(self):
        pass

    async def log_user_in(
        self, user_login: UserPasswordLoginSchema
    ) -> UserJWTResponseSchema:
        user = await self.repository.get_user_by_email(email=user_login.email)

        # If the user deos not exist, raise an exception
        if not user:
            raise HTTPException(
                status_code=404, detail="No user exists with the given email."
            )

        # See if this is a passwordless login
        if self.settings.passwordless_login_enabled:
            await self.signup_user(user_signup=UserSignupSchema(email=user_login.email))

        if not user.password:
            raise HTTPException(status_code=400, detail="Password is required.")

        # Verify the password
        if not verify_password(
            password=user_login.password, hashed_password=user.password
        ):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generate a jwt for the user and return
        return generate_jwt_token(user=user, settings=self.settings)

    async def signup_user(self, user_signup: UserSignupSchema):
        user = self.repository.get_user_by_email(email=user_signup.email)

        # If passswordless is enabled just create the user
        if self.settings.passwordless_login_enabled:
            pass

        # If a user exists, raise an exception
        if user:
            raise HTTPException(status_code=400, detail="User already exists.")

        # If email verification is required, send a verification email
        if self.settings.email_verification_required:
            pass

        # Create the user
        await self.repository.create_user(user=user_signup)

        # Generate a jwt for the user and return
        return generate_jwt_token(user=user, settings=self.settings)
