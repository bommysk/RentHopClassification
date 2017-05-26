#!/usr/local/bin/python3
#
# Example program using irc.bot.
#
# Joel Rosdahl <joel@rosdahl.net>
# slight modifications by Foaad Khosmood and Shubham Kahal.

"""A simple example bot.
This is an example bot that uses the SingleServerIRCBot class from
irc.bot.  The bot enters a channel and listens for commands in
private messages and channel traffic.  Commands in channel messages
are given by prefixing the text by the bot name followed by a colon.
It also responds to DCC CHAT invitations and echos data sent in such
sessions.
The known commands are:
    stats -- Prints some channel information.
    disconnect -- Disconnect the bot.  The bot will try to reconnect
                  after 60 seconds.
    die -- Let the bot cease to exist.
    dcc -- Let the bot invite you to a DCC CHAT connection.
"""

import irc.bot
import irc.strings
from irc.client import ip_numstr_to_quad, ip_quad_to_numstr
import re
from getBB import get_mls_html_data

def get_quantity_data(mls_html_data, amount, query):
    club_data = {}
    result = ""

    if query == "W-L-T"

    for mls_data in mls_html_data:
        club_data[mls_data["Club"]] = float(mls_data[query])

    sorted_data = sorted(club_data.items(), key=lambda x: x[1])
    greatest_amount = sorted_data[-1][1]
    least_amount = sorted_data[0][1] 

    print(sorted_data)

    if (amount == "most" or amount == "greatest"):
        for key in club_data:
            if club_data[key] == greatest_amount:
                result += key + ", "  
    elif (amount == "least"):
        for key in club_data:
            if club_data[key] == least_amount:
                result += key + ", " 
    else:
        return "Not understood: " + amount + ", please use most, greatest, or least."

    return result[:-2]

def get_conference_specific_quantity_data(mls_html_data, amount, query, conference):
    club_data = {}
    result = ""

    for mls_data in mls_html_data:
        if mls_data["Conference"] == conference:
            club_data[mls_data["Club"]] = float(mls_data[query])

    sorted_data = sorted(club_data.items(), key=lambda x: x[1])

    greatest_amount = sorted_data[-1][1]
    least_amount = sorted_data[0][1] 

    if (amount == "most" or amount == "greatest"):
        for key in club_data:
            if club_data[key] == greatest_amount:
                result += key + ", " 
    elif (amount == "least"):
        for key in club_data:
            if club_data[key] == least_amount:
                result += key + ", "
    else:
        return "Not understood: " + amount + ", please use most, greatest, or least."

    return result[:-2]

class Bot(irc.bot.SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, c, e):
        c.nick(c.get_nickname() + "_")

    def on_welcome(self, c, e):
        c.join(self.channel)

    def on_privmsg(self, c, e):
        self.do_command(e, e.arguments[0])

    def on_pubmsg(self, c, e):
        a = e.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(self.connection.get_nickname()):
            self.do_command(e, a[1].strip())
        return

    def on_dccmsg(self, c, e):
        # non-chat DCC messages are raw bytes; decode as text
        text = e.arguments[0].decode('utf-8')
        c.privmsg("You said: " + text)

    def on_dccchat(self, c, e):
        if len(e.arguments) != 2:
            return
        args = e.arguments[1].split()
        if len(args) == 4:
            try:
                address = ip_numstr_to_quad(args[2])
                port = int(args[3])
            except ValueError:
                return
            self.dcc_connect(address, port)
                
    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        what_question = re.compile(r'What is the (.*) of (.*)\?')
        which_question = re.compile(r'Which club or clubs have the (.*) (.*)\?')    
        which_question_eastern_conference = re.compile(r'Which club or clubs in the Eastern Conference have the (.*) (.*)\?')
        which_question_western_conference = re.compile(r'Which club or clubs in the Western Conference have the (.*) (.*)\?')
        how_question = re.compile(r'How many (.*) does (.*) have\?')

        mls_html_data = get_mls_html_data()

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        elif cmd == "dcc":
            dcc = self.dcc_listen()
            c.ctcp("DCC", nick, "CHAT chat %s %d" % (
                ip_quad_to_numstr(dcc.localaddress),
                dcc.localport))
        elif cmd == "hello": #Foaad: change this
            c.privmsg(self.channel, "Hello! Ready to explore some MLS data?")
        elif cmd == "yes": #Foaad: change this
            c.privmsg(self.channel, "Great! Let's get started, please ask me some questions.")
        elif cmd == "no": #Foaad: change this
            c.privmsg(self.channel, "No Problem! I'm here if you change your mind.")
        elif what_question.fullmatch(cmd):
            query = what_question.fullmatch(cmd).group(1)
            club = what_question.fullmatch(cmd).group(2)

            for mls_data in mls_html_data:
                if mls_data["Club"] == club:
                    c.privmsg(self.channel, mls_data[query])
        elif how_question.fullmatch(cmd):
            query = how_question.fullmatch(cmd).group(1)
            club = how_question.fullmatch(cmd).group(2)

            for mls_data in mls_html_data:
                if mls_data["Club"] == club:
                    c.privmsg(self.channel, mls_data[query])
        elif which_question.fullmatch(cmd):
            amount = which_question.fullmatch(cmd).group(1)
            query = which_question.fullmatch(cmd).group(2)
            result = get_quantity_data(mls_html_data, amount, query)

            c.privmsg(self.channel, result)
        elif which_question_eastern_conference.fullmatch(cmd):
            amount = which_question_eastern_conference.fullmatch(cmd).group(1)
            query = which_question_eastern_conference.fullmatch(cmd).group(2)
            result = get_conference_specific_quantity_data(mls_html_data, amount, query, "Eastern Conference")

            c.privmsg(self.channel, result)
        elif which_question_western_conference.fullmatch(cmd):
            amount = which_question_western_conference.fullmatch(cmd).group(1)
            query = which_question_western_conference.fullmatch(cmd).group(2)
            result = get_conference_specific_quantity_data(mls_html_data, amount, query, "Western Conference")

            c.privmsg(self.channel, result)          
        elif cmd == "about": #Foaad: add your name
            c.privmsg(self.channel, "I was made by Shubham Kahal for the CPE 466 class in Spring 2017. Use the bot by typing MLSBot: [QUESTION]. See usage for more details.")
        elif cmd == "usage":
            #Foaad: change this
            c.privmsg(self.channel, "I can answer questions like this: Which club or clubs have the most W? Which club or clubs in the [CONFERENCE] have the most W? What is the GP of [CLUB]? How many L does [CLUB] have? Please only use fields from the tables in https://www.mlssoccer.com/standings.") 
        else:
            c.notice(nick, "Not understood: " + cmd)

def main():
    import sys
    if len(sys.argv) != 4:
        print("Usage: testbot <server[:port]> <channel> <nickname>")
        sys.exit(1)

    s = sys.argv[1].split(":", 1)
    server = s[0]
    if len(s) == 2:
        try:
            port = int(s[1])
        except ValueError:
            print("Error: Erroneous port.")
            sys.exit(1)
    else:
        port = 6667
    channel = sys.argv[2]
    nickname = sys.argv[3]

    bot = Bot(channel, nickname, server, port)
    bot.start()

if __name__ == "__main__":
    main()
