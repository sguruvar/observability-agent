"""
OpenSearch Log Handler
Sends application logs to OpenSearch for centralized logging
"""

import logging
import json
import requests
from datetime import datetime
import traceback

class OpenSearchHandler(logging.Handler):
    """
    Custom logging handler that sends logs to OpenSearch
    """
    
    def __init__(self, opensearch_url='http://localhost:9200', index_name='app-logs'):
        super().__init__()
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.session = requests.Session()
        
        # Create index template if it doesn't exist
        self._create_index_template()
    
    def _create_index_template(self):
        """Create an index template for logs"""
        template = {
            "index_patterns": [f"{self.index_name}-*"],
            "template": {
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "@timestamp": {"type": "date"},
                        "level": {"type": "keyword"},
                        "logger": {"type": "keyword"},
                        "message": {"type": "text"},
                        "module": {"type": "keyword"},
                        "function": {"type": "keyword"},
                        "line": {"type": "integer"},
                        "trace_id": {"type": "keyword"},
                        "span_id": {"type": "keyword"},
                        "claim_id": {"type": "keyword"},
                        "policy_number": {"type": "keyword"},
                        "exception": {"type": "text"}
                    }
                }
            }
        }
        
        try:
            url = f"{self.opensearch_url}/_index_template/app-logs-template"
            self.session.put(url, json=template, timeout=2)
        except:
            pass  # Ignore errors during setup
    
    def emit(self, record):
        """
        Emit a log record to OpenSearch
        """
        try:
            # Get current date for daily indices
            date_str = datetime.utcnow().strftime('%Y.%m.%d')
            index = f"{self.index_name}-{date_str}"
            
            # Build log document
            log_doc = {
                "@timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
                "module": record.module,
                "function": record.funcName,
                "line": record.lineno,
            }
            
            # Add exception info if present
            if record.exc_info:
                log_doc["exception"] = traceback.format_exception(*record.exc_info)
            
            # Add extra fields if present
            if hasattr(record, 'claim_id'):
                log_doc["claim_id"] = record.claim_id
            if hasattr(record, 'policy_number'):
                log_doc["policy_number"] = record.policy_number
            if hasattr(record, 'trace_id'):
                log_doc["trace_id"] = record.trace_id
            if hasattr(record, 'span_id'):
                log_doc["span_id"] = record.span_id
            
            # Send to OpenSearch
            url = f"{self.opensearch_url}/{index}/_doc"
            self.session.post(url, json=log_doc, timeout=1)
            
        except Exception as e:
            # Don't let logging errors crash the app
            self.handleError(record)

def configure_opensearch_logging(app_logger, opensearch_url='http://localhost:9200'):
    """
    Configure OpenSearch logging for the application
    """
    handler = OpenSearchHandler(opensearch_url=opensearch_url)
    handler.setLevel(logging.INFO)
    
    # Format for console output
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    app_logger.addHandler(handler)
    return handler
