###
# Copyright (c) 2012, dan
# All rights reserved.
#
#
###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks

import math
import urllib2
import datetime
from local import rfc3339
from urllib import urlencode


class TvRage(callbacks.Plugin):
    """Add the help for "@plugin help TvRage" here
    This should describe *how* to use this plugin."""
    threaded = True

    def __init__(self, irc):
        self.__parent = super(TvRage, self)
        self.__parent.__init__(irc)
        
        self.months = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}


    def tvrage(self, irc, msg, args, opts, text):
        """[-n] [-l] [-e] <tv show name>
        information about a tv show and when it airs. -n for next episode, -l for last episode, and -e for extra info"""

        shownext = False
        showlast = False
        showextra = False
        for opt,val in opts:
            if opt == 'n' or opt == 'next':
                shownext = True
            if opt == 'l' or opt == 'last':
                showlast = True
            if opt == 'e' or opt == 'extra':
                showextra = True

        r = urllib2.urlopen('http://services.tvrage.com/tools/quickinfo.php?%s' % urlencode({'show': text})).read()

        if r.startswith('No Show Results Were Found For'):
            irc.error('No show found')
            return

        showinfo = {}
        for rline in r[5:].splitlines():
            a,b = rline.split('@', 1)
            showinfo[a] = b

        out = []
        out.append('\x02%(Show Name)s (%(Country)s)\x02' % showinfo)
        out.append('\x0307%(Status)s\x03' % showinfo)
        if 'Airtime' in showinfo:
            out.append('\x0307%(Airtime)s\x03' % showinfo)
        if 'Network' in showinfo:
            out.append('\x0307on %(Network)s\x03' % showinfo)
        irc.reply(' / '.join(out), prefixNick=False)

        date_now = rfc3339.now()

        if shownext:
            if 'Next Episode' in showinfo:
                epnumber, epname, epdate = showinfo['Next Episode'].split('^')
                date_next = rfc3339.parse_datetime(showinfo['RFC3339'])
                delta_next = date_next - date_now

                if delta_next.days > 1:
                    from_now = '%s days from now' % delta_next.days
                else:
                    td = delta_next
                    hours_from_now = (((td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6) / 60.0 / 60.0)
                    if hours_from_now < 0:
                        from_now = '%.2f hours ago' % (hours_from_now * -1)
                    else:
                        from_now = '%.2f hours from now' % hours_from_now

                irc.reply('\x02Next\x02 /\x0307 %s - %s\x03 / \x0307Airs on %s, %s\x03' % (epnumber, epname, epdate, from_now), prefixNick=False)
            else:
                irc.error('No next episode', prefixNick=False)
        if showlast:
            if 'Latest Episode' in showinfo:
                epnumber, epname, epdate = showinfo['Latest Episode'].split('^')
                irc.reply('\x02Last\x02 /\x0307 %s - %s\x03 / \x0307Aired on %s\x03' % (epnumber, epname, epdate), prefixNick=False)
            else:
                irc.error('No last episode', prefixNick=False)
        if showextra:
            out = []
            if 'Genres' in showinfo:
                genres = showinfo['Genres'].strip()
                if genres[:2] == '| ': genres = genres[2:]

                out.append('\x02Genres\x02/\x0307%s\x03' % genres)
            if 'Runtime' in showinfo:
                out.append('\x02Runtime\x02/\x0307%(Runtime)s\x03' % showinfo)
            if 'Premiered' in showinfo:
                out.append('\x02Premiered\x02/\x0307%(Premiered)s\x03' % showinfo)
            if 'Classification' in showinfo:
                out.append('\x02Classification\x02/\x0307%(Classification)s\x03' % showinfo)
            if out:
                irc.reply('  '.join(out), prefixNick=False)


        irc.reply('\x02Show URL\x02 / \x0307%(Show URL)s\x03' % showinfo, prefixNick=False)

    tvrage = wrap(tvrage, [getopts({'n': '', 'next': '', 'l': '', 'last': '', 'e': '', 'extra': ''}), 'text'])

Class = TvRage


# vim:set shiftwidth=4 softtabstop=4 expandtab:
