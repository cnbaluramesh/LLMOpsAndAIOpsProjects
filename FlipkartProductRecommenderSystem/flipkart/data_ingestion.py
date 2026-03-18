from langchain_astradb import AstraDBVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from flipkart.data_converter import DataConverter
from flipkart.config import Config


class DataIngestor:
    def __init__(self):
        print("Initializing embeddings...")

        # ✅ Use local embeddings (NO API issues)
        self.embedding = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Connecting to AstraDB...")

        self.vstore = AstraDBVectorStore(
            embedding=self.embedding,
            collection_name="flipkart_database",
            api_endpoint=Config.ASTRA_DB_API_ENDPOINT,
            token=Config.ASTRA_DB_APPLICATION_TOKEN,
            namespace=Config.ASTRA_DB_KEYSPACE
        )

    def ingest(self, load_existing=False):
        print("Ingest function called")

        if load_existing:
            print("Skipping ingestion, loading existing vector store...")
            return self.vstore

        try:
            print("Loading documents...")
            docs = DataConverter("data/flipkart_product_review.csv").convert()
            print(f"Loaded {len(docs)} documents")

            if not docs:
                print("No documents found. Check your CSV or DataConverter.")
                return self.vstore

            print("Starting ingestion...")

            # ✅ Batch insertion (prevents failures for large data)
            batch_size = 50
            for i in range(0, len(docs), batch_size):
                batch = docs[i:i + batch_size]
                self.vstore.add_documents(batch)
                print(f"Inserted batch {i // batch_size + 1}")

            print("Ingestion completed successfully!")

        except Exception as e:
            print("ERROR during ingestion:", str(e))

        return self.vstore


# # ✅ Entry point (VERY IMPORTANT)
# if __name__ == "__main__":
#     print("Main started")

#     ingestor = DataIngestor()
#     ingestor.ingest(load_existing=False)