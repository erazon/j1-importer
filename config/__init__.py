import os
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = ".aws.env"
env_path = Path('.').absolute() / ENV_FILE
print("ENV PATH: {}".format(env_path))
load_dotenv(dotenv_path=env_path, verbose=False)


class Config(object):
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "mongorun")
    MONGODB_HOST = os.getenv("MONGODB_HOST", "localhost")
    MONGODB_PORT = int(os.getenv("MONGODB_PORT", "27017"))
    MONGODB_USERNAME = os.getenv("MONGODB_USERNAME", "user")
    MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD", "password123")
    MONGODB_AUTH_DATABASE = os.getenv("MONGODB_AUTH_DATABASE", "mongorun")

    KOMBU_HOST = os.getenv("KOMBU_HOST")
    KOMBU_EXCHANGE = os.getenv("KOMBU_EXCHANGE")
    KOMBU_QUEUE = os.getenv("KOMBU_QUEUE")

    ENV = os.getenv("ENV", "development")
    APPLICATION_ROOT = os.getenv("APPLICATION_ROOT", "")
    TESTING = (os.getenv("TESTING", "False") == "True")
    DEBUG = (os.getenv("DEBUG", "False") == "True")

    SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
    S3_BUCKET = os.getenv("S3_BUCKET", "cc.devstage.marketplace.raw-import-data")
    S3_FOLDER = os.getenv("S3_FOLDER", "higher_reach_importer")
    AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

    # print("<----- MongoConfig(Config) ----->\n"
    #       "database: {}\n"
    #       "host: {}\n"
    #       "port: {}\n"
    #       "user: {}\n"
    #       "password: {}\n"
    #       "MONGODB_AUTH_DATABASE: {}\n"
    #       "SECRET_KEY: {}\n"
    #       "ACCESS_KEY: {}\n"
    #       "S3_BUCKET: {}\n"
    #       "S3_FOLDER: {}\n".format(
    #     MONGODB_DATABASE, MONGODB_HOST, MONGODB_PORT,
    #     MONGODB_USERNAME, MONGODB_PASSWORD,
    #     MONGODB_AUTH_DATABASE, SECRET_KEY, ACCESS_KEY, S3_BUCKET, S3_FOLDER
    # ))
    # print("-" * 40)
