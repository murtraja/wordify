#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wordify.settings")
    import redis
    rd = redis.StrictRedis()
    print "now deleting spellbee*"
    mydict = rd.keys('spellbee*')
    mydict = mydict + rd.keys('ws:broadcast*')
    for k in mydict:
        resp  = rd.delete(k)
        print "deleted:",k
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
