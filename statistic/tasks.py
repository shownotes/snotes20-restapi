from __future__ import absolute_import
from shownotes.celery import app

@app.task
def add_test(x, y):
    return(x + y)