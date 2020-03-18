# Cmput 455 sample code
# UCB algorithm
# Written by Martin Mueller

from math import log,sqrt
from board_util import GoBoardUtil
from pattern_util import PatternUtil
import sys
#from gtp_connection import point_to_coord, format_point

INFINITY = float('inf')

EMPTY = 0
BLACK = 1
WHITE = 2
BORDER = 3
PASS = None
MAXSIZE = 25

def mean(stats, i):
    return stats[i][0] / stats[i][1]
    
def ucb(stats, C, i, n):
    if stats[i][1] == 0:
        return INFINITY
    return mean(stats, i)  + C * sqrt(log(n) / stats[i][1])

def findBest(stats, C, n):
    best = -1
    bestScore = -INFINITY
    for i in range(len(stats)):
        score = ucb(stats, C, i, n) 
        if score > bestScore:
            bestScore = score
            best = i
    assert best != -1
    return best

def bestArm(stats): # Most-pulled arm
    best = -1
    bestScore = -INFINITY
    for i in range(len(stats)):
        if stats[i][1] > bestScore:
            bestScore = stats[i][1]
            best = i
    assert best != -1
    return best

# tuple = (move, percentage, wins, pulls)
def byPercentage(tuple):
    return tuple[1]

# tuple = (move, percentage, wins, pulls)
def byPulls(tuple):
    return tuple[3]


def writeMoves(board, moves, stats):
    gtp_moves = []
    for i in range(len(moves)):
        if moves[i] != None:
            x, y = point_to_coord(moves[i], board.size)
            pointString = format_point((x,y))
        #else:
        #    pointString = 'Pass'
        if stats[i][1] != 0:
            gtp_moves.append((pointString,
                            round(stats[i][0]/stats[i][1],3)))
                            #stats[i][0],
                            #stats[i][1]))
        else:
            gtp_moves.append((pointString,
                            0.0))
                            #stats[i][0],
                            #stats[i][1]))
    #sys.stderr.write("Statistics: {}\n"
    #                 .format(sorted(gtp_moves, key = byPulls,
    #                                           reverse = True)))
    sorted(gtp_moves, key = byPercentage, reverse = True)
    coord = []
    prob = []
    for pair in gtp_moves:
        coord.append(pair[0])
        prob.append(pair[1])
    return coord + prob
    #sys.stderr.flush()

def simulate(board, move, toplay):
        """
        Run a simulate game for a given move.
        """
        cboard = board.copy()
        cboard.play_move(move, toplay)
        opp = GoBoardUtil.opponent(toplay)
        return PatternUtil.playGame(cboard,
                                    opp,
                                    komi=0,
                                    limit=100,
                                    random_simulation = True,      #implement a way to change this accordingly
                                    use_pattern = False,           #implement a way to change this accordingly
                                    check_selfatari = False)

def runUcb(board, C, moves, toplay, sim_num):
    stats = [[0,0] for _ in moves]
    num_simulation = len(moves) * sim_num
    for n in range(num_simulation):
        moveIndex = findBest(stats, C, n)
        result = simulate(board, moves[moveIndex], toplay)
        if result == toplay:
            stats[moveIndex][0] += 1 # win
        stats[moveIndex][1] += 1
    #bestIndex = bestArm(stats)
    #best = moves[bestIndex]

    return writeMoves(board, moves, stats)
    #return best

def point_to_coord(point, boardsize):
    """
    Transform point given as board array index 
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)

def format_point(move):
    """
    Return move coordinates as a string such as 'a1', or 'pass'.
    """
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    #column_letters = "abcdefghjklmnopqrstuvwxyz"
    if move == PASS:
        return "pass"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1]+ str(row) 