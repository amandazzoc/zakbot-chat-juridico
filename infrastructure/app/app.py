from config import Config
from aws_services.cloudwatch_logger import CloudWatchLogger
from aws_services.s3_document_loader import S3DocumentLoader
from aws_services.bedrock_service import BedrockService
from document_processing.text_splitter import DocumentTextSplitter
from document_processing.vectorstore import VectorstoreManager
from telegram_bot.bot_handler import TelegramBotHandler

def main():
    # Validate configuration
    Config.validate_config()

    # Initialize logger
    logger = CloudWatchLogger()

    try:
        # Load documents from S3
        document_loader = S3DocumentLoader(Config.BUCKET_NAME, logger)
        documents = document_loader.load_pdfs()

        # Setup Bedrock service
        bedrock_service = BedrockService(logger, documents)
        embeddings = bedrock_service.setup_embeddings()

        # Prepare documents for vectorstore
        texts = DocumentTextSplitter.split_documents(documents)

        # Create vectorstore
        vectorstore_manager = VectorstoreManager(embeddings, logger)
        vectorstore = vectorstore_manager.create_vectorstore(texts)
        vectorstore_manager.vectorstore = vectorstore

        # Initialize Telegram bot
        bot_handler = TelegramBotHandler(
            Config.TELEGRAM_TOKEN, 
            bedrock_service, 
            vectorstore_manager, 
            logger,
            document_loader
        )

        # Start the bot
        bot_handler.start_bot()

    except Exception as e:
        logger.log(f"Erro fatal ao iniciar o bot: {str(e)}", severity='ERROR')
        print(f"Erro detalhado: {str(e)}")

    Config.validate_config()
if __name__ == "__main__":
    main()