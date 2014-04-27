

import os
import re
import urlparse
from datetime import datetime

import pytz
import requests
import lxml.html
from flask import Flask
from icalendar import Calendar, Event


USERNAME = os.getenv('SA_USERNAME')
if not USERNAME:
    raise LookupError('Missing SA_USERNAME environment variable.')

PASSWORD = os.getenv('SA_PASSWORD')
if not PASSWORD:
    raise LookupError('Missing SA_PASSWORD environment variable.')


def login(session):
    resp = session.get('https://jizdenky.studentagency.cz/Login?1')
    dom = lxml.html.fromstring(resp.content, base_url=resp.url)

    form = dom.forms[0]
    data = dict(form.fields,
                passwordAccountCode=USERNAME,
                password=PASSWORD)
    session.post(form.action, data=data)


def parse_datetime(date_string, time_string):
    dt_string = ' '.join([
        re.sub(r'[^\d\.]', '', date_string),
        re.sub(r'[^\d:]', '', time_string),
    ])
    dt = datetime.strptime(dt_string, '%d.%m.%Y %H:%M')
    return dt.replace(tzinfo=pytz.timezone('Europe/Prague'))


def parse_detail_url(base_url, button):
    match = re.search(r'location\.href\s?=\s?[\'"]([^\'"]+)',
                      button.get('onclick'))
    parts = urlparse.urlparse(base_url)
    return '{}://{}/{}'.format(parts.scheme, parts.netloc, match.group(1))


def scrape_end_time(session, base_url, tr):
    button = tr.xpath(".//*[contains(@class, 'nav_button')]//button")[0]
    url = parse_detail_url(base_url, button)

    resp = session.get(url)
    dom = lxml.html.fromstring(resp.content)

    tr = dom.xpath("//*[contains(@class, 'routePanel')]//tr")[-1]
    return tr[2].text_content()


def scrape_tickets(session):
    resp = session.get('https://jizdenky.studentagency.cz/Tickets?7')
    dom = lxml.html.fromstring(resp.content)

    for tr in dom.xpath("//tr[contains(@class, 'reservation')]"):
        yield {
            'dtstart': parse_datetime(tr[1].text_content(),
                                      tr[2].text_content()),
            'dtend': parse_datetime(tr[1].text_content(),
                                    scrape_end_time(session, resp.url, tr)),
            'summary': tr[3].text_content(),
        }


def build_ical(tickets):
    cal = Calendar()
    cal.add('summary', 'Student Agency')

    for ticket in tickets:
        event = Event()
        for key, value in ticket.items():
            event.add(key, value)
        cal.add_component(event)

    return cal.to_ical()


app = Flask(__name__)


@app.route('/')
def calendar():
    session = requests.Session()
    login(session)
    return build_ical(scrape_tickets(session))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
