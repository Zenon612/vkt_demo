# db/repositories.py

from sqlalchemy import select, delete, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.models import *
from typing import Optional, List
from dataclasses import dataclass


# ================= DTO =================

@dataclass
class UserDTO:
    tg_user_id: int
    vk_access_token: Optional[str] = None
    vk_user_id: Optional[int] = None
    filter_city_name: Optional[str] = None
    filter_gender: Optional[int] = None
    filter_age_from: Optional[int] = None
    filter_age_to: Optional[int] = None
    history_cursor: int = 0


@dataclass
class ProfileDTO:
    vk_user_id: int
    first_name: str = ""
    last_name: str = ""
    profile_url: str = ""


@dataclass
class PhotoDTO:
    photo_id: int
    owner_id: int
    url: str
    likes_count: int = 0
    local_path: Optional[str] = None
    status: str = "raw"


# ================= REPO =================

class SQLAlchemyUserRepo:

    def __init__(self, session: AsyncSession):
        self.session = session

# ---------------- USER ----------------

    async def get_or_create_user(self, tg_user_id: int) -> UserDTO:

        stmt = select(TgUser).where(TgUser.tg_user_id == tg_user_id)
        result = await self.session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = TgUser(tg_user_id=tg_user_id)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)

        return UserDTO(
            tg_user_id=user.tg_user_id,
            vk_access_token=user.vk_access_token,
            vk_user_id=user.vk_user_id,
            filter_city_name=user.filter_city_name,
            filter_gender=user.filter_gender,
            filter_age_from=user.filter_age_from,
            filter_age_to=user.filter_age_to,
            history_cursor=user.history_cursor,
        )

# ---------------- FAVORITES ----------------

    async def add_favorite(self, tg_user_id: int, vk_profile_id: int) -> None:
        stmt = insert(FavoriteProfile).values(
            tg_user_id=tg_user_id,
            vk_profile_id=vk_profile_id,
        ).on_conflict_do_nothing()

        await self.session.execute(stmt)
        await self.session.commit()

    async def remove_favorite(self, tg_user_id: int, vk_profile_id: int) -> None:
        await self.session.execute(
            delete(FavoriteProfile).where(
                FavoriteProfile.tg_user_id == tg_user_id,
                FavoriteProfile.vk_profile_id == vk_profile_id,
            )
        )
        await self.session.commit()

    async def list_favorites(self, tg_user_id: int) -> list[int]:
        stmt = select(FavoriteProfile.vk_profile_id).where(
            FavoriteProfile.tg_user_id == tg_user_id
        )
        result = await self.session.execute(stmt)
        return sorted(result.scalars().all())

# ---------------- BLACKLIST ----------------

    async def add_blacklist(self, tg_user_id: int, vk_profile_id: int) -> None:
        stmt = insert(BlacklistProfile).values(
            tg_user_id=tg_user_id,
            vk_profile_id=vk_profile_id,
        ).on_conflict_do_nothing()

        await self.session.execute(stmt)
        await self.session.commit()

# ---------------- QUEUE ----------------

    async def set_queue(self, tg_user_id: int, vk_ids: list[int]) -> None:

        await self.session.execute(
            delete(SearchQueue).where(SearchQueue.tg_user_id == tg_user_id)
        )

        for pos, vk_id in enumerate(vk_ids):
            self.session.add(
                SearchQueue(
                    tg_user_id=tg_user_id,
                    vk_profile_id=vk_id,
                    position=pos,
                )
            )

        await self.session.execute(
            update(TgUser)
            .where(TgUser.tg_user_id == tg_user_id)
            .values(history_cursor=0)
        )

        await self.session.commit()

    async def get_queue(self, tg_user_id: int) -> list[int]:
        stmt = select(SearchQueue.vk_profile_id).where(
            SearchQueue.tg_user_id == tg_user_id
        ).order_by(SearchQueue.position)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_current_vk_id(self, tg_user_id: int) -> int | None:

        user = await self.get_or_create_user(tg_user_id)

        stmt = select(SearchQueue.vk_profile_id).where(
            SearchQueue.tg_user_id == tg_user_id,
            SearchQueue.position == user.history_cursor,
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def move_next(self, tg_user_id: int) -> int | None:

        user = await self.get_or_create_user(tg_user_id)

        queue = await self.get_queue(tg_user_id)

        if not queue:
            return None

        if user.history_cursor < len(queue) - 1:
            user.history_cursor += 1

            await self.session.execute(
                update(TgUser)
                .where(TgUser.tg_user_id == tg_user_id)
                .values(history_cursor=user.history_cursor)
            )
            await self.session.commit()

        return queue[user.history_cursor]

    async def move_prev(self, tg_user_id: int) -> int | None:

        user = await self.get_or_create_user(tg_user_id)

        if user.history_cursor <= 0:
            return None

        user.history_cursor -= 1

        await self.session.execute(
            update(TgUser)
            .where(TgUser.tg_user_id == tg_user_id)
            .values(history_cursor=user.history_cursor)
        )
        await self.session.commit()

        return await self.get_current_vk_id(tg_user_id)

    async def update_filters(
        self,
        tg_user_id: int,
        city: str,
        gender: int,
        age_from: int,
        age_to: int,
    ) -> None:

        await self.get_or_create_user(tg_user_id)

        await self.session.execute(
            update(TgUser)
            .where(TgUser.tg_user_id == tg_user_id)
            .values(
                filter_city_name=city,
                filter_gender=gender,
                filter_age_from=age_from,
                filter_age_to=age_to,
                history_cursor=0,
            )
        )

        await self.session.commit()

    async def get_cursor(self, tg_user_id: int) -> int:

        stmt = select(TgUser.history_cursor).where(
            TgUser.tg_user_id == tg_user_id
        )

        result = await self.session.execute(stmt)
        cursor = result.scalar_one_or_none()

        return cursor if cursor is not None else 0

    async def set_cursor(self, tg_user_id: int, cursor: int) -> None:

        await self.get_or_create_user(tg_user_id)

        await self.session.execute(
            update(TgUser)
            .where(TgUser.tg_user_id == tg_user_id)
            .values(history_cursor=cursor)
        )

        await self.session.commit()

    async def upsert_profile(self, profile: ProfileDTO) -> None:

        stmt = insert(VkProfile).values(
            vk_user_id=profile.vk_user_id,
            first_name=profile.first_name,
            last_name=profile.last_name,
            profile_url=profile.profile_url,
        ).on_conflict_do_update(
            index_elements=[VkProfile.vk_user_id],
            set_={
                "first_name": profile.first_name,
                "last_name": profile.last_name,
                "profile_url": profile.profile_url,
            },
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def set_photos(self, vk_user_id: int, photos: list[PhotoDTO]) -> None:

        await self.session.execute(
            delete(VkPhoto).where(VkPhoto.vk_user_id == vk_user_id)
        )

        for p in photos:
            self.session.add(
                VkPhoto(
                    vk_user_id=vk_user_id,
                    vk_photo_id=p.photo_id,
                    likes_count=p.likes_count,
                    file_path=p.local_path,
                    status=p.status,
                )
            )

        await self.session.commit()

    async def get_photos(self, vk_user_id: int) -> list[PhotoDTO]:

        stmt = select(VkPhoto).where(
            VkPhoto.vk_user_id == vk_user_id
        )

        result = await self.session.execute(stmt)
        photos = result.scalars().all()

        return [
            PhotoDTO(
                photo_id=p.vk_photo_id,
                owner_id=p.vk_user_id,
                url="",
                likes_count=p.likes_count,
                local_path=p.file_path,
                status=p.status,
            )
            for p in photos
        ]


