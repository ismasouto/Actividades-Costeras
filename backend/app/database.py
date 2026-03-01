import os
import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager

from app.config import get_settings


def get_connection():
    settings = get_settings()
    return psycopg.connect(settings.database_url, row_factory=dict_row)


@contextmanager
def get_cursor(commit: bool = True):
    conn = get_connection()
    try:
        cur = conn.cursor()
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
    finally:
        conn.close()
