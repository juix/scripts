import psycopg2
import psycopg2.extras
import psycopg2.extensions

"""
Don't do:

sql = "INSERT INTO TABLE_A (COL_A,COL_B) VALUES (%s, %s)" % (val1, val2)
cursor.execute(sql)

Do:

sql = "INSERT INTO TABLE_A (COL_A,COL_B) VALUES (%s, %s)"
cursor.execute(sql, (val1, val2))
cursor.execute('SELECT * FROM stocks WHERE symbol=?', t)
"""

params = {
 'database': 'motherless',
 'cursor_factory': psycopg2.extras.DictCursor,
}

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

class DB(object):
    def __init__(self, commitOnClose=True, **xargs):
        super(DB, self).__init__()
        self._commitOnClose = commitOnClose
        if len(xargs)==0: xargs=params
        self.dbconnection = psycopg2.connect(**xargs)
        self.cursor = self.dbconnection.cursor()
        #self.execute = self.cursor.execute
        #self.cursor = self.dbconnection.cursor()
        
        
    def __del__(self):
        if self._commitOnClose:
            self.dbconnection.commit()
        self.dbconnection.close()
        
    def commit(self): self.dbconnection.commit()
    
    def rollback(self): self.dbconnection.rollback() 
    
    def execute(self, *args, **kwargs):
        """ 
        this function is being replaced by cursor.execute 
        """
        self.cursor.execute(*args,**kwargs)

    query=execute

class ExtendedDB(DB):
    
    def update(self, table, where, returnkey=None, **x):
        """
        table String
        where Dict
        returnkey String or None
        x args key=val
        """
        keys=[] # keep order of keys and vals
        values=[]
        for k,v in x.items():
            keys.append(k)
            values.append(v)
        
        setq = ",".join(["%s=%s"%(k,"%s") for k in keys])
        wherekeys=[]
        for key, val in where.items():
            wherekeys.append(key)
            values.append(val)
        whereq = ",".join(["%s="%key+"%s" for key in wherekeys])
        q = "UPDATE %s SET %s WHERE %s"%(table,setq,whereq)
        args = tuple(values)
        if returnkey: q = "%s RETURNING %s"%(q, returnkey)
        self.query(q,args)
        if returnkey: 
            r = self.cursor.fetchone()
            return r[0]
        else: return None

    def save(self, table, returnkey=None, **x):
        """ 
        Put data into database according schema of @table 
        @table String table name
        @x key=value, [key2=value2, [...]]
        """
        keys=[] # keep order of keys and vals
        values=[]
        for k,v in x.items():
            keys.append(k)
            values.append(v)
        
        q="INSERT INTO "+table+" ("+",".join(keys)+") VALUES (%s"+\
        ",%s"*(len(x)-1)+")"
        args = tuple(values)
        if returnkey: q = "%s RETURNING %s"%(q, returnkey)
        self.query(q,args)
        if returnkey: 
            r = self.cursor.fetchone()
            return r[0]
        else: return None
        
