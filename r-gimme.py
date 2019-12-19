#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bs4 import BeautifulSoup, SoupStrainer
import requests
import sys
import os

if len(sys.argv) <= 1:
    sys.exit("ERROR: You should provide at least one URL")



columns = int(os.popen('stty size', 'r').read().split()[1])

separator = '-' * columns

sys.argv.pop(0)
for arg in sys.argv:

    try:    
        url = arg
        page = requests.get(url)    
        data = page.text
        soup = BeautifulSoup(data, "html.parser")

        print("\n" + separator) 
        print("\nGetting links from: " + url + "\n") 

        for link in soup.find_all('a'):
            if link.get('href') is not None:
                if link.get('href')[0] == "/": 
                    print(url + link.get('href')) 
                elif link.get('href')[0] == "#":
                    print(url + "/" + link.get('href'))
                else:
                    print(link.get('href'))

        print("\n" + separator + "\n")

    except: 
        sys.exit("ERROR: Not valid URL -->: " + url)
