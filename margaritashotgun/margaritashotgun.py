#!/usr/bin/env python

from margaritashotgun.cli import cli

class margaritashotgun():

    def run(self):
        c = cli()
        c.run()


if __name__=="__main__":
    ms = margaritashotgun()
    ms.run()

