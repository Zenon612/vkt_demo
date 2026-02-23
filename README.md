# Developer B – Database Layer

## Реализовано:

- Async SQLAlchemy
- Repository pattern
- DTO layer
- Interface layer
- Cursor logic
- Queue logic
- Favorites / Blacklist
- Profile & Photo persistence
- Alembic migrations
- Async tests

## Архитектура

scr/
  /infrastructure/
    db/
    repositories/
    schemas/

## Запуск

1. Создать БД
2. Указать DATABASE_URL
3. alembic upgrade head
4. pytest