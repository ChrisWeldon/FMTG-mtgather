import mysql.connector
from mysql.connector.errors import *
import os, csv, json, sys, math
import pandas as pd
import numpy as np
from datetime import timedelta, date, datetime

"""A module containing the datatype definitions.

"""

def daterange(first, last):
    dates = []
    for n in range(int ((last - first).days)+1):
        dates.append(first + timedelta(n))
    return dates

class Card:
    """Card Datatype

    The Card Class is used to represent one card in MTG. The class is also used as a Database model for one card.
    This card does not represent any particular moment in time. A card class, should represent the full extend of the card's life
    in the MTG Game given.

    This Card Class is chock full of deprecated methods and attributes. Documentation is on hold for this class
    because it needs to be completely overhauled.

    Deprecated Attributes are not incuded in Documentation.

    TODO:
        Strip of non usefull attribute

    Attributes:
        title: A string of title of the card.
        price: A Pandas Dataframe of the paper pricing history.
        tix: A Pandas Dataframe of the MTGO pricing history
        set: A string of the URL of the set.
        echo_id: An int of the echomtg unique identifier.
        rarity: A string of the rarity of the card "rare", "mythic", "uncommon", ...
        release_date: A datetime object of the release date of the card. *Note:* Not the prerelease date. Same value as set release date.
    """
    price_data_columns =["date_unix", "datetime", "price_dollars"]
    occ_data_columns = [
        'card',
        'date',
        'date_unix',
        'raw',
        'event',
        'deck_nums',
        '1st Place',
        '2nd Place',
        '3rd Place',
        '4th Place',
        '5th Place',
        '6th Place',
        '7th Place',
        '8th Place',
        '9th Place',
        '10th Place',
        '11th Place',
        '12th Place',
        '13th Place',
        '14th Place',
        '15th Place',
        '16th Place',
        '(9-0)',
        '(8-0)',
        '(7-0)',
        '(6-0)',
        '(5-0)',
        '(6-1)',
        '(5-2)',
        '(8-1)',
        '(7-2)',
        '(7-1)',
        '(6-2)']

    def __init__(self, id=-1, title="", occ = pd.DataFrame(columns=occ_data_columns), price=pd.DataFrame(columns=['date','price']),tix=pd.DataFrame(columns=['date','price']),
                set=None,echo_id=-1,rarity=None, release_date = None, rotation_date=None):

        """Init of a card object."""
        assert isinstance(occ, pd.DataFrame), "non dataframe passed through occ"
        assert isinstance(price, pd.DataFrame), "non dataframe passed through price"
        self.id = id
        self.title = title
        self.release_date = release_date
        self.rotation_date = rotation_date
        self.occ = occ
        self.price = price
        self.tix = tix
        self.set = set
        self.echo_id = echo_id
        self.rarity = rarity

    def __repr__(self):
        object = {
            'id': self.echo_id,
            'title': self.title,
            'release_date': datetime.strftime(self.release_date, "%Y-%m-%d") if self.release_date!=None else None,
            'rotation_date': datetime.strftime(self.rotation_date, "%Y-%m-%d") if self.rotation_date!=None else None,
            'set': self.set,
            'rarity':self.rarity
        }
        return ("(%s, %s)" % (object['title'], object['id']))

    def __eq__(self, o):
        """ Returns True or False based on echo_id"""
        return isinstance(o, Card) and o.echo_id == self.echo_id

    def __str__(self):
        """ Returns readable string of card.
        Important for logging and such."""
        return str(self.echo_id) + "-" + str(self.title)

    def isEmpty(self):
        """ Deprecated from other versions"""
        #TODO
        return False;

    def dateparse(time_unix):
        """ Converts unix timestamp into string"""
        return datetime.utcfromtimestamp(int(time_unix)/1000).strftime('%Y-%m-%d %H:%M:%S')

    def CardPrices(self, start=None, end=None):
        """ Returns an of array of CardPrice objects from the start and end dates.

        Args:
            start: a datetime indicating the start of desired CardPrice retrieval.
            end: a datetime indication the end of desired CardPrice retrieval
        """
        if start == None:
            start = card.release_date
        if end == None:
            end=date.today()

        prices = []
        for day in daterange(start, end):
            try:
                prices.append(CardPrice(self, day))
            except DatePricingError as e:
                print("No Price info on day ", day)
        return prices

