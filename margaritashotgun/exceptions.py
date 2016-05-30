#!/usr/bin/env python


class LimeError(Exception):
    def __init__(self, *args, **kwargs):
            Exception.__init__(self, *args, **kwargs)
