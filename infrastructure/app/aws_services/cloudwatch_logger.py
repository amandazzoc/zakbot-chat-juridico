import time
import boto3

class CloudWatchLogger:
    def __init__(self, log_group='/zakbot/logs', log_stream='application'):
        self.client = boto3.client('logs', region_name='us-east-1')
        self.log_group = log_group
        self.log_stream = log_stream
        
        self._create_log_group_and_stream()

    def _create_log_group_and_stream(self):
        """Create log group and stream if they don't exist"""
        for create_method, name in [
            (self.client.create_log_group, self.log_group),
            (self.client.create_log_stream, (self.log_group, self.log_stream))
        ]:
            try:
                # Handle different method signatures
                if isinstance(name, tuple):
                    create_method(logGroupName=name[0], logStreamName=name[1])
                else:
                    create_method(logGroupName=name)
            except self.client.exceptions.ResourceAlreadyExistsException:
                pass

    def log(self, message, severity='INFO'):
        """Log a message to CloudWatch"""
        log_event = {
            'timestamp': int(round(time.time() * 1000)),
            'message': f"[{severity}] {message}"
        }
        
        try:
            self.client.put_log_events(
                logGroupName=self.log_group,
                logStreamName=self.log_stream,
                logEvents=[{
                    'timestamp': log_event['timestamp'],
                    'message': log_event['message']
                }]
            )
        except Exception as e:
            print(f"Erro ao logar no CloudWatch: {e}")