from logger import logger
import traceback

def safe_execute(func, *args, **kwargs):
    try:
        result = func(*args, **kwargs)
        logger.info(f"Executed {func.__name__} successfully with args={args}, kwargs={kwargs}")
        return result
    except Exception as e:
        logger.error(f"Error in {func.__name__}: {e}")
        logger.error(traceback.format_exc())
        return {"error": str(e)}
