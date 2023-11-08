import os

import yaml
from sqlalchemy import create_engine


base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
secrets_path = os.path.join(base_dir, 'secret', 'secrets.yaml')

# secrets.yaml 파일을 읽어옵니다.
with open(secrets_path, 'r') as stream:
    secrets = yaml.safe_load(stream)

# DB 접속 정보를 변수에 저장합니다.
USER = secrets['database_credentials']['USER']
PASSWORD = secrets['database_credentials']['PASSWORD']
HOST = secrets['database_credentials']['HOST']
PORT = secrets['database_credentials']['PORT']
DATABASE = secrets['database_credentials']['DATABASE']

engine = create_engine(
    f'mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}'
    )

# chrome driver 경로
driver_path = "/usr/local/bin/chromedriver"
