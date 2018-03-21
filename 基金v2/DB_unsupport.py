import pymysql

class DB_unsupport:
    '''[unsupport]数据库'''
    # Table Name
    table_name = 'unsupport'

    connection = None

    def __init__(self):
        '''Initalize'''
        self.connection = pymysql.connect(host = 'localhost',
                             user = 'root',
                             password = 'root',
                             db = 'fund')

    def select_all(self):
        '''Select All'''
        with self.connection.cursor() as cursor:
            sql = "SELECT * FROM `%s`"%self.table_name

            cursor.execute(sql)
            results = cursor.fetchall()

        results_ = []
        for result in results:
            results_.append(result[1])
        return results_

if __name__ == '__main__':
    db = DB_unsupport()
    print(db.select_all())
