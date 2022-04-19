from __init__ import db
from utils.utils import *
import datetime
import time

CURRENT_TIME = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

# 文件夹
class DocFolder(db.Model):
    __tablename__ = "doc_folder"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True,autoincrement=True) 
    folder_id=db.Column(db.Integer, primary_key=True,autoincrement=True)
    ishot=db.Column(db.String(255))
    name=db.Column(db.String(255))
    create_date=db.Column(db.String(255))
    read_num=db.Column(db.Integer)
    store_id=db.Column(db.Integer)
    print_num=db.Column(db.Integer)
    doc_num=db.Column(db.Integer)
    def __init__(self, folder_id,ishot,name,create_date,read_num,print_num,store_id,doc_num):
        self.folder_id=folder_id
        self.ishot=ishot
        self.name=name
        self.create_date=create_date
        self.read_num=read_num
        self.print_num=print_num
        self.store_id=store_id
        self.doc_num=doc_num

# 文件
class Doc(db.Model):
    __tablename__ = "doc"
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True,autoincrement=True) 
    file_id=db.Column(db.String(255))
    file_type=db.Column(db.String(55))
    file_type_id=db.Column(db.Integer)
    folder_id=db.Column(db.Integer)
    ishot=db.Column(db.Integer,default=0)
    file_name=db.Column(db.String(255))
    create_date=db.Column(db.String(255),default=date_now())
    read_num=db.Column(db.Integer,default=0)
    print_num=db.Column(db.Integer,default=0)
    file_page_num=db.Column(db.Integer)
    store_id=db.Column(db.Integer)
    download_url=db.Column(db.String(255))
    def __init__(self, folder_id,store_id,file_id,file_type,file_type_id,file_name,file_page_num,download_url):
        self.folder_id=folder_id
        self.store_id=store_id
        self.file_id=file_id
        self.file_type=file_type
        self.file_type_id=file_type_id
        self.file_name=file_name
        self.file_page_num=file_page_num
        self.download_url=download_url