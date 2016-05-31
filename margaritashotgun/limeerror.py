#!/usr/bin/env python


class limeerror(Exception):
    def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)
