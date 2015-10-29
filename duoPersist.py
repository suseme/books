__author__ = 'vin@misday.com'

from spider import SqliteHelp

class Persist(SqliteHelp):
    DB_NAME = 'data.db'
    DB_VER = 1

    CREATE_BOOK_TBL = '''
    CREATE TABLE IF NOT EXISTS book (
        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
        bid TEXT NOT NULL,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        link TEXT NOT NULL,
        date TEXT NOT NULL,
        download INTEGER NOT NULL DEFAULT 0
    );
    '''

    def __init__(self):
        SqliteHelp.__init__(self, Persist.DB_NAME, Persist.DB_VER)

    # overide
    def onCreate(self):
        self.cursor.execute(Persist.CREATE_BOOK_TBL)
        self.conn.commit()

    # add or not
    def addBook(self, id, title, author, link):
        query = 'SELECT id FROM book WHERE bid = ?'
        self.cursor.execute(query, (id,))
        rows = self.cursor.fetchall()
        if len(rows) < 1:
            query = 'INSERT INTO book (\'bid\', \'title\', \'author\', \'link\', \'date\') VALUES (?, ?, ?, ?, date(\'now\', \'localtime\'))'
            self.cursor.execute(query, (id, title, author, link))
            self.conn.commit()
            return True
        else:
            return False

    def setDownload(self, id):
        query = 'UPDATE book SET download = 1 WHERE bid = ?'
        self.cursor.execute(query, (id,))
        self.conn.commit()

    def isDownload(self, id):
        query = 'SELECT download FROM book WHERE bid = ?'
        self.cursor.execute(query, (id,))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            down = rows[0][0]
            return down == 1
        else:
            return False

    def getTitle(self, id):
        query = 'SELECT title FROM book WHERE bid = ?'
        self.cursor.execute(query, (id,))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            title = rows[0][0]
            return title
        else:
            return None