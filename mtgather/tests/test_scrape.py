from unittest import TestCase
import json
from datetime import datetime
from mtgather import getCardsBySet, getEventsDay, getEventData, getOccDataByEvent, getPaperPriceByCard, getMTGOPriceByCard

''' A Test designed to test the active scraping functions.
This test is especially helpful for when mtggoldfish and mtgecho change
their webpage structures.
'''
class TestLiveScrape(TestCase):
    standards_path = "mtgather/tests/standards.json"
    events_standard = {}
    events_pioneer = {}

    with open(standards_path, 'r') as json_file:
        text = json_file.read()
        standards = json.loads(text)

    def test_getCardsBySet(self):
        sets = self.standards["test_getCardsBySet"]["sets"]

        for set in sets.keys():
            empty = getCardsBySet(set_url = set, rarities=[])
            self.assertEqual(len(empty), 0)

            mythic = getCardsBySet(set_url = set, rarities=['mythic-rare'])
            self.assertEqual(len(mythic), sets[set]['count_mythic'])

            rare = getCardsBySet(set_url = set, rarities=['rare'])
            self.assertEqual(len(rare), sets[set]['count_rare'])

            all = getCardsBySet(set_url = set, rarities=['mythic-rare', 'rare', 'uncommon', 'common'])
            self.assertEqual(len(all), sets[set]['count_rare']+sets[set]['count_mythic']+sets[set]['count_uncommon']+sets[set]['count_common'])

    def test_getEventsDay(self):
        print("\n")
        days = self.standards["test_getEventsDay"]["days"]
        for day in days.keys():
            events_standard = getEventsDay(date=datetime.strptime(day, "%Y-%m-%d"), format='standard')
            self.assertEqual(set([e.event_url for e in events_standard]), set(days[day]['events-standard'].keys()))

            events_pioneer = getEventsDay(date=datetime.strptime(day, "%Y-%m-%d"), format='pioneer')
            self.assertEqual(set([e.event_url for e in events_pioneer]), set(days[day]['events-pioneer'].keys()))

    def test_getEventData(self):
        print("\n")
        #TODO complete test
        days = self.standards["test_getEventsDay"]["days"]
        for day in days.keys():
            events_standard = getEventsDay(date=datetime.strptime(day, "%Y-%m-%d"), format='standard')
            events_pioneer = getEventsDay(date=datetime.strptime(day, "%Y-%m-%d"), format='pioneer')

            for e in events_standard:
                decks_test = self.standards["test_getEventsDay"]["days"][e.getDate()]["events-standard"][e.event_url]["decks"]
                decks = getEventData(e)
                self.assertEqual(set(decks), set(decks_test))

            for e in events_pioneer:
                decks_test = self.standards["test_getEventsDay"]["days"][e.getDate()]["events-pioneer"][e.event_url]["decks"]
                decks = getEventData(e)
                self.assertEqual(set(decks), set(decks_test))

    def test_getOccData(self):
        print("\n")
        #TODO complete test
        days = self.standards["test_getEventsDay"]["days"]
        for day in days.keys():
            events_standard = getEventsDay(date=datetime.strptime(day, "%Y-%m-%d"), format='standard')
            events_pioneer = getEventsDay(date=datetime.strptime(day, "%Y-%m-%d"), format='pioneer')

            for e in events_pioneer:
                decks = self.standards["test_getEventsDay"]["days"][e.getDate()]["events-pioneer"][e.event_url]["decks"]
                occ_test = self.standards["test_getEventsDay"]["days"][e.getDate()]["events-pioneer"][e.event_url]["occ"]
                e.decks = getEventData(e)
                occ = getOccDataByEvent(e, deck_max=16)
                self.assertEqual(occ, occ_test)

            for e in events_standard:
                occ_test = self.standards["test_getEventsDay"]["days"][e.getDate()]["events-standard"][e.event_url]["occ"]
                decks = self.standards["test_getEventsDay"]["days"][e.getDate()]["events-standard"][e.event_url]["decks"]
                e.decks = getEventData(e)
                occ = getOccDataByEvent(e, deck_max=16)
                self.assertEqual(occ, occ_test)
