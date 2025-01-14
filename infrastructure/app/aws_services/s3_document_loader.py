import io
import boto3
import PyPDF2

class S3DocumentLoader:
    def __init__(self, bucket_name, logger):
        self.s3 = boto3.client('s3')
        self.bucket_name = bucket_name
        self.logger = logger

    def load_pdfs(self):
        """Load PDFs from S3 bucket with detailed error handling"""
        pdf_texts = []
        
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                self.logger.log("Nenhum documento encontrado no bucket!", severity='WARNING')
                return pdf_texts
            
            for obj in response.get('Contents', []):
                if obj['Key'].endswith('.pdf'):
                    pdf_text = self._process_pdf(obj['Key'])
                    if pdf_text:
                        pdf_texts.append(pdf_text)
        
        except Exception as e:
            self.logger.log(f"Erro ao listar objetos no bucket: {str(e)}", severity='ERROR')
        
        # Log total documents and preview
        self.logger.log(f"Número de documentos carregados: {len(pdf_texts)}")
        for i, doc in enumerate(pdf_texts):
            self.logger.log(f"Prévia do documento {i+1}: {doc[:200]}...")
        
        return pdf_texts

    def _process_pdf(self, key):
        """Process a single PDF from S3"""
        try:
            self.logger.log(f"Processando PDF: {key}")
            
            pdf_obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            pdf_content = pdf_obj['Body'].read()
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text = ''.join(page.extract_text() for page in pdf_reader.pages)
            
            if text.strip():
                self.logger.log(f"Carregado PDF: {key}, Tamanho: {len(text)} caracteres")
                return text
            else:
                self.logger.log(f"PDF vazio: {key}", severity='WARNING')
                return None
        
        except Exception as e:
            self.logger.log(f"Erro ao processar PDF {key}: {str(e)}", severity='ERROR')
            return None

    def list_pdfs(self):
        """Listar apenas os nomes dos PDFs no bucket"""
        try:
            response = self.s3.list_objects_v2(Bucket=self.bucket_name)
            
            if 'Contents' not in response:
                self.logger.log("Nenhum documento encontrado no bucket!", severity='WARNING')
                return []
            
            pdfs = [obj['Key'] for obj in response.get('Contents', []) if obj['Key'].endswith('.pdf')]
            
            return pdfs
        
        except Exception as e:
            self.logger.log(f"Erro ao listar objetos no bucket: {str(e)}", severity='ERROR')
            return []

    def load_specific_pdf(self, key):
        """Carregar conteúdo de um PDF específico"""
        try:
            self.logger.log(f"Processando PDF específico: {key}")
            
            pdf_obj = self.s3.get_object(Bucket=self.bucket_name, Key=key)
            pdf_content = pdf_obj['Body'].read()
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            text = ''.join(page.extract_text() for page in pdf_reader.pages)
            
            if text.strip():
                self.logger.log(f"Carregado PDF: {key}, Tamanho: {len(text)} caracteres")
                return text
            else:
                self.logger.log(f"PDF vazio: {key}", severity='WARNING')
                return None
        
        except Exception as e:
            self.logger.log(f"Erro ao processar PDF {key}: {str(e)}", severity='ERROR')
            return None