

import os
import re
from datetime import datetime

import pytz
import requests
import lxml.html
from flask import Flask
from icalendar import Calendar, Event


USERNAME = os.getenv('SA_USERNAME')
PASSWORD = os.getenv('SA_PASSWORD')

app = Flask(__name__)


@app.route('/')
def calendar():
    sess = requests.Session()

    resp = sess.get('https://jizdenky.studentagency.cz/Login?1')
    dom = lxml.html.fromstring(resp.content, base_url=resp.url)

    form = dom.forms[0]
    data = dict(form.fields,
                passwordAccountCode=USERNAME,
                password=PASSWORD)
    sess.post(form.action, data=data)

    resp = sess.get('https://jizdenky.studentagency.cz/Tickets?7')
    dom = lxml.html.fromstring(resp.content)

    cal = Calendar()
    cal.add('summary', 'Student Agency')

    for tr in dom.xpath("//tr[contains(@class, 'reservation')]"):
        dt_string = ' '.join([
            re.sub(r'[^\d\.]', '', tr[1].text_content()),
            re.sub(r'[^\d:]', '', tr[2].text_content()),
        ])
        dt = datetime.strptime(
            dt_string,
            '%d.%m.%Y %H:%M'
        ).replace(tzinfo=pytz.timezone('Europe/Prague'))

        event = Event()
        event.add('summary', tr[3].text_content())
        event.add('dtstart', dt)
        cal.add_component(event)

    return cal.to_ical()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
