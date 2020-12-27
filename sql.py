import sqlite3

class SQL:
    def __init__(self, database_file):
        self.connection = sqlite3.connect(database_file, check_same_thread = False)
        self.cursor = self.connection.cursor()
    
    def add(self, streamer, date, begin, end):
        with self.connection:
            return self.cursor.execute("INSERT INTO `streamers` (`streamer`, `date`, `begin`, `end`) VALUES (?,?,?,?)", (streamer, date, begin, end))
    
    def delete(self, streamer, date, begin):
        with self.connection:
            return self.cursor.execute("DELETE FROM 'streamers' WHERE 'streamer'=?  AND 'date'=? AND 'begin'=?", (streamer, date, begin,))

    def close(self):
        self.connection.close()