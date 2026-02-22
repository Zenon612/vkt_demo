from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import (
    BigInteger,
    String,
    SmallInteger,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
    Index,
    Boolean,
    TIMESTAMP,
)
from sqlalchemy.dialects.postgresql import JSONB
from typing import Optional

class Base(DeclarativeBase):
    pass

class TgUser(Base):
    __tablename__ = "tg_users"


    tg_user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    vk_access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    vk_user_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    filter_city_name: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    filter_gender: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    filter_age_from: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)
    filter_age_to: Mapped[Optional[int]] = mapped_column(SmallInteger, nullable=True)

    history_cursor: Mapped[int] = mapped_column(Integer, default=0)

class VkProfile(Base):
    __tablename__ = "vk_profiles"

    vk_user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(128))
    last_name: Mapped[Optional[str]] = mapped_column(String(128))
    profile_url: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="new")
    found_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)



class SearchQueue(Base):
    __tablename__ = "search_queue"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_users.tg_user_id", ondelete="CASCADE"),
    )

    vk_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("vk_profiles.vk_user_id"),
    )

    __table_args__ = (
        UniqueConstraint("tg_user_id", "vk_profile_id"),
        Index("idx_search_queue_user_position", "tg_user_id", "position"),
    )

class ViewHistory(Base):
    __tablename__ = "view_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_users.tg_user_id", ondelete="CASKADE"),
    )

    vk_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("vk_profiles.vk_user_id"),
    )

    __table_args__ = (
        UniqueConstraint("tg_user_id", "position"),
    )

    photo_attachments: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

class FavoriteProfile(Base):
    __tablename__ = "favorite_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_users.tg_user_id"),
    )

    vk_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("vk_profiles.vk_profile_id"),
    )

    __table_args__ = (
        UniqueConstraint("tg_user_id", "vk_profile_id"),
        Index("idx_favorites_user", "tg_user_id"),
    )


class BlacklistProfile(Base):
    __tablename__ = "blacklist_profiles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    tg_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("tg_users.tg_user_id", ondelete="CASCADE"),
    )

    vk_profile_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("vk_profiles.vk_user_id", ondelete="CASCADE"),
    )

    __table_args__ = (
        UniqueConstraint("tg_user_id", "vk_profile_id"),
        Index("idx_blacklist_user", "tg_user_id"),
    )


class VkPhoto(Base):
    __tablename__ = "vk_photos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    vk_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("vk_profiles.vk_user_id", ondelete="CASCADE"),
    )

    vk_photo_id: Mapped[int] = mapped_column(BigInteger)

    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    file_path: Mapped[Optional[str]] = mapped_column(Text)
    downloaded_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    status: Mapped[str] = mapped_column(String(16), default="raw")
    reject_reason: Mapped[Optional[str]] = mapped_column(String(32))

    faces_count: Mapped[Optional[int]] = mapped_column(SmallInteger)
    det_score: Mapped[Optional[float]] = mapped_column()
    bbox: Mapped[Optional[dict]] = mapped_column(JSONB)
    blur_score: Mapped[Optional[float]] = mapped_column()

    embedding: Mapped[Optional[bytes]] = mapped_column()
    embedding_normed: Mapped[bool] = mapped_column(Boolean, default=False)

    model_name: Mapped[Optional[str]] = mapped_column(String(64))
    model_version: Mapped[Optional[str]] = mapped_column(String(32))

    processed_at: Mapped[Optional[datetime]] = mapped_column(TIMESTAMP)

    __table_args__ = (
        UniqueConstraint("vk_user_id", "vk_photo_id"),
        Index("idx_vk_photos_user", "vk_user_id"),
        Index("idx_vk_photos_status", "status"),
    )