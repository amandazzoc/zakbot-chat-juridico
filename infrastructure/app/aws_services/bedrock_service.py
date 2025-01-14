import json
import boto3
from langchain_aws import BedrockEmbeddings

class BedrockService:
    def __init__(self, logger, documents):
        self.bedrock = boto3.client('bedrock-runtime')
        self.logger = logger
        self.documents = documents

    def setup_embeddings(self):
        """Configure Titan embeddings"""
        return BedrockEmbeddings(
            client=self.bedrock,
            model_id="amazon.titan-embed-text-v2:0"
        )

    def invoke_model(self, input_text, context):
        """Invoke Bedrock model with context"""
        try:
            response = self.bedrock.invoke_model(
                modelId="amazon.titan-text-express-v1",
                contentType="application/json",
                body=json.dumps({
                    "inputText": (
                        "Você é um assistente jurídico especializado. "
                        "Responda APENAS com base nos seguintes documentos: "
                        f"\n\nDOCUMENTOS: {context}\n\n"
                        "A resposta deve ser em português, concisa e direta. "
                        "Se não souber a resposta, diga 'Não encontrei informações suficientes nos documentos.'. "
                        f"Pergunta: {input_text}"
                    ),
                    "textGenerationConfig": {
                        "maxTokenCount": 1024,
                        "stopSequences": ["User:"],
                        "temperature": 0.7,
                        "topP": 0.4
                    }
                })
            )
            
            response_body = json.loads(response['body'].read().decode('utf-8'))
            return response_body['results'][0]['outputText']
        
        except Exception as e:
            self.logger.log(f"Detailed error invoking model: {str(e)}", severity='ERROR')
            return "Desculpe, ocorreu um erro ao processar sua pergunta."