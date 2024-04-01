from datetime import timedelta


class Config:
    SECRET_KEY = 'super_secretoso'
    SESSION_TYPE = 'filesystem'
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:atx11525@192.168.1.103:5432/box_manager'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
