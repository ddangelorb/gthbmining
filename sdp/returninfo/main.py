import sys
import sqlite3
import logging
from sqlite3 import Error
from processor import Processor

DEBUG = True  # Production should be False
logger = logging.getLogger()

db_path = "../db/sdp4ossp.db"
output_path = "../output/results.csv"

def set_logger():
    logging.basicConfig(
        filename="../output/returninfo.log",
        format='%(asctime)s.%(msecs)03d [%(levelname)s] {%(module)s - %(funcName)s}: %(message)s',
        level=logging.INFO
    )
    logger = logging.getLogger()
    if DEBUG:
        logger.addHandler(logging.StreamHandler(sys.stdout))


def process_db():
    try:
        logger.info("sqlite3.version: {}".format(sqlite3.version))

        conn = sqlite3.connect(db_path)
        logger.info("Database ready to operate")

        processor = Processor(logger, conn)
        logger.info(":: Starting Processor.process()...")
        processor.process(output_path)

        logger.info(":: Processor.process() finished...")
    except Error as e:
        logging.exception("Error. process_db")
        conn = None
        raise e
    except Exception as e:
        logging.exception("Exception. process_db")
        conn = None
        raise e
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    try:
        set_logger()
        logger.info("** returninfo/main.py **")
        process_db()
        logger.info(" ** returninfo/main.py finished successfully ** ")
    except Exception as e:
        logger.error("Exception. __main__: '{}'".format(e))
