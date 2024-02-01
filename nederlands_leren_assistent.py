"""
Anki Add-on: Nederlands Leren Assistent
based on Reviewer Context Menu Search (https://ankiweb.net/shared/info/359618071), which is based on Glutanimate's addon (https://ankiweb.net/shared/info/869824347).

Adds context menu entries for searching various online search providers.

You can customize the menu entries for online providers by
editing the SEARCH_PROVIDERS list below.

Based on:
'Context Menu Search' by Glutanimate,
'OSX Dictionary Lookup' by Eddie Blundell,
'Search Google Images' by Steve AW,
'GuyB790 'Ultimate Programming Machine' Guy Bidkar & Ofek A.
"""
import urllib
import requests
from bs4 import BeautifulSoup
import aqt
from aqt.qt import *
from aqt.utils import openLink, showInfo
from anki.hooks import addHook

############## USER CONFIGURATION START ##############

# list of tuples of search provider names and urls.
# '%s' will be replaced with the search term
SEARCH_PROVIDERS = [
    # ("&Woorden.nl", ["https://www.woorden.org/woord/%s"]),
    ("&Forvo", ["https://forvo.com/search/%s/nl/"]),
    ("&Reverso", ["https://context.reverso.net/vertaling/nederlands-engels/%s"]),
]

##############  USER CONFIGURATION END  ##############


def lookup_online(text, idx):
    #    text = " ".join(text.split())
    text = urllib.parse.quote(text, encoding="utf8")
    for url in SEARCH_PROVIDERS[idx][1]:
        openLink(url % text)
    return text


def get_definitions(phrase):
    """Defines given phrase through woord.org"""
    TRANSLATE_URL_TEMPLATE = "https://www.woorden.org/woord/%s"

    # Get the contents of the translated phrase page from woord
    result = requests.get(TRANSLATE_URL_TEMPLATE % phrase)
    raw_html = result.text

    soup = BeautifulSoup(raw_html, "html.parser")
    main_element = soup.find_all("div", class_="slider-wrap")[2]
    translations = main_element.find_all("h1")
    descriptions = main_element.find_all(attrs={"style": "color:#000;font-size:10pt"})
    usage_examples = main_element.find_all(attrs={"style": "color:#422526"})

    result = []
    for (i, translation) in enumerate(translations):
        description = descriptions[i].b.text
        usage_example = usage_examples[i].text
        result.append((translation.text, description, usage_example))
    return result


def show_definition(phrase):
    try:
        definitions = get_definitions(phrase.strip())
        textToPrint = ""
        for definition in definitions:
            textToPrint += f"<h1>{definition[0]}</h1><div style='font-size: 16px'><b>Definitie:</b> {definition[1]}<br /><b>Voorbeeld:</b> {definition[2]}</div><br />"
        if textToPrint:
            showInfo(textToPrint, textFormat="rich")
        else:
            showInfo(
                f"<h2>Er zijn geen uitgebreide woordinformatie.</h2><br />",
                textFormat="rich",
            )

    except Exception:
        showInfo(
            f"<h2>Er zijn geen uitgebreide woordinformatie.</h2><br />",
            textFormat="rich",
        )


def add_lookup_action(view, menu):
    selected = view.page().selectedText()

    if not selected:
        return

    suffix = (selected[:20] + "..") if len(selected) > 20 else selected

    menu.addAction("Woordenboekdefinitie").triggered.connect(
        lambda _: show_definition(selected)
    )

    search_menu = None
    if len(SEARCH_PROVIDERS) > 10:
        # search_menu = menu.addMenu(u'&Search for "%s" with...' % suffix)
        search_menu = menu.addMenu('&Zoek "%s" op...' % suffix)

    for idx, provider in enumerate(SEARCH_PROVIDERS):
        if search_menu:
            label = provider[0]
            menu = search_menu
        else:
            label = 'Zoek "%s" op %s' % (suffix, provider[0])
        a = menu.addAction(label)
        a.triggered.connect(lambda _, i=idx, t=selected: lookup_online(t, i))


addHook("AnkiWebView.contextMenuEvent", add_lookup_action)
addHook("EditorWebView.contextMenuEvent", add_lookup_action)
