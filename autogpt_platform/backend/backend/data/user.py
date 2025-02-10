import logging
from datetime import datetime, timedelta
from typing import Optional, cast

from autogpt_libs.auth.models import DEFAULT_USER_ID
from fastapi import HTTPException
from prisma import Json
from prisma.models import User

from backend.data.db import prisma
from backend.data.model import UserIntegrations, UserMetadata, UserMetadataRaw
from backend.data.notifications import NotificationPreference
from backend.util.encryption import JSONCryptor

logger = logging.getLogger(__name__)


async def get_or_create_user(user_data: dict) -> User:
    user_id = user_data.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    user_email = user_data.get("email")
    if not user_email:
        raise HTTPException(status_code=401, detail="Email not found in token")

    user = await prisma.user.find_unique(where={"id": user_id})
    if not user:
        user = await prisma.user.create(
            data={
                "id": user_id,
                "email": user_email,
                "name": user_data.get("user_metadata", {}).get("name"),
            }
        )
    return User.model_validate(user)


async def get_user_by_id(user_id: str) -> User:
    user = await prisma.user.find_unique(where={"id": user_id})
    if not user:
        raise ValueError(f"User not found with ID: {user_id}")
    return User.model_validate(user)


async def create_default_user() -> Optional[User]:
    user = await prisma.user.find_unique(where={"id": DEFAULT_USER_ID})
    if not user:
        user = await prisma.user.create(
            data={
                "id": DEFAULT_USER_ID,
                "email": "default@example.com",
                "name": "Default User",
            }
        )
    return User.model_validate(user)


async def get_user_metadata(user_id: str) -> UserMetadata:
    user = await User.prisma().find_unique_or_raise(
        where={"id": user_id},
    )

    metadata = cast(UserMetadataRaw, user.metadata)
    return UserMetadata.model_validate(metadata)


async def update_user_metadata(user_id: str, metadata: UserMetadata):
    await User.prisma().update(
        where={"id": user_id},
        data={"metadata": Json(metadata.model_dump())},
    )


async def get_user_integrations(user_id: str) -> UserIntegrations:
    user = await User.prisma().find_unique_or_raise(
        where={"id": user_id},
    )

    encrypted_integrations = user.integrations
    if not encrypted_integrations:
        return UserIntegrations()
    else:
        return UserIntegrations.model_validate(
            JSONCryptor().decrypt(encrypted_integrations)
        )


async def update_user_integrations(user_id: str, data: UserIntegrations):
    encrypted_data = JSONCryptor().encrypt(data.model_dump())
    await User.prisma().update(
        where={"id": user_id},
        data={"integrations": encrypted_data},
    )


async def migrate_and_encrypt_user_integrations():
    """Migrate integration credentials and OAuth states from metadata to integrations column."""
    users = await User.prisma().find_many(
        where={
            "metadata": {
                "path": ["integration_credentials"],
                "not": Json({"a": "yolo"}),  # bogus value works to check if key exists
            }  # type: ignore
        }
    )
    logger.info(f"Migrating integration credentials for {len(users)} users")

    for user in users:
        raw_metadata = cast(UserMetadataRaw, user.metadata)
        metadata = UserMetadata.model_validate(raw_metadata)

        # Get existing integrations data
        integrations = await get_user_integrations(user_id=user.id)

        # Copy credentials and oauth states from metadata if they exist
        if metadata.integration_credentials and not integrations.credentials:
            integrations.credentials = metadata.integration_credentials
        if metadata.integration_oauth_states:
            integrations.oauth_states = metadata.integration_oauth_states

        # Save to integrations column
        await update_user_integrations(user_id=user.id, data=integrations)

        # Remove from metadata
        raw_metadata = dict(raw_metadata)
        raw_metadata.pop("integration_credentials", None)
        raw_metadata.pop("integration_oauth_states", None)

        # Update metadata without integration data
        await User.prisma().update(
            where={"id": user.id},
            data={"metadata": Json(raw_metadata)},
        )


async def get_active_user_ids_in_timerange(start_time: str, end_time: str) -> list[str]:
    users = await User.prisma().find_many(
        where={
            "AgentGraphExecutions": {
                "some": {
                    "createdAt": {
                        "gte": datetime.fromisoformat(start_time),
                        "lte": datetime.fromisoformat(end_time),
                    }
                }
            }
        },
    )
    return [user.id for user in users]


async def get_active_users_ids() -> list[str]:
    user_ids = await get_active_user_ids_in_timerange(
        (datetime.now() - timedelta(days=30)).isoformat(),
        datetime.now().isoformat(),
    )
    return user_ids


async def get_user_notification_preference(user_id: str) -> NotificationPreference:
    user = await User.prisma().find_unique_or_raise(
        where={"id": user_id},
        include={
            "UserNotificationPreference": True,
        },
    )
    notification_preference = NotificationPreference(
        user_id=user.id,
        email=user.email,
        # TODO with the UI when it comes in
        preferences={},
        daily_limit=3,
        emails_sent_today=0,
        last_reset_date=datetime.now(),
    )
    return NotificationPreference.model_validate(notification_preference)
