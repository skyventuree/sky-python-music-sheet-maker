# import os
from modes import ReplyType
from communication import Query, Reply, QueryOpen, QueryChoice, QueryBoolean, QueryMemory, Information
import communication
#import copy

"""
Classes to ask and answer questions called Query and Reply between the bot and the music sheet maker
TODO: list of mandatory questions to implement
a) asked by the cog:
- notes, OPEN
- musical notation (if several are found), CHOICE
- music key (if several are found), CHOICE
- song title, OPEN
- song headers, OPEN
- note shift, OPEN with type and range restrictions

b) asked by the bot:
- what are the PNGs?, OPEN with type restriction
- how many PNGs?, OPEN with type and range restrictions

c) asked by the command line:
- what are the files and where are they saved, OPEN

"""


class CommunicatorError(Exception):
    def __init__(self, explanation):
        self.explanation = explanation

    def __str__(self):
        return str(self.explanation)

    pass


class Communicator:

    def __init__(self, owner):
        self.owner = owner
        self.memory = QueryMemory(self.owner)
        self.name = self.owner.get_name()

        # A dictionary of standard queries arguments
        # TODO: create generic (quasi-empty) stock queries, such as Information to output dome text
        self.query_stock = {
            # Queries asked by the Player / Music Cog
            'create_song': {'class': QueryOpen.__name__, 'handler': 'create_song',
                            'question': 'create_song'},
            
            # Generic Query
            'information': {'class': Information.__name__, 'handler': 'None',
                            'question': '', 'reply_type': ReplyType.TEXT},
                            
            # Queries asked by Music Sheet Maker
            'song_overwrite': {'class': QueryBoolean.__name__, 'handler': 'None',
                               'foreword': 'A Song already exists in memory.',
                               'question': 'Do you want to overwrite it?', 'reply_type': ReplyType.TEXT},

            #TODO: Add more verbose instruction
            'instructions': {'class': Information.__name__, 'handler': 'None',
                             'foreword': '===== VISUAL MUSIC SHEETS FOR SKY:CHILDREN OF THE LIGHT =====',
                             'question': ''},

            'song_title': {'class': QueryOpen.__name__, 'handler': 'None',
                           'question': 'What is the song title?', 'reply_type': ReplyType.TEXT},

            'original_artist': {'class': QueryOpen.__name__, 'handler': 'None',
                                'question': 'What is the Original artist(s)?', 'reply_type': ReplyType.TEXT},

            'transcript_writer': {'class': QueryOpen.__name__, 'handler': 'None',
                                  'question': 'What is the transcript writer?', 'reply_type': ReplyType.TEXT},

            'song_notes_files': {'class': QueryOpen.__name__, 'handler': 'None', 'question': 'Please type or copy-paste notes, or enter file name', 'reply_type': ReplyType.TEXT, 'limits': None},

            'song_notes': {'class': QueryOpen.__name__, 'handler': 'None',
                           'question': 'Please type or copy-paste notes', 'reply_type': ReplyType.NOTE, 'limits': None},

            'musical_notation': {'class': QueryChoice.__name__, 'handler': 'None', 'foreword': '\nSeveral possible notations detected.', 'question': 'Please choose your note format', 'reply_type': ReplyType.INPUTMODE,
                                 'limits': []},

            'possible_keys': {'class': QueryChoice.__name__, 'handler': 'None',
                              'question': 'Please choose your musical key', 'reply_type': ReplyType.NOTE,
                              'limits': None},

            'recommended_key': {'class': QueryOpen.__name__, 'handler': 'None',
                                'foreword': 'Your notes use relative pitch notation.',
                                'question': 'What is the recommended key to play in Sky?', 'reply_type': ReplyType.NOTE,
                                'limits': None},

            'octave_shift': {'class': QueryOpen.__name__, 'handler': 'None',
                             'question': 'Do you want to shift by n octaves?', 'reply_type': ReplyType.INTEGER,
                             'limits': [-6, 6]}

        }

    def __str__(self):

        return '<' + self.__class__.__name__ + ' of ' + repr(self.owner.get_name()) + ' with ' + str(
            len(self.memory)) + ' stored queries>'

    def __getattr__(self, attr_name):
        """
        Default function to call in case no one else is found.
        """
        if 'memory' in self.__dict__.keys():
            return getattr(self.memory, attr_name)
        else:
            raise AttributeError("type object " + repr(type(self).__name__) + " has no attribute 'memory")

    def get_name(self):
        return self.name


    def send_stock_query(self, stock_query_name, recipient, **kwargs):
        """
        Create and send a query from a catalog, overriding some parameters with kwargs
        """
        try:
            stock_query_name = stock_query_name.lower().replace(' ', '_')
            stock_query = self.query_stock[stock_query_name]
        except KeyError:
            raise CommunicatorError(str(stock_query_name) + ' is not a standard query')

        method_args = stock_query.copy()
        method_args.pop('class') #The class was used and is not an argument for Query
        method_args.pop('handler') #The handler is not useful here and is not an argument for Query
        method_args['name'] = stock_query_name
        method_args['sender'] = self.owner
        method_args['recipient'] = recipient
        method_args.update(kwargs) #Merge tuples to override default parameters with optional keyword arguments

        query_method = getattr(communication, stock_query['class']) #QueryChoice, QueryOpen, QueryBoolean

        q = query_method(**method_args) #Creates the Query
        self.memory.store(q)
        q.check_sender(allowed=self.owner)
        q.send(recipient=recipient)

        return q

    '''
    def send(self, communication_objects, recipient=None):

        try:
            communication_objects[0]
        except (TypeError, IndexError):
            communication_objects = [communication_objects]

        for obj in communication_objects:
            if isinstance(obj, Query):
                self.send_query(obj, recipient)

    def send_query(self, query, recipient):

        if not self.memory.has_query(query):
            print('I am ' + self.owner.get_name() + ', storing a query before sending.')
            self.memory.store(query)

        query.check_sender(allowed=self.owner)#TODO: previously self.get_name()
        query.send(recipient=recipient)
    '''

    def receive(self, queries):

        if not isinstance(queries, (list, tuple)):
            queries = [queries]

        for q in queries:
            if q.check_recipient(allowed=self.owner):
                self.memory.store(q)
                # TODO: check for duplicates before storing?

    def query_to_stdout(self, query):

        question = query.get_result()
        return question

    def query_to_discord(self, query):

        utils_question = query.get_result()
        return utils_question

    def discord_to_query(self, utils_question):
        
        #TODO: This is the tricky part: how do we transform a free-text question in a precise Query?
        #=> Requires interpreting strings or finding key strings within a sentence
        #This is usually done in the Cog, note here
        return
    
    def send_information(self, recipient, string, prerequisites=None):
        """
        A shortcut to send an information Query. Could be replaced by a stock query though.
        """
        i = Information(sender=self, recipient=recipient, question=string, prerequisites=prerequisites)
        self.memory.store(i)
        i.send(recipient=recipient)
        return i
    
    def translate(self, obj):

        if isinstance(obj, (Query, Reply)):
            self.query_to_discord(obj)
        else:
            self.discord_to_query(obj)
        return

    '''
    def send_unsent_queries(self, recipient=None):

        for q in self.memory.recall_unsent():
            q.send(recipient)
    '''
