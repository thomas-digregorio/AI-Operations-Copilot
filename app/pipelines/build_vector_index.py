from app.services.rag_service import RAGService


def main() -> None:
    service = RAGService()
    result = service.build_index()
    print(result)


if __name__ == "__main__":
    main()
