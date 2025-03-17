"""
This code is consistent with the revised verison of the course, which went live 3-11-2025.  With these 2 files 
(main.py and cat_trap_algorithms.py), I was able to find success.  With my original 3 files (CatTrap.py, CatGame.py, hexutil.py),
I was unable to run the game, so I spoke with Eduardo Corpeno via email.  He advised that I may have success running the game
by using this revised version, which included GitHub Codespaces.  


"""

import random
import copy
import time
import numpy as np

CAT_TILE = 6
BLOCKED_TILE = 1
EMPTY_TILE = 0
LAST_CALL_MS = 0.5
VERBOSE = True
TIMEOUT = [-1, -1]

class CatTrapGame:
    size = 0
    start_time = time.time()
    deadline = time.time()
    terminated = False
    max_depth = float('inf')
    reached_max_depth = False
    
    def __init__(self, size):
        self.cat = [size // 2] * 2
        self.hexgrid = np.full((size, size), EMPTY_TILE)
        self.hexgrid[tuple(self.cat)] = CAT_TILE
        CatTrapGame.size = size

    def initialize_random_hexgrid(self):
        tiles = CatTrapGame.size ** 2
        num_blocks = random.randint(round(0.067 * tiles), round(0.13 * tiles))
        count = 0
        self.hexgrid[tuple(self.cat)] = CAT_TILE

        while count < num_blocks:
            r = random.randint(0, CatTrapGame.size - 1)
            c = random.randint(0, CatTrapGame.size - 1)
            if self.hexgrid[r, c] == EMPTY_TILE:
                self.hexgrid[r, c] = BLOCKED_TILE
                count += 1    
        if VERBOSE:
            print('\n======= NEW GAME =======')
            self.print_hexgrid()

    def set_hexgrid(self, hexgrid):
        self.hexgrid = hexgrid
        self.cat = list(np.argwhere(self.hexgrid == CAT_TILE)[0])  
        if VERBOSE:
            print('\n======= NEW GAME =======')
            self.print_hexgrid()
   
    def block_tile(self, coord):
        self.hexgrid[tuple(coord)] = BLOCKED_TILE

    def unblock_tile(self, coord):
        self.hexgrid[tuple(coord)] = EMPTY_TILE

    def place_cat(self, coord):
        self.hexgrid[tuple(coord)] = CAT_TILE
        self.cat = coord

    def move_cat(self, coord):
        self.hexgrid[tuple(self.cat)] = EMPTY_TILE  
        self.place_cat(coord)
    
    def get_cat_moves(self):
        hexgrid = self.hexgrid
        r, c = self.cat
        n = CatTrapGame.size
        col_offset = r % 2  
        moves = []

        directions = {
            'E': (0, 1),
            'W': (0, -1),
            'NE': (-1, col_offset),
            'NW': (-1, -1 + col_offset),
            'SE': (1, col_offset),
            'SW': (1, -1 + col_offset),
        }

        for dr, dc in directions.values():
            tr, tc = r + dr, c + dc  
            if 0 <= tr < n and 0 <= tc < n and hexgrid[tr, tc] == EMPTY_TILE:
                moves.append([tr, tc])

        return moves

    def apply_move(self, move, cat_turn):
        if self.hexgrid[tuple(move)] != EMPTY_TILE:
            action_str = "move cat to" if cat_turn else "block"
            self.print_hexgrid()
            print('\n=====================================')
            print(f'Attempting to {action_str} {move} = {self.hexgrid[tuple(move)]}')
            print('Invalid Move! Check your code.')
            print('=====================================\n')

        if cat_turn:
            self.move_cat(move)
        else:
            self.hexgrid[tuple(move)] = BLOCKED_TILE

    def time_left(self):
        return (CatTrapGame.deadline - time.time()) * 1000
    
    def print_hexgrid(self):
        tile_map = {
            EMPTY_TILE: ' ⬡',  
            BLOCKED_TILE: ' ⬢', 
            CAT_TILE: '🐈'    
        }
        for r in range(CatTrapGame.size):
            prefix = ' ' if r % 2 != 0 else ''
            row_display = ' '.join(tile_map[cell] for cell in self.hexgrid[r])
            print(prefix + row_display)
        return

    def evaluation(self, cat_turn):
        evaluation_function = 'custom'

        if evaluation_function == 'moves':
            return self.eval_moves(cat_turn)
        elif evaluation_function == 'straight_exit':
            return self.eval_straight_exit(cat_turn)
        elif evaluation_function == 'custom':
            return self.eval_custom(cat_turn)
        return 0

    def eval_moves(self, cat_turn):
        cat_moves = self.get_cat_moves()
        return len(cat_moves) if cat_turn else len(cat_moves) - 1

    def get_target_position(self, scout, direction):
        r, c = scout
        col_offset = r % 2  
        
        if direction == 'E':
            return [r, c + 1]
        elif direction == 'W':
            return [r, c - 1]
        elif direction == 'NE':
            return [r - 1, c + col_offset]
        elif direction == 'NW':
            return [r - 1, c - 1 + col_offset]
        elif direction == 'SE':
            return [r + 1, c + col_offset]
        elif direction == 'SW':
            return [r + 1, c - 1 + col_offset]
        return [r, c]
    def eval_straight_exit(self, cat_turn):
        distances = []
        directions =  ['E', 'W', 'NE', 'NW', 'SE', 'SW']
        n = CatTrapGame.size
        for dir in directions:
            distance = 0
            r, c = self.cat
            while not (r < 0 or r >= n or c < 0 or c >= n):
                if self.hexgrid[r, c] == BLOCKED_TILE:
                    distance += n 
                    break
                distance += 1
                r, c = self.get_target_position([r, c], dir)
            distances.append(distance)

        distances.sort() 
        return CatTrapGame.size - (distances[0] if cat_turn else distances[1])

    def eval_custom(self, cat_turn):
        n = CatTrapGame.size
        move_score = self.eval_moves(cat_turn) / 6.0  
        proximity_score = self.eval_straight_exit(cat_turn) / n

        center_row, center_col = n // 2, n // 2
        cat_row, cat_col = self.cat
        distance = ((cat_row - center_row) ** 2 + (cat_col - center_col) ** 2) ** 0.5

        max_penalty = n * 0.75
        penalty = max_penalty - distance
        penalty = penalty / max_penalty # Normalize
        if not cat_turn:
            penalty += 0.2 

        score = 0.2 * move_score + proximity_score - 0.5 * penalty
        return score

    def select_cat_move(self, random_cat, minimax, alpha_beta, depth_limited,
                        max_depth, iterative_deepening, allotted_time):
        CatTrapGame.start_time = time.time()
        CatTrapGame.deadline = CatTrapGame.start_time + allotted_time
        CatTrapGame.terminated = False
        CatTrapGame.max_depth = float('inf') 
        CatTrapGame.reached_max_depth = False 
        move = self.cat

        if VERBOSE:
            print('\n======= NEW MOVE =======')

        if random_cat:
            move = self.random_cat_move() 
        elif minimax:
            # Select a move using the Minimax algorithm.
            move = self.alpha_beta() if alpha_beta else self.minimax()   
        elif depth_limited:
            # Select a move using Depth-Limited Search.
            CatTrapGame.max_depth = max_depth
            move = self.alpha_beta() if alpha_beta else self.minimax()
        elif iterative_deepening:
            # Select a move using the Iterative Deepening algorithm.
            move = self.iterative_deepening(alpha_beta)

        elapsed_time = (time.time() - CatTrapGame.start_time) * 1000
        if VERBOSE:
            print(f'Elapsed time: {elapsed_time:.3f}ms ')
            print(f'New cat coordinates: {move}')
            temp = copy.deepcopy(self)
            if move != TIMEOUT:
                temp.move_cat(move)
            temp.print_hexgrid()
        return move

    def random_cat_move(self):
        moves = self.get_cat_moves()
        if moves:
            return random.choice(moves)
        return self.cat

    def max_value(self, depth):
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return TIMEOUT, 0
        
        legal_moves = self.get_cat_moves() 
        if not legal_moves:
            max_turns = 2 * (CatTrapGame.size ** 2)
            utility = (max_turns - depth) * (-500) 
            return self.cat, utility
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.cat, self.evaluation(cat_turn = True)
        
        best_value = float('-inf')
        best_move = legal_moves[0]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = True)
            value = next_game.min_value(depth + 1)

            if CatTrapGame.terminated:
                return TIMEOUT, 0

            if value > best_value:
                best_value = value
                best_move = move
  
        return best_move, best_value

    def min_value(self, depth):
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return 0

        r, c = self.cat
        n = CatTrapGame.size
        if (
            r == 0 or r == n - 1 or 
            c == 0 or c == n - 1
        ):
            max_turns = 2 * (CatTrapGame.size ** 2)
            return (max_turns - depth) * (500) 
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.evaluation(cat_turn = False)
        
        best_value = float('inf')

        legal_moves = [list(rc) for rc in np.argwhere(self.hexgrid == EMPTY_TILE)]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = False)
            _, value = next_game.max_value(depth + 1)

            if CatTrapGame.terminated:
                return 0
            
            best_value = min(best_value, value)

        return best_value

    def minimax(self):
        best_move, _ = self.max_value(depth = 0) 
        return best_move

    def alpha_beta_max_value(self, alpha, beta, depth):
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return TIMEOUT, 0
        
        legal_moves = self.get_cat_moves() 
        if not legal_moves:
            max_turns = 2 * (CatTrapGame.size ** 2)
            utility = (max_turns - depth) * (-500) 
            return self.cat, utility
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.cat, self.evaluation(cat_turn = True)
        
        best_value = float('-inf')
        best_move = legal_moves[0]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = True)
            value = next_game.alpha_beta_min_value(alpha, beta, depth + 1)

            if CatTrapGame.terminated:
                return TIMEOUT, 0

            if value > best_value:
                best_value = value
                best_move = move

            if best_value >= beta: 
                return best_move, best_value
            alpha = max(alpha, best_value)

        return best_move, best_value

    def alpha_beta_min_value(self, alpha, beta, depth):
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return 0

        r, c = self.cat
        n = CatTrapGame.size
        if (
            r == 0 or r == n - 1 or 
            c == 0 or c == n - 1
        ):
            max_turns = 2 * (CatTrapGame.size ** 2)
            return (max_turns - depth) * (500) 
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.evaluation(cat_turn = False)
        
        best_value = float('inf')

        legal_moves = [list(rc) for rc in np.argwhere(self.hexgrid == EMPTY_TILE)]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = False)
            _, value = next_game.alpha_beta_max_value(alpha, beta, depth + 1)

            if CatTrapGame.terminated:
                return 0
            
            best_value = min(best_value, value)

            if best_value <= alpha: 
                return best_value
            beta = min(beta, best_value)

        return best_value

    def alpha_beta(self):
        alpha = float('-inf')
        beta = float('inf')
        best_move, _ = self.alpha_beta_max_value(alpha, beta, depth = 0)
        return best_move

    def iterative_deepening(self, alpha_beta):
        best_depth = 0
        output_move = TIMEOUT
        
        max_turns = 2 * (CatTrapGame.size ** 2)
        for depth in range(1, max_turns):
            CatTrapGame.reached_max_depth = False
            CatTrapGame.max_depth = depth
            best_move = self.alpha_beta() if alpha_beta else self.minimax()   
            
            if CatTrapGame.terminated:
                break
            else:
                output_move = best_move
                best_depth = depth
                elapsed_time = (time.time() - CatTrapGame.start_time) * 1000
                if VERBOSE:
                    print(f'Done with a tree of depth {depth} '
                          f'after {elapsed_time:.3f}ms')

                if not CatTrapGame.reached_max_depth:
                    break

        if VERBOSE:
            print(f'Depth reached: {best_depth}')
        return output_move

if __name__ == '__main__':
    signs = '⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️'
    print(f'\n{signs} {signs}')
    print('               WARNING')
    print('You ran cat_trap_algorithms.py')
    print('This file contains the AI algorithms')
    print('and classes for the intelligent cat.')
    print('Did you mean to run main.py?')
    print(f'{signs} {signs}\n')
