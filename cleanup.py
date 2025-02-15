import os
import time
import logging
from logging.handlers import RotatingFileHandler

# Configure logging
def setup_logging():
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, 'cleanup.log')
    
    logger = logging.getLogger('CleanupLogger')
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # File handler with rotation (5 files, 1MB each)
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=1024*1024,  # 1MB
        backupCount=5,
        encoding='utf-8'
    )
    
    # Console handler for terminal output
    console_handler = logging.StreamHandler()

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Get the absolute path to uploads folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SCRIPT_DIR, "uploads")

def cleanup_old_files(logger):
    now = time.time()
    max_age = 24 * 3600  # 24 hours
    
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            logger.warning(f"Upload folder not found: {UPLOAD_FOLDER}")
            return

        for user_folder in os.listdir(UPLOAD_FOLDER):
            user_path = os.path.join(UPLOAD_FOLDER, user_folder)
            
            if os.path.isdir(user_path):
                try:
                    folder_age = now - os.path.getmtime(user_path)
                    if folder_age > max_age:
                        # Delete files in the user folder
                        file_count = 0
                        for file in os.listdir(user_path):
                            file_path = os.path.join(user_path, file)
                            try:
                                os.remove(file_path)
                                file_count += 1
                            except Exception as e:
                                logger.error(f"Failed to delete {file_path}: {str(e)}")
                        
                        # Delete the empty folder
                        try:
                            os.rmdir(user_path)
                            logger.info(
                                f"Cleaned {user_folder} - "
                                f"Deleted {file_count} files, "
                                f"Folder age: {folder_age/3600:.1f} hours"
                            )
                        except Exception as e:
                            logger.error(f"Failed to remove directory {user_path}: {str(e)}")
                            
                except Exception as e:
                    logger.error(f"Error processing {user_folder}: {str(e)}")

    except Exception as e:
        logger.critical(f"Fatal error during cleanup: {str(e)}", exc_info=True)

if __name__ == "__main__":
    logger = setup_logging()
    logger.info("=== Starting cleanup process ===")
    cleanup_old_files(logger)
    logger.info("=== Cleanup completed ===")