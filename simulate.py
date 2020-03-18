#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

#from gtp_connection_go3 import GtpConnectionGo3
#from gtp_connection import point_to_coord, format_point
from board_util import GoBoardUtil
from pattern_util import PatternUtil
from simple_board import SimpleGoBoard
from ucb import findBest, bestArm, runUcb
import numpy as np
import argparse
import sys

EMPTY = 0
BLACK = 1
WHITE = 2
BORDER = 3
PASS = None
MAXSIZE = 25

def byPercentage(pair):
    return pair[1]

def writeMoves(board, moves, count, numSimulations):
    #Write simulation results for each move.

    gtp_moves = []
    for i in range(len(moves)):
        if moves[i] != None:
            x, y = point_to_coord(moves[i], board.size)
            gtp_moves.append((format_point((x, y)), round(float(count[i])/float(numSimulations),3)))
        #else:
        #    gtp_moves.append(('Pass',float(count[i])/float(numSimulations)))
    #sys.stderr.write("win rates: {}\n"
    #                 .format(sorted(gtp_moves, key = byPercentage,
    #                                reverse = True)))
    sorted(gtp_moves, key = byPercentage, reverse = True)
    coord = []
    prob = []
    #output = []
    for pair in gtp_moves:
        coord.append(pair[0])
        prob.append(pair[1])
    return coord + prob


#sys.stderr.flush()


def select_best_move(board, moves, moveWins):
    """
    Move select after the search.
    """
    max_child = np.argmax(moveWins)
    return moves[max_child]
    
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
                                check_selfatari = False)       #implement a way to change this accordingly

def simulateMove(board, move, toplay, sim_num):
    """
    Run simulations for a given move.
    """
    wins = 0
    for _ in range(sim_num):
        result = simulate(board, move, toplay)
        if result == toplay:
            wins += 1
    return wins

def get_move(board, color, selection_policy, sim_num):
    """
    Run one-ply MC simulations to get a move to play.
    """
    #cboard = board.copy()
    emptyPoints = board.get_empty_points()
    moves = []
    for p in emptyPoints:
        if board.is_legal(p, color):
            moves.append(p)
    if not moves:
        return None
    moves.append(None)
    if selection_policy == "ucb":
        C = 0.4 #sqrt(2) is safe, this is more aggressive
        best = runUcb(board, C, moves, color, sim_num)
        return best
    else:
        moveWins = []
        for move in moves:
            wins = simulateMove(board, move, color, sim_num)
            moveWins.append(wins)
        return writeMoves(board, moves, moveWins, sim_num)
        #return moveWins
        #return select_best_move(board, moves, moveWins)

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

"""
def run(sim, move_select, sim_rule, move_filter):
    #Start the gtp connection and wait for commands.
    board = SimpleGoBoard(7)
    con = GtpConnectionGo3(Go3(sim, move_select, sim_rule, move_filter), board)
    con.start_connection()

def parse_args():
    #Parse the arguments of the program.
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--sim', type=int, default=10, help='number of simulations per move, so total playouts=sim*legal_moves')
    parser.add_argument('--moveselect', type=str, default='simple', help='type of move selection: simple or ucb')
    parser.add_argument('--simrule', type=str, default='random', help='type of simulation policy: random or rulebased')
    parser.add_argument('--movefilter', action='store_true', default=False, help='whether use move filter or not')

    args = parser.parse_args()
    sim = args.sim
    move_select = args.moveselect
    sim_rule = args.simrule
    move_filter = args.movefilter

    if move_select != "simple" and move_select != "ucb":
        print('moveselect must be simple or ucb')
        sys.exit(0)
    if sim_rule != "random" and sim_rule != "rulebased":
        print('simrule must be random or rulebased')
        sys.exit(0)

    return sim, move_select, sim_rule, move_filter

if __name__=='__main__':
    sim, move_select, sim_rule, move_filter = parse_args()
    run(sim, move_select, sim_rule, move_filter)
"""
