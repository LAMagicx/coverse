from loguru import logger
import sys
import os

# Adopted from https://stackoverflow.com/a/35804945/1691778
# Adds a new logging method to the logging module
def addLoggingLevel(levelName, levelNum, methodName=None):
    if not methodName:
        methodName = levelName.lower()

    if hasattr(logger, levelName):
        raise AttributeError("{} already defined in logging module".format(levelName))
    if hasattr(logger, methodName):
        raise AttributeError("{} already defined in logging module".format(methodName))

    def logForLevel(message: str, levelName: str = levelName, *args, **kwargs):
        logger.log(levelName, message, args, **kwargs)

    def logToRoot(message, *args, **kwargs):
        logging.log(levelNum, message, *args, **kwargs)

    logger.level(levelName, no=levelNum)
    setattr(logger, methodName, logForLevel)


def create_logger(name: str):
    log_format = (
        "<level>{level}</level>:\t"
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green>\t"
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>\t"
        "<level>{message}</level>"
    )

    # Remove default logger
    logger.remove()

    # Adding a console handler with color formatting
    logger.add(sys.stdout, format=log_format, level="DEBUG", colorize=True)

    # Adding a file handler with JSON formatting
    logger.add("logs/api_logs.txt", rotation="7 days", retention="1 month", serialize=True, backtrace=False)

    # Set log level to EVENT (which is slightly lower than INFO)
    logger.level("EVENT", no=logger.level("INFO").no - 5)
    # addLoggingLevel("EVENT", logger.level("INFO").no - 5)

    # Adding an auto exception handler
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        # Log the exception using logger.exception, which automatically logs the traceback
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

    # sys.excepthook = handle_exception

    return logger

"""
if __name__ == "__main__":
    # Example usage
    logger = create_logger(__name__)

    try:
        # Example logging
        raise ValueError("This is a test exception")
    except Exception as e:
        # Use logger.exception() to automatically log the exception with traceback
        logger.exception("An error occurred")

    logger.debug("This is a debug message")
    logger.log("EVENT", "This is an event message")
"""