class CardOccurance:
    """CardOccurance Datatype

    Sometimes the name 'play' is used as a synonym for CardOccurance.

    The CardOccurance datatype is used as a wrapper class of the Card datatype.
    CardOccurance holds a card as well as a date which the occurance takes place.
    Unlike Card, CardOccurance's price and tix attribute is a float, instead of a dataframe.
    This is because the price of a CardOccurance coorelates to the price of the
    associated card at the date it was played.

    Attributes:
        card: As Card object representing the associated card of the card Occurance.
        event: An Event object representing the Event the card was played in.
        occ: A JSON object (Python Dictionary) of the occurance data.
        date: A datetime object of the play date.
        format: A string of the format of the event the card appeared in. 'pioneer', 'standard', 'modern', etc
        id: A string as a unique row identifier for a MySQL database of form '<card.echo_id>:<event.id>:<date>'
        price: A float of the paper cost of the card the day of the event.
        tix. A float of the MTGO cost of the card the day of the event.
    """
    def __init__(self, card, event, occ, date=None):
        """Initialization of the Card with Card, Event, and occ data mandatory"""
        self.card = card
        self.event = event
        self.format = event.format
        self.occ = occ
        if not date==None:
            self.date = date
        else:
            self.date = event.date
        self.id = str(card.echo_id)+ ":" + str(event.id)+ ":" + str(self.date)


    def __repr__(self):
        """ Provides a json based represenation of the CardOccurance object """

        object = {
            "event": self.event.__repr__(),
            "occ": self.occ
        }
        return object

    def __eq__(self, o):
        """Overrides the == operator to establish equality based on the card and the event"""
        isinstance(o, CardOccurance) and self.card == o.card and self.event == o.event

class Set:
    """Set Datatype

    TODO description

    Attributes:
        TODO
    """
    def __init__(self, code, title=None, release_date=None, prerelease_date=None, echo_url=None, rot_out_standard=None, tot_rares=None, tot_mythics=None):
        """Initialization of the Set"""
        self.code = code
        self.title = title
        self.release_date=release_date
        self.prerelease_date=prerelease_date
        self.echo_url=echo_url
        self.rot_out_standard=rot_out_standard
        self.tot_rares=tot_rares
        self.tot_mythics=tot_mythics


    def __repr__(self):
        return "<({}) {}>".format(self.code, self.title)

    def __str__(self):
        return self.title

    def __eq__(self, o):
        """Overrides the == operator to establish equality based on the card and the event"""
        isinstance(o, Set) and self.code == o.code

class CardPrice:

    """CardPrice Datatype

    The CardPrice datatype is used as a wrapper class of the Card datatype.
    CardPrice holds a card as well as a date for when the card was at that price.
    Unlike Card, CardPrice's price and tix attribute is a float, instead of a dataframe.
    This is because the price of a CardPrice's price  coorelates to the price of the
    associated card at the date it was played.

    Attributes:
        card: As Card object representing the associated card of the card Occurance.
        date: A datetime object of the play date.
        id: A string as a unique row identifier for a MySQL database of form '<card.echo_id>:<date>'
        price: A float of the paper cost of the card the day of the event.
        tix. A float of the MTGO cost of the card the day of the event.
    """
    def __init__(self, card, date, price=None, tix=None):
        self.card = card
        self.date = date
        if price==None:
            try:
                self.price = self.card.price.loc[self.date]['price']
            except KeyError as e:
                print(e)
                print("Price at date : ", self.date, " unavailable.")
                self.price=None

        if tix ==None:
            try:
                self.tix = self.card.tix.loc[self.date]['price']
            except KeyError as e:
                print(e)
                print("tix at date : ", self.date, " unavailable.")
                self.tix=None

        if self.price==None and self.tix==None:
            print(date)
            raise DatePricingError("No Pricing History")

