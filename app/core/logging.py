import logging
import sys

import structlog

from app.core.config import settings

def setup_logging() -> None:

    #create the handlers (console and file)
    console_handler = logging.StreamHandler(sys.stdout)
    
    
    #Configure the minimum level and base logger
    level = logging.DEBUG if settings.debug else logging.INFO
    logging.basicConfig(
        level=level,
        format=f"%(message)s",
        handlers=[
            console_handler
        ]
    )
    
    #Configure the processors and format
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.stdlib.LoggerFactory()  
    )

#Function created to delete dependencies with Logging
def get_logger(name: str):
    return structlog.get_logger(name)
