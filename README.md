SweGammon
=========
This is a backgammon game, made for SWE 544 - Internet Programming course in Bogazici University. The game is based on socket programming. The implementation is done with Python programming language..

Server Installation and Running:
- Install Python 2.x to your server. The setup files are downloadable from the address: https://www.python.org/downloads/ 
- Installation shoud be done on C:\Python2x directory on Windows, and in Application folder in Mac OS.
- Change directory to the location of SweGammonServer.py file on terminal. For Python 2.8, Run it in terminal by typing: 
  On Mac OS=> python SweGammonServer.py
  or
  On Windows=> C:\Python28\python SweGammonServer.py

Client Installation and Running:
- Install Python 2.x to your client computer. The setup files are downloadable from the address: https://www.python.org/downloads/ 
- Installation shoud be made on C:\Python2x directory on Windows, and in Application folder in Mac OS.
- Make sure SweGammonServer.py program is running on a server. 
- Change directory to the location of SweGammonClient.py file on terminal. For Python 2.8, Run it in terminal by typing: 
  On Mac OS=> python SweGammonClient.py
  or
  On Windows=> C:\Python28\python SweGammonClient.py
- A login page will show up. 
- Type a user name on Username field. Type ip address of the server on IP Address field. Then click Login button.
- Choose to be a player or to be a watcher.
- The player can start playing a game when an opponent arrives.
- The watcher can start watching a random game if there is a game to watch.

Gameplay:
- Player rolls dice with Roll Dice button.
- Player can send backgammon moves by typing moves depending on standard backgammon notation and clicking Send Move button. This notation can be found in:
  http://www.bkgm.com/faq/BasicRules.html#backgammon_notation
- Move examples: 

  4-3: 8/4 24/21

  4-4: 24/20 24/20 18/14 18/14
  
  3-2: bar/22 4/2
  
  5-4: 5/off 3/off
  
- If a player detects a wrong move from the opponent, he/she can click Wrong Move Alert button and the move is undone.
- If a player wins a game after a move, the opponent cannot see the Roll Dice button active. However, he/she can still click Wrong Move Alert button.
