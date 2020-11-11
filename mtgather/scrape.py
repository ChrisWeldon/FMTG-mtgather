#TODO write docs to this
import sys, os
import requests, json, time
import pandas as pd
from datetime import date, datetime
import numpy as np
from bs4 import BeautifulSoup,  NavigableString, Tag

from mtgather import Card
from mtgather import Event

"""A submodule containing functions to scrape data from the internet.
"""

def getCardsBySet(set_url="/set/THB/theros-beyond-death/", rarities=['rare', 'mythic-rare']):
    """Scrapes a list of cards from the echomytg.

    Args:
        set_url: a string '/path/to/set',
        rarities: an array of strings

    Returns:
        An array of Cards
    """
    url='https://www.echomtg.com' + set_url
    headers = requests.utils.default_headers()
    headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
    page=requests.get(url,headers=headers)
    soup=BeautifulSoup(page.content,'html.parser')

    data = []
    for card in soup.find('table', id='set-table').findAll('tr'):
        if card.find('a', class_='list-item'):
            data.append({'title': card.find('a', class_='list-item').text,
                        'url': card.find('a', class_='list-item')['href'],
                        'rarity': card['class'][0],
                        'id': card.find('a', class_='list-item')['href'].split('/')[2],
                        'set': set_url})

    return_cards = []
    for object in data:
        if object['rarity'] in rarities:
            return_cards.append(Card(echo_id=object['id'], title=object['title'], rarity=object['rarity'], set=object['set']))
    return return_cards

def getEventsDay(date = date.today(), format='standard'):
    """Scrapes a list of Events that occur on one day.

    Args:
        date: a datetime date
        format: the format to collect for

    Returns:
        An array of Events
    """

    url = 'https://www.mtggoldfish.com/deck_searches/create?utf8=✓&deck_search%5Bname%5D=&deck_search%5Bformat%5D='+format+'&deck_search%5Btypes%5D%5B%5D=&deck_search%5Btypes%5D%5B%5D=tournament&deck_search%5Bplayer%5D=&deck_search%5Bdate_range%5D='+str(date.strftime('%m'))+'%2F'+str(date.strftime('%d'))+'%2F'+str(date.strftime('%Y'))+'+-+'+str(date.strftime('%m'))+'%2F'+str(date.strftime('%d'))+'%2F'+str(date.strftime('%Y'))+'&deck_search%5Bdeck_search_card_filters_attributes%5D%5B0%5D%5Bcard%5D=&deck_search%5Bdeck_search_card_filters_attributes%5D%5B0%5D%5Bquantity%5D=1&deck_search%5Bdeck_search_card_filters_attributes%5D%5B0%5D%5Btype%5D=maindeck&deck_search%5Bdeck_search_card_filters_attributes%5D%5B1%5D%5Bcard%5D=&deck_search%5Bdeck_search_card_filters_attributes%5D%5B1%5D%5Bquantity%5D=1&deck_search%5Bdeck_search_card_filters_attributes%5D%5B1%5D%5Btype%5D=maindeck&counter=2&commit=Search'
    headers = requests.utils.default_headers()
    headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})

    tourns = {}
    while url!=None:

        page=requests.get(url,headers=headers)
        soup=BeautifulSoup(page.content,'html.parser')

        if(page.status_code == 500):
            print("Status Code: 500")
            raise ServerError(page.status_code, "Server Error")

        if(str(soup)==str('Throttled\n')):
            print("Throttled")
            raise ThrottleError("Throttled on MTG Goldfish")

        table = soup.find('table', class_='table table-striped')
        if table == None:
            break
        for row in table.findAll('tr'):
            try:
                id = row.findAll('td')[2].find('a')['href']
                if id not in tourns.keys():
                    tourns[id] = row.findAll('td')[0].text
                    print(id, " : ", tourns[id])
            except IndexError:
                continue

        next = soup.find('a', class_='next_page')
        if next == None:
            url  = None
        else:
            url = 'https://www.mtggoldfish.com' +next['href']


    return [Event(key, date=datetime.strptime(tourns[key], "%Y-%m-%d"), format=format) for key in tourns.keys()]

def getEventData(event):
    """Retrieves the ID's of all the deck's that occur in the event
    Note: does not mutate the Event object.

    Args:
        event: an Event obect

    Returns:
        An array of event Id's
    """
    assert isinstance(event, Event)
    url='https://www.mtggoldfish.com' + event.event_url
    headers = requests.utils.default_headers()
    headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
    page=requests.get(url,headers=headers)
    soup=BeautifulSoup(page.content,'html.parser')

    if(page.status_code == 500):
        raise ServerError(page.status_code, "Server Error: getEventData")

    if(str(soup)==str('Throttled\n')):
        raise ThrottleError("Throttled on MTG Goldfish")

    deck_ids = [deck['data-deckid'] for deck in soup.find('table',
    class_='table-tournament').findAll('tr', class_='tournament-decklist')]

    return deck_ids

