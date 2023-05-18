import sqlite3
from typing import List

class DatabaseManager:
    """
    Class to manage inserting/updating databases based on excavated data

    Attributes:
        conn (Connection): Connection to database
        c (Cursor): Database cursor for the connection above
        commit_everything (bool): Determines whether or not to commit after every execute.
    """


    def __init__(self, db: str, commit: bool):
        """
        Initializes the instance by connecting the manager with database of choice.

        Args:
            db: Name or path to database to connect to. Make sure to end with '.db'.
            commit: see 'commit_everything' description.
        """
        self.conn = sqlite3.connect(db)
        self.c = self.conn.cursor()
        self.commit_everything = commit
    

    def create_table(self):
        """
        Creates a table to contain odds in database if it doesn't already exist

        The table created should look like: linkbook | link | date | market | bookmaker | odds_1 | odds_2 | odds_3
        """
        query = '''
                CREATE TABLE IF NOT EXISTS odds
                (
                    linkbook TEXT NOT NULL PRIMARY KEY,
                    link TEXT NOT NULL,
                    date TEXT NOT NULL,
                    market TEXT,
                    bookmaker TEXT,
                    odds_1 NUMERIC,
                    odds_2 NUMERIC,
                    odds_3 NUMERIC
                )
                '''

        self.c.execute(query)
        
        if (self.commit_everything):
            self.conn.commit()
    

    def add_to_table(self, link: str, date: str, market: str, bookmaker: str, odds: List[float]):
        """
        Adds row to odds table

        Args:
            link: Link to the page of the game where odds were found
            date: Date the game occured. YYYYMMDD format.
            bookmaker: The bookmaker who set these odds.
            market: The market the odds were in. For example 1X2, Double Chance, etc.
            odds: List of up to 3 odds.
        """
        query = '''
                INSERT INTO odds (linkbook, link, date, market, bookmaker, odds_1, odds_2, odds_3)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(linkbook) DO UPDATE SET
                    link = excluded.link,
                    date = excluded.date,
                    market = excluded.market,
                    bookmaker = excluded.bookmaker,
                    odds_1 = excluded.odds_1,
                    odds_2 = excluded.odds_2,
                    odds_3 = excluded.odds_3;
                '''
        
        temp_odds = [None, None, None]
        for i in range(len(odds)):
            temp_odds[i] = odds[i]

        vals = (link + bookmaker, link, date, market, bookmaker, temp_odds[0], temp_odds[1], temp_odds[2])

        self.c.execute(query, vals)
        
        if (self.commit_everything):
            self.conn.commit()
    

    def commit(self):
        """
        Commits changes to database.

        Use this to commit if commit_everything is false, and you want to decide when
        to commit changes to database yourself.
        """
        self.conn.commit()
    
    def __del__(self):
        """Closes all connection when object is destroyed"""
        self.c.close()
        self.conn.close()

"""        
There are 3 values to contain odds in the table--odds_1 odds_2 and odds_3--and they correspond
to different things depending on the 'market' value. For instance, in a '1X2' market, odds_1 corresponds
to 1, odds_2 corresponds to X, and odds_3 corresponds to 2. 

The order that you see the odds in is how they will appear here. If on the website 
the market is displayed by showing the 1 odds first, the X odds second, and 2 odds 
third, then odds_1 will hold the 1 odds, odds_2 the X odds, and odds_3 the 2 odds.
"""