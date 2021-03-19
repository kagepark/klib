#Kage Park
from klib.MODULE import *

class SQLITE:
    def __init__(self,filename):
        MODULE().Import('import sqlite3')
        self.filename=filename
        self.conn=None
        self.cur=None
        self.Conn()
        self.Cur()

    def Conn(self):
        if self.conn: return self.conn
        if isinstance(self.filename,str) and os.path.isfile(self.filename):
            try:
                self.conn=sqlite3.connect(self.filename)
                return self.conn
            except sqlite3.Error as error:
                print('Error while connecting to sqlite',error)
                self.conn=None

    def Cur(self):
        if self.cur: return self.cur
        if self.conn:
            self.cur=self.conn.cursor()
            return self.cur

    def Create(self,tablename,*fields):
        fieldstr=','.join(fields)
        query='''CREATE TABLE {} ({});'''.format(tablename,fieldstr)
        cur=self.conn.cursor()
        got=cur.execute(query)
        self.conn.commit()

    def Execute(self,query,mode='put',opt='all'):
        got=self.cur.execute(query)
        if mode != 'put':
            if opt == 'all':
                return got.fetchall()
            else:
                return got.fetchone()

    def Close(self):
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()

class MYSQL:
    def __init__(self):
        MODULE().Import('import mysql')

    def Conn(self):
        pass

class POSTGRESQL:
    def __init__(self):
        MODULE().Import('import postgresql')

    def Conn(self):
        pass

class DB:
    def __init__(self,conn=None,db_type='sqlite', filename=None):
        self.db_type=db_type
        self.MyDB=None
        if self.db_type == 'sqlite':
            if isinstance(filename,str) and os.path.isfile(filename):
                self.MyDB=SQLITE(filename)

    def Fields(self): # Get/check/find field
        pass

    def Put(self): # Put data (If exist then Update, Not then Insert)
        #if data is exist:
        #    Update()
        #else:
        #    Insert()
        pass

    def Del(self): # Delete data
        pass

    def Insert(self): # Insert New data
        pass

    def Update(self): # Update data
        pass

    def Get(self,query): # Get data
        return self.MyDB.Execute(query)

    def Create(self): # Create database
        pass

    def Remove(self): # Remove database
        pass

    def Close(self):
        self.MyDB.Close()
