#!/usr/local/bin/python3

import os, sys, random, requests
from bs4 import BeautifulSoup

def get_mls_html_data():
   #obtain the content of the URL in HTML
   url = "https://www.mlssoccer.com/standings"
   my_request = requests.get(url)

   #Create a soup object that parses the HTML
   soup = BeautifulSoup(my_request.text.replace('<br>', ' '), "html.parser")
   non_break_space = u'\xa0'
   keys = ['#', 'Club', 'PTS', 'PPG', 'GP', 'W', 'L', 'T', 'GF', 'GA', 'GD', 'W-L-T', 'W-L-T']
   conferences = ["Eastern Conference", "Western Conference"]
   conference_counter = 0

   mls_data = []

   #step through the tag hierarchy
   for dataTable in soup.find_all('table', attrs={'class':'standings_table'}):
      conference = conferences[conference_counter]

      table_rows = dataTable.find_all('tr')

      table_rows.pop(0)
      table_rows.pop(0)

      for tr in table_rows:
         table_data = tr.find_all('td')
         td_counter = 0
         
         team_data = {}

         for td in table_data:
            if (td.text == ''):
               continue

            key = keys[td_counter]

            team_data[key] = td.text

            td_counter += 1

         team_data["Conference"] = conference

         mls_data.append(team_data.copy())

      conference_counter += 1

   return mls_data
