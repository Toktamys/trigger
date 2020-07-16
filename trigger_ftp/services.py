import os
import re
import shutil
from _md5 import md5
from ftplib import FTP
from uuid import uuid4

import pandas as pd
from django.conf import settings

from trigger_ftp.models import Customer


class FTPHandler:
    __CSV = '.csv'
    __XLS = '.xls'
    __XLSX = '.xlsx'

    extensions = (
        __CSV,
        __XLS,
        __XLSX
    )
    files = []

    def __init__(self):
        self.folder_name = uuid4().hex[:20]
        self.full_path = f'./temp_files/{self.folder_name}/'
        self.connect_to_ftp()
        self.search_files()

    def connect_to_ftp(self):
        ftp_connection = FTP()
        try:
            ftp_connection.connect(host=settings.FTP_HOST, timeout=15)
            ftp_connection.login(settings.FTP_LOGIN, settings.FTP_PASSWORD)
            os.mkdir(self.full_path)
            for idx, f in enumerate(ftp_connection.nlst()):
                if f.endswith(self.extensions):
                    file_extension = os.path.splitext(f)[1]
                    file_name = f'crm_{idx}{file_extension}'
                    ftp_connection.retrbinary(f'RETR {f}', open(self.full_path + file_name, 'wb').write)
        except Exception as error:
            print(str(error))
            raise error
        finally:
            ftp_connection.quit()
            ftp_connection.close()

    def search_files(self):
        self.files = []
        for f in os.listdir(self.full_path):
            if f.endswith(self.extensions):
                self.files.append(os.path.join(self.full_path, f))

    def normalize_phone(self, phone):
        result = phone.replace(' ', '').replace('(', '').replace(')', '').replace('+', '').replace('-', '')
        result = '7{}'.format(result[1:])
        return result

    def check_email(self, email):
        if email:
            regex = r"[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}"
            if re.search(regex, email):
                return email
        return None

    def read_file(self):
        data_list = []
        for idx, f in enumerate(self.files):
            data = None

            if f.endswith(self.__CSV):
                data = pd.read_csv(f)
            elif f.endswith((self.__XLS, self.__XLSX)):
                data = pd.read_excel(f)

            if not data.empty:
                df = pd.DataFrame(data, columns=['phone', 'email'])
                df = df.where(df.notnull(), None)
                values = df.values[:]
                values = list(
                    map(lambda x: {'phone': self.normalize_phone(x[0]), 'email': self.check_email(x[1])}, values)
                )
                data_list.extend(values)

        return data_list

    def get_hashed_data(self):
        data = self.read_file()
        hashed_list = []
        if data:
            for datum in data:
                hashed_item = {}
                if datum:
                    for key, value in datum.items():
                        if value:
                            hashed_item[key] = md5(value.encode()).hexdigest()
                        else:
                            hashed_item[key] = value
                    if hashed_item:
                        hashed_list.append(hashed_item)
        return hashed_list

    def save(self):
        data = self.get_hashed_data()
        bulk_list = []
        if data:
            for datum in data:
                bulk_list.append(
                    Customer(**datum)
                )
            if bulk_list:
                Customer.objects.bulk_create(bulk_list)

    def __del__(self):
        for f in self.files:
            if os.path.exists(f):
                os.remove(f)
        if os.path.exists(self.full_path):
            os.rmdir(self.full_path)