def getOccDataByEvent(event, deck_max = 16):
    """Retrieves all of the occurance data from the event from mtggoldfish.

    Args:
        event: an Event obect. Must be populated with a deck list.

    Returns:
        A dictionary containing the  occurance data of the event.
    """
    if not isinstance(event, Event):
        print("event is Not instance of Event")
        return False
    if(event.isEmpty()):
        print("Warning: Event is empty" )
    headers = requests.utils.default_headers()
    headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})

    cards = {}
    # get occurance data per deck in event
    decks = event.decks

    if(deck_max != -1):
        decks = decks[:deck_max]
    for id in decks:
        url='https://www.mtggoldfish.com/deck/'+id+'#paper'
        page=requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        try: # No Errors pass Silently PEP 8
            if(page.status_code == 500):
                raise ServerError(page.status_code, "Server Error")
        except ServerError as e:
            print(e)
            continue

        # TODO: Handle Bad Gateway 502
        if(str(soup)==str('Throttled\n')):
            raise ThrottleError("Throttled on MTG Goldfish")

        # deck is private. Not collecting data for private decks
        if 'private' in str(soup.find('div', class_='alert alert-warning')):
            continue



        print(url)
        table = soup.find('table', class_='deck-view-deck-table')
        description = soup.find('p', class_='deck-container-information')
        place = description.findChildren()[1].nextSibling.strip()[2:]

        for tr in table.findAll('tr'):
            qty = tr.find('td', class_='text-right')
            name = tr.find('a')
            if qty:
                name = name.text.strip()
                qty = int(qty.text.strip())
                if name not in cards.keys():
                    cards[name] = {'raw': 0}
                    cards[name]['raw'] =qty #creating quantity for raw occurances
                    cards[name][place] = qty #creating quantity for occurances at that placement
                else:
                    cards[name]['raw'] = cards[name]['raw'] + qty
                    if place not in cards[name].keys():
                        cards[name][place] = qty
                    else:
                        cards[name][place] = cards[name][place] + qty

    return cards

def getPaperPriceByCard(card, foil=False, cutoff_date=None):
    """Retrieves the price of  the paper card from echomtg.

    Args:
        card: A Card object to be retrieved

    Returns:
        A pandas dataframe containing the price series indexed by 1 day.
    """
    assert isinstance(card, Card)
    if not foil:
        url='https://www.echomtg.com/cache/'+str(card.echo_id)+'.r.json'
    else:
        url='https://www.echomtg.com/cache/'+str(card.echo_id)+'.f.json'
    headers = requests.utils.default_headers()
    headers.update({'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'})
    page=requests.get(url,headers=headers)

    price_array = page.json()
    for row in price_array:
        row[0] = datetime.fromtimestamp(int(row[0])/1000)

    df = pd.DataFrame(columns=['datetime', 'price'], data=np.array(price_array))
    dates = pd.date_range(df['datetime'].min(), date.today())
    dates = dates.to_frame(name='datetime')
    df = df.set_index('datetime')

    df = dates.join(df, on='datetime')
    df = df.set_index('datetime')
    df = df.ffill()
    return df

# must be patched, not working currently
def getMTGOPriceByCard(card, foil=False, proxies={}, headers= requests.utils.default_headers()):
    """Retrieves the price of the online card from goatbots.

    Args:
        card: A Card object to be retrieved

    Returns:
        A pandas dataframe containing the price series indexed by 1 day.
    """
    assert isinstance(card, Card)
    title = card.title
    formatted_title = title.replace(" // ", " ").replace(" ", "-").replace(",", "").replace("'", "").lower()
    url = 'https://www.goatbots.com/card/ajax_card?search_name=' + formatted_title

    page=requests.get(url, headers = headers, proxies=proxies)
    print(page.status_code)
    if(page.status_code == 403):
        raise ForbiddenError("Goatbots revolked access to pricing history")
    versions = page.json()[1]

    #v[0] is the first entry a card versions pricing array, v[i][0] is the date in str
    version = versions[0]

    for v in versions:
        version_date = datetime.strptime(v[0][0], "%m/%d/%Y").date()
        if(version_date <= card.release_date):
            version = v
            break

    df = pd.DataFrame(columns=['datetime', 'price'], data=np.array(version))
    df['datetime']  = pd.to_datetime(df['datetime'])

    dates = pd.date_range(df['datetime'].min(), date.today())
    dates = dates.to_frame(name='datetime')
    df = df.set_index('datetime')

    df = dates.join(df, on='datetime')
    df = df.set_index('datetime')
    df = df.ffill()
    return df
