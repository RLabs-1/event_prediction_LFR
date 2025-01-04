import logging
from log_processor.config_loader import ConfigLoader
from log_processor.log_parser import LogParser
from log_processor.filters import LogFilter
from log_processor.batch_processor import BatchProcessor


def setup_logging():
    """
    Configures logging for the application.
    Logs are displayed on the console and saved to a file.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),  # Log to console
            logging.FileHandler("log_processing.log", mode='a')  # Append logs to a file
        ]
    )


if __name__ == "__main__":
    # Step 1: Set up logging
    setup_logging()
    logging.info("Starting log processing application...")

    try:
        # Step 2: Load configuration
        config_file = "config/.yaml"
        config_loader = ConfigLoader(config_file)
        try:
            config = config_loader.load()
        except FileNotFoundError:
            logging.error(f"Configuration file not found: {config_file}")
            raise SystemExit("Unable to proceed without configuration.")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            raise SystemExit("Configuration loading error.")

        # Extract parameters from configuration
        try:
            source_dir = config['log_processing']['source']['location']
            supported_formats = config['log_processing']['format']['supported_formats']
            include_keywords = config['log_processing']['filters']['include_keywords']
            exclude_keywords = config['log_processing']['filters']['exclude_keywords']
            date_range = config['log_processing']['filters']['date_range']
            batch_size = config['log_processing']['batch']['size']
            encoding = config.get('log_processing', {}).get('encoding', 'utf-8')
        except KeyError as ke:
            logging.error(f"Missing configuration key: {ke}")
            raise SystemExit("Invalid or incomplete configuration file.")

        # Step 3: Initialize components
        log_filter = LogFilter(include_keywords, exclude_keywords, date_range)
        batch_processor = BatchProcessor(batch_size)
        log_parser = LogParser(source_dir, supported_formats, log_filter, batch_processor, encoding=encoding)

        # Step 4: Start processing logs
        logging.info(f"Processing logs from directory: {source_dir}")
        try:
            log_parser.parse_all_logs()
        except Exception as e:
            logging.error(f"Error during log parsing: {e}")
            raise

        # Step 5: Finalize processing
        try:
            batch_processor.flush()  # Ensure remaining logs are processed
            logging.info("Log processing completed successfully.")
        except Exception as e:
            logging.error(f"Error during batch finalization: {e}")
            raise

    except Exception as e:
        logging.critical(f"An unrecoverable error occurred: {e}")
