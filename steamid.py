import os
import sys
import argparse
import urllib.request
import re
from bs4 import BeautifulSoup
import json

"""
Given a Steam game's numeric ID, this function finds what game the ID corresponds to, if it does exist,
by opening the corresponding Steam store page URL.

Input
    gameID (str) - the Steam game's numeric app ID

Output
    (str) - a string containing the game's name
"""
def game_lookup(gameID: str) -> str:
    with urllib.request.urlopen('https://store.steampowered.com/app/'+gameID) as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
        title = soup.title.string

        # If we are redirected to the main steam store page, then the game does not exist
        if 'Welcome to Steam' in title:
            print(f'Invalid game {gameID}')
            return ''
                            
        title = re.sub('^Save [0-9]?[0-9]% on ', '', title[:-9]) #strip sale information from game title as well as the ' on Steam' string

        print(f'{gameID} - {title}')
        return title


"""
Given a Steam Workshop mod's numeric ID, this function finds what mod the ID corresponds to, if it does exist,
by opening the corresponding Steam Community page URL. It retrieves the mod name, and any further information
provided on the right panel, which may include file size, date posted, and date updated. This function returns
a dictionary containing the id, name, and the attributes.

Input
    modID (str) - the Steam Workshop mod's numeric ID

Output
    (dict) - a dictionary containing at least the mod ID, the mod name, and the attributes available (if any), or None if the mod does not exist
"""
def mod_lookup(modID: str) -> dict:
    with urllib.request.urlopen('https://steamcommunity.com/sharedfiles/filedetails/?id='+modID) as f:

            modInfo = dict()
            modInfo['id'] = modID

            soup = BeautifulSoup(f.read(), 'html.parser')
            title = soup.title.string
            if 'Steam Community :: Error' in title:
                print(f'\tInvalid mod {modID}')
                return None
            
            print(f'\t{modID} - {title[16:]}') #strip the "Steam Workshop::" string from title
            modInfo['mod_name'] = title[16:]
            details = soup.find_all(attrs={'class':'detailsStatRight'})
            detailLables = soup.find_all(attrs={'class':'detailsStatLeft'})
            for i in range(len(detailLables)):
                print(f'\t\t{detailLables[i].string.strip().lower().replace(" ","_")}: {details[i].string}')
                modInfo[detailLables[i].string.strip().lower().replace(" ","_")] = details[i].string
            return modInfo

"""
Given a path to a folder containing mod folders for a specific game, this function returns the mod details from the 
mod_lookup() function for all mod ID's contained within, all encapsulated as dict objects in a list.

Input
    path (str) - the path to a game folder containing mod folders

Output
    (list) - a list of dicts containing mod information from mod_lookup for each mod in the game folder
"""
def mods_loop(path: str) -> list:
    with os.scandir(path) as moddirs:
        modsList = []
        for moddir in moddirs:
            modObject = mod_lookup(moddir.name)
            if(modObject):
                modsList.append(modObject)
        return modsList

"""
Given a path to a Steam Workshop content folder containing game folders, this function iterates over all
game folders, gets the name of the game the folder's ID corresponds to, and then gets mod information for each
mod folder within the game folder. All this information for all games is encapsulated in a dict object (for JSON dumping).

Input
    path (str) - the path to a Steam Workshop content folder containing game folders

Output
    (dict) - a dict containing a list of game dict objects, which contain game and mods info for each game.
"""
def games_loop(path: str) -> dict:
    with os.scandir(path) as gamedirs:
        games = dict()
        gamesList = []
        for gamedir in gamedirs:
            name = game_lookup(gamedir.name)
            if name:
                gameObject = dict()
                gameObject['id'] = gamedir.name
                gameObject['game_name'] = name
                gameObject['mods'] = mods_loop(path+gamedir.name)
                gamesList.append(gameObject)
        games['games'] = gamesList
        
        return games
'''
def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        usage = "%(prog)s [OPTION] [FILE]",
        description='Find the name, file size, and last update date of mod(s) from their steamIDs'
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-p', '--content_path', type=str,action='store', help='the path to a workshop content folder')
    group.add_argument('-g', '--game_path', type=str,action='store', help='the path to a game folder')
    group.add_argument('-m', '--mod_path', type=str,action='store', help='the path to a mod folder')

    group.add_argument('-i', '--game_id', type=str,action='store', help='a game id to find the game name for')
    group.add_argument('-j', '--mod_id', type=str,action='store', help='a mod id to find the mod details for')

    parser.add_argument('-o','--output_file', type=str, action='store', help = 'the file path to output JSON data to')

    return parser
'''
if __name__ == '__main__':
    # parser = init_argparse()
    # args = parser.parse_args()
    # print(vars(args))
    path = 'C:/Program Files (x86)/Steam/steamapps/workshop/content'
    if os.path.exists(path):
        path = os.path.join(path, '') #ensure path name has trailing slash
        
        res = games_loop(path)
        print(res)
        js = json.dumps(res, indent = 4, sort_keys=True)
        with open('data.json', 'w') as f:
            json.dump(res, f)
        print(js)
