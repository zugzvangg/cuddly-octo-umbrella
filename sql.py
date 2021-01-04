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
            return self.cursor.execute("DELETE FROM `streamers` WHERE `streamer`=?  AND `date`=? AND `begin`=?", (streamer, date, begin,))

    def get_users_streams(self, streamer):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `streamers` WHERE `streamer` = ?', (streamer,)).fetchall()

    def close(self):
        self.connection.close()

    def get_today_streams(self, today, streamer):
        with self.connection:
            return self.cursor.execute('SELECT * FROM `streamers` WHERE `date` = ? AND `streamer`=?', (today, streamer)).fetchall()
    
    def get_statistics(self, streamer):
        with self.connection:
            return self.cursor.execute('SELECT date, begin, end FROM `streamers` WHERE `streamer` = ?', (streamer,)).fetchall()