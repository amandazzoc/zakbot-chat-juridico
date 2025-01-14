from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler

class TelegramBotHandler:
    def __init__(self, telegram_token, bedrock_service, vectorstore, logger, s3_document_loader):
        self.telegram_token = telegram_token
        self.bedrock_service = bedrock_service
        self.vectorstore = vectorstore
        self.logger = logger
        self.s3_document_loader = s3_document_loader
        self.selected_document = {}

    async def handle_message(self, update: Update, context):
        """Handle incoming Telegram messages"""
        query = update.message.text
        user_id = update.effective_user.id
        
        # Check if the user has selected a document
        if user_id not in self.selected_document:
            await update.message.reply_text(
                "Por favor, primeiro use /listar para selecionar um documento."
            )
            return

        try:
            # Load the selected document
            document_content = self.s3_document_loader.load_specific_pdf(
                self.selected_document[user_id]
            )
            
            # Retrieve context and generate response
            context = self.vectorstore.retrieve_relevant_documents(
                self.vectorstore.vectorstore, 
                query
            )
            response = self.bedrock_service.invoke_model(query, context)
            
            await update.message.reply_text(response)
            
            # Log interaction
            self.logger.log(f"Query: {query}\nResposta: {response}")
        
        except Exception as e:
            error_message = f"Erro ao processar mensagem: {str(e)}"
            await update.message.reply_text("Eu não consegui entender ☹️. Reformule sua pergunta.")
            self.logger.log(error_message, severity='ERROR')
            print(f"Erro detalhado: {str(e)}")

    async def start_command(self, update: Update, context):
        """Initial bot command"""
        await update.message.reply_text(
            "Oi, eu sou o Zak! 🤖 "
            "Use /listar para começar."
        )

    async def listar_command(self, update: Update, context):
        """Listar documentos disponíveis no bucket S3"""
        try:
            pdfs = self.s3_document_loader.list_pdfs()
            
            if not pdfs:
                await update.message.reply_text("Nenhum documento PDF encontrado no bucket.")
                return

            # Creates inline for each PDF file
            keyboard = []
            for pdf in pdfs:
                keyboard.append([InlineKeyboardButton(pdf, callback_data=pdf)])

            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                "Selecione um documento para consultar:", 
                reply_markup=reply_markup
            )

        except Exception as e:
            self.logger.log(f"Erro ao listar documentos: {str(e)}", severity='ERROR')
            await update.message.reply_text("Desculpe, não foi possível listar os documentos.")

    async def documento_selecionado(self, update: Update, context):
        """Callback quando um documento é selecionado"""
        query = update.callback_query
        await query.answer()
        
        documento = query.data
        user_id = query.from_user.id
        
        self.selected_document[user_id] = documento
        
        # Update message with selected document
        await query.edit_message_text(
            f"📄 Documento selecionado: *{documento}*\n\n"
            "✅ Estou pronto para responder suas dúvidas. ",
            parse_mode='Markdown'
        )

    def start_bot(self):
        """Start Telegram bot"""
        app = Application.builder().token(self.telegram_token).build()
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("listar", self.listar_command))
        app.add_handler(CallbackQueryHandler(self.documento_selecionado))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        app.run_polling(drop_pending_updates=True)