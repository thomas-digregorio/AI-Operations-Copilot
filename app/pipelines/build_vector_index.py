from app.db.session import Base, SessionLocal, engine
from app.services.rag_service import RAGService


def main() -> None:
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    service = RAGService()
    try:
        result = service.build_index(db=session)
    finally:
        session.close()
    print(result)


if __name__ == "__main__":
    main()
