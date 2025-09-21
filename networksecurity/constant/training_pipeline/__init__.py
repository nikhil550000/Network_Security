import os,sys
import numpy as np
import pandas as pd

"""
defining constant variable for training pipeline
"""

TARGET_COLUMN = 'Result'
PIPELINE_NAME:str = 'NetworkSecurityPipeline'
ARTIFACT_DIR:str = 'artifact'
FILE_NAME:str = 'NetworkData.csv'

TRAIN_FILE_NAME = 'train.csv'
TEST_FILE_NAME = 'test.csv'
PREPROCESSING_OBJECT_FILE_NAME = 'preprocessing.pkl'
MODEL_FILE_NAME = 'model.pkl'
SCHEMA_FILE_PATH = os.path.join('data_schema','schema.yaml')
SCHEMA_DROP_COLS = 'drop_columns'

SAVE_MODEL_DIR = os.path.join('saved_models')

"""
Data Ingestion related constant start with DATA_INGESTION VAR NAME
"""
DATA_INGESTION_COLLECTION_NAME:str = 'phishing_data'
DATA_INGESTION_DATABASE_NAME:str = 'network_security_db'
DATA_INGESTION_DIR_NAME:str = 'data_ingestion'
DATA_INGESTION_FEATURE_STORE_DIR:str = 'feature_store'
DATA_INGESTION_INGESTED_DIR:str = 'ingested'
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION:float = 0.2

"""
DATA Validataion related constant start with DATA_VALIDATION VAR NAME
"""


"""
DATA Transformation relate constant start with DATA_TRANSFORMATION VAR NAME
"""


"""
Model Trainer related constant start with MODE TRAINER VAR NAME
"""

