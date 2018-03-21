import pymysql

class FundDB:
    '''基金赎回信息类'''
##    table_name = 'test'
    table_name = 'redeem'
    
    connection = None
    
    def __init__(self):
        self.connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'root',
                             db = 'fund')
        print('数据库连接已开启 ...')

    def insert_redeem(self, code, redeem):
        with self.connection.cursor() as cursor:
            sql = """ INSERT INTO `"""+self.table_name+"""` (`code`, `fee`) VALUES ('"""+code+"""', """+str(redeem)+""")"""

            cursor.execute(sql)
            self.connection.commit()

    def get_redeem_by_code(self, code = 0):
        with self.connection.cursor() as cursor:
            sql = """SELECT fee FROM """+self.table_name+""" WHERE `code` = '"""+code+"""'"""

            cursor.execute(sql)
            result = cursor.fetchone()
            if result != None:
                try:
                    result = float(result[0])
                except ValueError:
                    result = None
        return result

    def close(self):
        self.connection.close()
        print('数据库连接已关闭 ...')

###===============================================
##redeem = Redeem()
##print(redeem.get_redeem_by_code(str('004643')))
