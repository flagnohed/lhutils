# lhutils

lhutils is a third-party tool for Livehockey (www.livehockey.se)
that can give advanced details about players, transfers, rosters, and arenas.

This project tries to follow pylint and black as formatting guidelines.

Common usage:

`
git clone https://github.com/flagnohed/lhutils.git && cd lhutils
`
1. Log in to livehockey.se
2. Go to one of the following:
    
    b. Roster/Spelartrupp
    
    c. Transfers/Transferlista (also, make a search in the transfer list 
                                or show all transfer listed players)
3. Right click anywhere on the screen and choose 'inspect'.
4. Copy the inner HTML of the outermost HTML element.
5. Paste it into the appropriate file in the /html directory.
6. Run main.py with the desired options.

For full usage, run `./main.py {-h, --help}`
while standing in the lhutils directory

Until livehockey releases some kind of public API, this is what you have to do. 
I am not comfortable using webscraping here, as my knowledge is limited and
I am slightly worried about the server capacity, so this will have to do for
now at least.

## TODO
* Enable using CTRL+A instead of copying HTML. Should work for transferlist
and games. Program should automatically detect if the text is HTML or just copied
from what the user sees.

Add parsing of game stats, i.e, game events. 
* Time, type, players involved (1-3), team (h/a)


