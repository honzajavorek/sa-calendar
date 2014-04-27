# sa-calendar

My personal calendar of booked [Student Agency](http://www.sa.cz) bus journeys.

## Status: ACTIVE

Under active development and maintenance.

## Installation

```python
$ pip install -r requirements.txt
```

## Usage

```bash
$ export SA_USERNAME=983498345
$ export SA_PASSWORD=4czQI7PstC
$ python sa_calendar.py
```

...or, for production deployment replace the last line with following:

```bash
$ gunicorn sa_calendar:app
```

There's also a `Procfile` for [Heroku](https://www.heroku.com/) deployment.

## License

This work is [public domain](http://unlicense.org).
