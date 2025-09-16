from app.db import engine
from app.models import Base


def main() -> None:
    # Create all tables defined in models.Base metadata
    Base.metadata.create_all(bind=engine)
    print("Tables created (if not existing).")


if __name__ == "__main__":
    main()
