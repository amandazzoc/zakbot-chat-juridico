from langchain_community.vectorstores import Chroma

class VectorstoreManager:
    def __init__(self, embeddings, logger):
        self.embeddings = embeddings
        self.logger = logger

    def create_vectorstore(self, texts):
        """Create vectorstore with loaded documents"""
        if not texts:
            self.logger.log("Nenhum documento para criar vetorstore!", severity='ERROR')
            return None

        return Chroma.from_texts(
            texts, 
            embedding=self.embeddings,
            persist_directory="./chroma_db"
        )

    def retrieve_relevant_documents(self, vectorstore, query, k=3):
        """Retrieve relevant documents for a query"""
        if not vectorstore:
            return "Nenhum documento disponível para busca."
        
        # Buscar documentos mais relevantes
        results = vectorstore.similarity_search(query, k=k)
        
        # Formatar resultados para contexto
        return "\n\n".join([doc.page_content for doc in results])