class Database:
    """A Class for the Database object

    Database is used as an object which interacts with a MySQL database. Check GITHUB page for schema details on MySQL database.

    Attributes:
        config: path to file containing database connection information
        cnx: a mysql-connector connection.

    """
    def __init__(self, path = '../config.json'):
        """Inits Database with specified config file. On reading of config

        Args:
            path: a string '/path/to/config.json'

        """
        try:
            with open(path, 'r') as json_file:
                text = json_file.read()
                json_data = json.loads(text)
                self.config = json_data
            self.cnx = mysql.connector.connect(user=self.config["database"]["user"], password=self.config["database"]["password"],
                                          host=self.config["database"]["host"],
                                          database= (self.config["database"]["dev_database_name"] if self.config["dev"]=="True" else self.config["database"]["database_name"]))

        except Exception as e:
            # TODO: throw custom exception for error on initial
            print(e)
            self.cnx = None
            self.config = None

    def __del__(self):
        """Closes cnx connection"""
        self.cnx.close()

    def isConnected(self):
        """Returns if connection is connected"""
        if(self.cnx != None):
            return True
        else:
            return False

    def addCard(self, card):
        # TODO: upload release date too
        """Adds Card Model to Database.

        Args:
            card: A Card object which contains title, set, echo_id, and release_date.

        """
        cursor = self.cnx.cursor()
        insert_card = ("INSERT INTO cards"
                        """(title,code, echo_id, rarity)"""
                        "VALUES (%s, %s, %s, %s)")
        insert_card_data = (card.title, card.set, card.echo_id, card.rarity)
        try:
            cursor.execute(insert_card, insert_card_data)
            self.cnx.commit()
        except Exception as err:
            print(err)
            return False
        id = cursor.lastrowid
        return id

    def addCards(self, cards):
        """Adds list of Cards to database using addCard()

        Args:
            cards: an array of cards.
        """
        for card in cards:
            self.addCard(card)
            print(card)

    def getSets(self, from_date= date(2017, 9, 28)):
        """Retrieves all sets in the Sets table.

        Returns:
            Array of Set objects.
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `sets` ")
        cursor.execute(query)
        sets = []
        for row in cursor.fetchall():
            sets.append(Set(row['code'], title=row['title'], prerelease_date=row['prerelease_date'], echo_url=row['echo_url'],
                release_date=row['release_date'], rot_out_standard=row['rot_out_standard'], tot_rares=row['tot_rares'], tot_mythics=row['tot_mythics']))
        return sets

    def getCards(self, from_date= date(2017, 9, 28)):
        """Retrieves all cards in the Cards table.

        Returns:
            Array of Card objects.
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `cards` "
                " WHERE rotation_date is NULL OR rotation_date >= %s ")
        vals = (from_date,)
        cursor.execute(query,vals)
        cards = []
        for row in cursor.fetchall():
            cards.append(Card(title=row['title'], set = row['code'], echo_id = row['echo_id'], rarity=row['rarity'], rotation_date=row['rotation_date']))
        return cards

    def getCardByTitle(self, title, date=date.today()):
        # RESOLVE: What happens when there is no card by this name?
        """Retrieves one card from the database by title.

        Retrieves a card from the cards table. If multiple cards are queried (IE two of the same card from different
        sets) then the date arg is used to reconcile which age of card is required. The most recent version available
        is always returned.

        For example:
            Sorcerous Spyglass returns two cards, one from Ixilan and Eldrain. By passing in a date (date of event) we can further
            filter our results. If the event occured before the release of Eldrain then the Ixilan version is return.

        Args:
            title: a string of the title of the desired card.
            date: a datetime object to resolve multiple cards of the same name.

        Returns:
            A Card object.
        """

        #TODO factorin rotation_date
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT `cards`.`title`, `cards`.`code`, `cards`.`echo_id`, `cards`.`rarity`, `sets`.`release_date`, `sets`.`rot_out_standard` "
        "FROM `cards` INNER JOIN `sets` ON `cards`.`code`=`sets`.`code`"
        "WHERE `cards`.`title` = %s AND `sets`.`release_date` <= %s ORDER BY `sets`.`release_date` DESC")
        values = (title, date)
        try:
            cursor.execute(query, values)
        except Exception as err:
            print(err)
            return False

        try:
            data = cursor.fetchall()[0]
        except IndexError:
            return False

        return Card(title=data['title'], set=data['code'], echo_id=data['echo_id'], rarity=data['rarity'], rotation_date=data['rot_out_standard'])

    def getCardByID(self, id, date=date.today()):
        """Retrieves one card from the database by ECHO ID.

        Retrieves a card from the cards table. If multiple cards are queried (IE two of the same card from different
        sets) then the date arg is used to reconcile which age of card is required. The most recent version available
        is always returned.

        For example:
            Sorcerous Spyglass returns two cards, one from Ixilan and Eldrain. By passing in a date (date of event) we can further
            filter our results. If the event occured before the release of Eldrain then the Ixilan version is return.

        Args:
            title: a string of the title of the desired card.
            date: a datetime object to resolve multiple cards of the same name.

        Returns:
            A Card object.
        """
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `cards` WHERE `echo_id` = %s AND `release_date` <= %s ORDER BY `release_date` DESC")
        values = (id, date)
        try:
            cursor.execute(query, values)
        except Exception as err:
            print(err)
            return False

        try:
            data = cursor.fetchall()[0]
        except IndexError:
            return False

        return Card(title=data['title'], set=data['code'], echo_id=data['echo_id'], rarity=data['rarity'], rotation_date=rotation_date['rotation_date'])

    def addEvent(self, event):
        """Adds Event object to database

        Args:
            event: An Event object

        Returns: A boolean, True if successful addition, False if failed.
        """
        cursor = self.cnx.cursor()
        insert_tournament = ("INSERT INTO tournaments"
                            """(date, url, format, id)"""
                            "VALUES (%s, %s, %s, %s)")
        insert_values = (event.date, event.event_url, event.format, event.id)
        try:
            cursor.execute(insert_tournament, insert_values)
            self.cnx.commit()
        except Exception as err:
            print(err)
            return False
        return True

    def addEvents(self, events):
        """Adds list of Event objects using addEvent()"""
        for event in events:
            self.addEvent(event)
        return True

    def getEvents(self, from_date):
        """Retrieves all the events past date (inclusive) """

        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `tournaments` "
                " WHERE date >= %s ")
        vals = (from_date,)
        cursor.execute(query,vals)
        events = []
        for row in cursor.fetchall():
            events.append(Event(row['url'], format=row['format'], date=row['date'], id=['id']))

        return events

    def getLastTimelineDate(self):
        """Deprecated: Retrieves the date of the occurance collected

        This method is useful for when there is weekly/daily collection so a script can pickup where it left off.

        Returns:
            A datetime date object.
        """
        cursor = self.cnx.cursor()
        query = ("""SELECT MAX(date) FROM `card_series`;""")
        try:
            cursor.execute(query)
        except Exception as err:
            print(err)
            return False

        for row in cursor.fetchall():
            if row[0]==None:
                return False
            return row[0]
        return False

    def getLastEventDate(self, format=None):
        """Retrieves the date of the event collected

        This method is useful for when there is weekly/daily collection so a script can pickup where it left off.

        Returns:
            A datetime date object.
        """
        cursor = self.cnx.cursor()
        query = ("""SELECT MAX(date) FROM `tournaments`;""")
        if format!= None:
            query = ("SELECT MAX(date) FROM `tournaments` WHERE `format` = '"+format+"';")
        try:
            cursor.execute(query)
        except Exception as err:
            print(err)
            return False

        for row in cursor.fetchall():
            if row[0]==None:
                return False
            return row[0]
        return False

    def addCardOccurance(self, play):
        """Adds a CardOccurance Object to the Database

        Args:
            play: A CardOccurance object
        """
        assert isinstance(play, CardOccurance), "Expected instance of CardOccurance, got " + str(play)

        cursor = self.cnx.cursor()
        insert = ("INSERT INTO card_series"
                        """(rowid, title,date,tot_occ,event_,format,deck_nums,
                        first_place,secon_place,third_place,fourt_place,
                        fifth_place,sixth_place,seven_place,eigth_place,
                        ninet_place,tenth_place,twelt_place,thtee_place,
                        fotee_place,fitee_place,sitee_place,nineo,eighto,
                        seveno,sixo,fiveo,sixone,fivetwo,eightone,seventwo,
                        sevenone,sixtwo,echo_id)"""
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s)")

        occ = {
            'raw':0,
            '1st Place':0,
            '2nd Place':0,
            '3rd Place':0,
            '4th Place':0,
            '5th Place':0,
            '6th Place':0,
            '7th Place':0,
            '8th Place':0,
            '9th Place':0,
            '10th Place':0,
            '11th Place':0,
            '12th Place':0,
            '13th Place':0,
            '14th Place':0,
            '15th Place':0,
            '16th Place':0,
            '(9-0)': 0,
            '(8-0)': 0,
            '(7-0)': 0,
            '(6-0)': 0,
            '(5-0)': 0,
            '(6-1)': 0,
            '(5-2)': 0,
            '(8-1)': 0,
            '(7-2)': 0,
            '(7-1)': 0,
            '(6-2)': 0
        }
        data = play.occ
        occ.update(data)
        insert_data = (play.id, play.card.title, play.date, occ['raw'], str(play.event.event_url),play.format, len(play.event.decks) , occ['1st Place'],
                                occ['2nd Place'], occ['3rd Place'], occ['5th Place'], occ['6th Place'], occ['7th Place'], occ['8th Place'],
                                occ['9th Place'], occ['10th Place'], occ['11th Place'], occ['12th Place'], occ['13th Place'], occ['14th Place'],
                                occ['15th Place'], occ['16th Place'],occ['(9-0)'],occ['(8-0)'],occ['(7-0)'],occ['(6-0)'],occ['(5-0)'],
                                occ['(6-1)'],occ['(5-2)'],occ['(8-1)'],occ['(7-2)'],occ['(7-1)'],occ['(6-2)'],play.card.echo_id)

        try:
            cursor.execute(insert, insert_data)
        except IntegrityError as err:
            print(err)
            return False
        self.cnx.commit()
        return True

    def addCardPrice(self, cardprice):
        """ Adds CardPrice object to the database.

        Args:
            cardprice: An instance of a CardPrice object to be serialized and added.

        Returns:
            A boolean describing success of database addition.
        """

        assert isinstance(cardprice, CardPrice), "Expected instance of CardPrice, got " + str(play)

        cursor = self.cnx.cursor()
        insert = ("INSERT INTO price_series"
                """(date, title, price, tix, rowid, echo_id)"""
                "VALUES (%s, %s, %s, %s, %s, %s)")
        rowid= str(cardprice.card.echo_id) + ":" + str(cardprice.date)
        cpp = float(cardprice.price) if cardprice.price != None else None
        cpt = float(cardprice.tix) if cardprice.tix != None else None
        insert_data = (cardprice.date, cardprice.card.title, cpp, cpt, rowid, cardprice.card.echo_id)

        try:
            cursor.execute(insert, insert_data)
        except IntegrityError as err:
            print(err)
            return False
        self.cnx.commit()
        return True

    def addCardPrices(self, cardprices):
        """ Adds and array of cardprices"""
        for p in cardprices:
            self.addCardPrice(p)

    def getCardPriceByDate(self, card, date):
        """ Retrieves a the price of a card at a specific date

        Args:
            card: Card object containing data about the desired card price.
            date: datetime of the desired price.
        """

        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `price_series` WHERE `title` = %s AND `date` = %s")
        data = (card.title, date)
        cursor.execute(query, data)
        return cursor.fetchone()

    def getOccurancesByCard(self, card):
        """Retrieves a list of CardOccurance in database based on card"""

        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `card_series` WHERE `title` = '"+card.title+"' ORDER BY `date` DESC")
        cursor.execute(query)

        plays = []
        for p in cursor.fetchall():
            # Building the the Objects that CardOccurance wraps around
            event = Event(event_url=p['event_'], format=p['format'], date=p['date'])

            #Creating a subset of the result to become the CardOccurance.occ attribute
            tuple_not_in_occ = ('title', 'date', 'price', 'tix', 'event_', 'format', 'echo_id', 'rowid');
            occ = {k: p[k] for k in p.keys() if k not in tuple_not_in_occ}

            plays.append(CardOccurance(card, event, occ=occ))

        return plays

    def getCardSeriesDataFrame(self, card, format=None):
        """ Returns a pandas dataframe of card plays by card"""
        cursor = self.cnx.cursor(dictionary=True)

        if format != None:
            query = ("SELECT * FROM `card_series` WHERE `echo_id` = '"+str(card.echo_id)+"' AND `format`='"+format+"' ORDER BY `date` DESC")
        else:
            query = ("SELECT * FROM `card_series` WHERE `title` = '"+card.title+"' ORDER BY `date` DESC")

        cursor.execute(query)

        return pd.DataFrame(cursor.fetchall())

    def getPriceSeriesDataFrame(self, card):
        """ Returns a pandas dataframe of prices by card"""
        cursor = self.cnx.cursor(dictionary=True)

        query = ("SELECT * FROM `price_series` WHERE `title` = '"+card.title+"' ORDER BY `date` ASC")

        cursor.execute(query)

        return pd.DataFrame(cursor.fetchall())

    def getTournamentSeriesDataFrame(self, format=None):
        """ Returns a pandas dataframe of all events based on MTG event format"""
        cursor = self.cnx.cursor(dictionary=True)

        if format != None:
            query = ("SELECT * FROM `tournaments` WHERE `format`='"+format+"' ORDER BY `date` DESC")
        else:
            query = ("SELECT * FROM `tournaments` WHERE 1 ORDER BY `date` DESC")

        cursor.execute(query)

        return pd.DataFrame(cursor.fetchall())

    def eventCollected(self, event):
        """Checks if event has been collected"""
        cursor = self.cnx.cursor()


        query = ("SELECT COUNT(1) FROM `tournaments` WHERE `id` = "+str(event.id))
        cursor.execute(query)

        if cursor.fetchone()[0] == 0:
            return False
        return True

    def allPlaysRecorded(self, card):
        """ Returns boolean if all plays for a card have been recorded into the database"""
        play_count_query = ('SELECT COUNT(*) FROM `card_series` WHERE `title` =  "'+card.title+'"')
        event_count_query = ('SELECT COUNT(*) FROM `tournaments` WHERE `date` >= "'+datetime.datetime.strftime(card.release_date, '%Y-%m-%d') +'"')

        cursor = self.cnx.cursor()
        cursor.execute(play_count_query)
        play_count = cursor.fetchone()[0]

        cursor = self.cnx.cursor()
        cursor.execute(event_count_query)
        event_count = cursor.fetchone()[0]

        if(play_count>event_count):
            print("WARNING play count > event_count!!!!")
        return(play_count >= event_count)

    def getLastCardPriceByCard(self, card):
        """ Returns last price collected for card"""
        query = ('SELECT max(`date`) FROM `price_series` WHERE `title` = "'+card.title+'"')
        cursor = self.cnx.cursor()
        cursor.execute(query)
        result = cursor.fetchone()[0]
        return result if result != None else None

    def searchCards(self, string):

        query = ('SELECT * FROM `cards` WHERE `title` LIKE "%'+string+'%"')
        cursor = self.cnx.cursor()
        cursor.execute(query)
        cards =[]
        for row in cursor.fetchall():
            cards.append(Card(title=row[0],set = row[1], echo_id = row[5], rarity=row[4], release_date=row[2], rotation_date=row[3]))
        return cards

    def searchDate(self, string):
        cursor = self.cnx.cursor(dictionary=True)
        query = ("SELECT * FROM `card_series` WHERE `date` = '"+string+"' ORDER BY `date` DESC")
        cursor.execute(query)

        plays = []
        for p in cursor.fetchall():
            # Building the the Objects that CardOccurance wraps around
            event = Event(event_url=p['event_'], format=p['format'], date=p['date'])

            #Creating a subset of the result to become the CardOccurance.occ attribute
            tuple_not_in_occ = ('title', 'date', 'price', 'tix', 'event_', 'format', 'echo_id', 'rowid');
            occ = {k: p[k] for k in p.keys() if k not in tuple_not_in_occ}

            #TODO append occurance

        return plays

