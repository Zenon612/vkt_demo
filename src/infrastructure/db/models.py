from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


# ================= USERS =================

class User(Base):
    __tablename__ = "users"

    tg_user_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    vk_access_token: Mapped[str | None]
    vk_user_id: Mapped[int | None]

    filter_city_name: Mapped[str | None]
    filter_city_id: Mapped[int | None]
    filter_gender: Mapped[int | None]
    filter_age_from: Mapped[int | None]
    filter_age_to: Mapped[int | None]

    history_cursor: Mapped[int] = mapped_column(default=0)


# ================= QUEUE =================

class QueueItem(Base):
    __tablename__ = "queue"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_user_id"))
    vk_profile_id: Mapped[int]
    position: Mapped[int]


# ================= FAVORITES =================

class FavoriteProfile(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int]
    vk_profile_id: Mapped[int]

    __table_args__ = (
        UniqueConstraint("tg_user_id", "vk_profile_id"),
    )


# ================= BLACKLIST =================

class Blacklist(Base):
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_user_id: Mapped[int]
    vk_profile_id: Mapped[int]


# ================= PROFILES =================

class Profile(Base):
    __tablename__ = "profiles"

    vk_user_id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str]
    last_name: Mapped[str]
    domain: Mapped[str]


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(primary_key=True)
    vk_user_id: Mapped[int] = mapped_column(ForeignKey("profiles.vk_user_id"))

    photo_id: Mapped[int]
    owner_id: Mapped[int]
    url: Mapped[str]
    likes_count: Mapped[int]

    local_path: Mapped[str | None]
    status: Mapped[str | None]