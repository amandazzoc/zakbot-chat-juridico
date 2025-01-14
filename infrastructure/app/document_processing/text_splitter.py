from langchain.text_splitter import RecursiveCharacterTextSplitter

class DocumentTextSplitter:
    @staticmethod
    def split_documents(documents):
        """Split documents into chunks"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n"]
        )
        return text_splitter.split_text('\n\n, \n'.join(documents))