class Event:
    """Event Datatype

    Event class is used to represent one event from MTG Goldfish. The Events class acts as a model for one row in a MySQL database.

    Attributes:
        event_url: A string of format "/tournament/<int number>". This is a relative url on www.mtggoldfish.com.
        decks: An array if deck id's from mtggoldfish.com. Represntative of the decks that placed in the event.
        date: A date object at the day the event occured.
        id: An int pulled from event_url as a unique id for the event.
        format: A str representation of format. 'standard','pioneer','modern'
    """

    def __init__(self, event_url, decks=[], id=-1, date="", format=None):
        """Inits Event with an event url"""
        self.event_url = event_url
        self.decks = decks
        self.date = date
        self.id = id
        self.format = format
        if id==-1 and event_url:
            self.id = int(event_url.split('/')[-1])

    def __str__(self):
        """Converts to printable string"""
        #return self.event_url +" : "+ datetime.strftime(self.date, "%Y-%m-%d")
        return self.event_url +" : "+ datetime.strftime(self.date, "%Y-%m-%d")

    def __eq__(self, o):
        """Overides == operator : compares based on Event.id"""
        return isinstance(o, Event) and self.id == o.id

    def __repr__(self):
        object = {
            "id":self.id,
            "event_url" :self.event_url,
            "format": self.format,
            "date": datetime.strftime(self.date, "%Y-%m-%d"),
            "decks": self.decks,
        }
        return ("(%s)" %  (self.id) )

    def getEventURL(self):
        """Deprecated: Getter for event_url"""
        return self.event_url

    def getDecks(self):
        """Deprecated: Getter for decks"""
        return self.decks

    def isEmpty(self):
        """Returns Status of empty"""
        return len(self.decks) == 0;

    def getDate(self):
        """Gives string representation of date"""
        return datetime.strftime(self.date, "%Y-%m-%d")
        #return self.date

    def setDecks(self, decks):
        """Deprecated: Setter of decks"""
        self.decks = decks

    def addDeck(self, deck):
        """Adds deck to decks"""
        self.decks.append(deck);
        return deck

    def getID(self):
        """Deprecated: Getter of id"""
        return self.id

    def setOcc(self, occ):
        """Deprecated: setter of occ"""
        self.occ = occ

    def getOcc(self):
        """Deprecated: getter of occ"""
        return self.occ

    def setCardOccurances(self, cards):
        """Deprecated: setter of occurance objects"""
        self.card_occurances = cards

    def addCardOccurance(self, card_occurance):
        """Deprecated: adds one occurance to occurance objects"""
        if(card_occurance not in self.card_occurances):
            self.card_occurances.append(card_occurance)
            return True
        return False

    def getCardOccurances(self):
        """Deprecated: getter of card_occurances"""
        return self.card_occurances
