import re

class GameState(object):
    def __init__(self):
        self.dice = [0,0]
        self.buttons = [1,0,0,1]

        #[white,black]
        self.pieces = [[0,0],
                       [2,0],[0,0],[0,0],[0,0],[0,0],[0,5],
                       [0,0],[0,3],[0,0],[0,0],[0,0],[5,0],
                       [0,5],[0,0],[0,0],[0,0],[3,0],[0,0],
                       [5,0],[0,0],[0,0],[0,0],[0,0],[0,2],
                       [0,0]]

    def parse(self, bgNotationString):
        #sample backgammon notation: 4-2: 22/18 6/4
        bgNotationString = bgNotationString.strip()
        returnList = re.split('-|: | |/', bgNotationString)
        print returnList
        return returnList


    def SetDice(self, i, j):
        self.dice = [i,j]

    def SetButtons(self, rollDice, sendMove, wrongMove, leaveGame):
        self.buttons = [rollDice, sendMove, wrongMove, leaveGame]

    def MovePieces(self, color, bgNotationString):
        #sample move = ['4', '2', '22', '18', '6', '2']
        move = self.parse(bgNotationString)

        #white color is true
        if color:
            print('white plays')
            self.pieces[25 - int(move[2])][0] -= 1
            self.pieces[25 - int(move[3])][0] += 1
            self.pieces[25 - int(move[4])][0] -= 1
            self.pieces[25 - int(move[5])][0] += 1
        #black color is true
        else:
            print('black plays')
            self.pieces[int(move[2])][1] -= 1
            self.pieces[int(move[3])][1] += 1
            self.pieces[int(move[4])][1] -= 1
            self.pieces[int(move[5])][1] += 1


#test code
a = GameState()
print a.pieces
a.MovePieces(False, '1-1: 24/23 24/23')
print a.pieces