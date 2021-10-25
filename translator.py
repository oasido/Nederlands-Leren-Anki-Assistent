import requests
from bs4 import BeautifulSoup


def extract_main_element(phrase):
    TRANSLATE_URL_TEMPLATE = "https://www.woorden.org/woord/%s"

    # Get the contents of the translated phrase page from woord
    result = requests.get(TRANSLATE_URL_TEMPLATE % phrase)
    raw_html = result.text

    soup = BeautifulSoup(raw_html, "html.parser")
    s = soup.find_all("div", class_="slider-wrap")[2]
    return s if len(s) > 0 else None


def translate(phrase):
    main_element = extract_main_element(phrase)
    translations = main_element.find_all("h2")
    descriptions = main_element.find_all(attrs={"style": "color:#000;font-size:10pt"})
    usage_example = main_element.find_all(attrs={"style": "color:#422526"})

    result = []
    for (i, translation) in enumerate(translations):
        description = descriptions[i].b.text
        usage_example = usage_examples[i].text
        result.append((translation.text, description, usage_example))
    return result


print(translate("aanstellen"))
