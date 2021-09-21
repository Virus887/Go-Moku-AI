from ctypes import c_bool
import numpy as np
import random
import multiprocessing as mp

# zoptymalizowac dopisac o blokowaniu
# zwraca --> (max_sum,has_five, block_four)
#               k_pion  k_poziom
# pionowo        1       0
# poziomo        0       1
# skos dół prawo 1       1
# skos dół lewo  1      -1
# sprawdzic czy typowanie statyczne dobrze dziala
# można łatwo zmienić rozmiar planszy dodając parametr do funkcji i zmieniając 9 i 8
def make_move(board: np.array, chromosome, player_sign: int):
    pos_i, pos_j, won = count_all(board, chromosome, player_sign)
    if pos_i == -1 and pos_j == -1:
        return False, won
    board[pos_i, pos_j] = player_sign
    return True, won

def check_board(board,i,j,chromosome, player_sign, block_four, max_sum, pos_i,pos_j):
    if board[i][j] == 0:
        this_sum, my_five, enemy_four = count_move(np.array(board), chromosome, i, j, player_sign)
        if my_five:
            return i, j,True
        if block_four:
            return
        elif enemy_four:
            pos_i = i
            pos_j = j
            block_four = True
        elif this_sum > max_sum:
            pos_i = i
            pos_j = j
            max_sum = this_sum


def count_all(board: np.array, chromosome, player_sign: int):
    best_pos_i=mp.Value('i',-1)
    best_pos_j=mp.Value('i',-1)
    block_four = mp.Value(c_bool, False)
    mpBoard=mp.Array('i', board.tolist())
    max_sum = -1
    max_count = 0
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                this_sum, my_five, enemy_four = count_move(board, chromosome, i, j, player_sign)
                if my_five:
                    return i, j,True
                if block_four:
                    continue
                elif enemy_four:
                    best_pos_i = i
                    best_pos_j = j
                    block_four = True
                elif this_sum > max_sum:
                    best_pos_i = i
                    best_pos_j = j
                    max_sum = this_sum
                    max_count = 0
                elif this_sum == max_sum:
                    max_count += 1
                    if random.randrange(0, max_count) == 0:
                        best_pos_i = i
                        best_pos_j = j
                        max_sum = this_sum


    return best_pos_i, best_pos_j, False


def count_move(board: np.array, chromosome, pos_i: int, pos_j: int, player_sign: int):
    this_sum = 0
    enemy_four = False
    my_five = False
    results = [(0, False, False) for i in range(4)]

    results[0] = count_move_in_direction(board, chromosome, pos_i, pos_j, player_sign, 1, 0)
    results[1] = count_move_in_direction(board, chromosome, pos_i, pos_j, player_sign, 0, 1)
    results[2] = count_move_in_direction(board, chromosome, pos_i, pos_j, player_sign, 1, 1)
    results[3] = count_move_in_direction(board, chromosome, pos_i, pos_j, player_sign, 1, -1)

    for pos in results:
        this_sum += pos[0]
        if pos[1]:
            my_five = True
            break
        if pos[2]:
            enemy_four = True
    return this_sum, my_five, enemy_four


def count_move_in_direction(board: np.array, chromosome, pos_i: int, pos_j: int, player_sign: int, k_pion: int, k_poziom: int):
    best_move = 0
    for i in range(-4, 1):
        # w zakresie
        enemy_four = False
        my_sum = 0
        enemy_sum = 0
        consistent = True
        block = False
        left_most = False
        right_most = False
        closure = 0
        pos_start_pion = pos_i + k_pion * i
        pos_end_pion = pos_start_pion + k_pion * 4
        pos_start_poziom = pos_j + k_poziom * i
        pos_end_poziom = pos_start_poziom + k_poziom * 4
        #if pos_start_pion >= 0 and pos_end_pion < 9 and pos_start_poziom >= 0 and pos_end_poziom < 9:
        if pos_start_pion >= 0 and pos_start_pion<9 and pos_end_pion < 9 and pos_end_pion>=0 and pos_start_poziom >= 0 and pos_start_poziom<9 and pos_end_poziom < 9 and pos_end_poziom>=0:
            # counting
            # tworzenie slice
            current_slice = []
            for k in range(0, 5):
                #print((pos_start_pion + k_pion * k, pos_start_poziom + k_poziom * k))
                current_slice.append(board[pos_start_pion + k_pion * k, pos_start_poziom + k_poziom * k])
            # należy sprawdzic
            current_slice[-i] = player_sign

            my_sum, enemy_sum = count_sums(current_slice, player_sign)

            # consistentcy
            if enemy_sum == 0:  # jeżeli w piątce nie znajduje się przeciwnik
                consistent = count_consistent(current_slice[1:-1])

            # left_most i right_most
            if current_slice[0] == player_sign:
                left_most = True
            if current_slice[4] == player_sign:
                right_most = True

            # closure i block - jesli funkcja to trzeba przekazac całego board i pos
            if pos_start_pion == 0 or pos_start_poziom == 0 or (pos_start_poziom==8 and k_poziom==-1) or (pos_start_pion==8 and k_pion==-1):  # lewy kraniec
                closure += 1
                if left_most:
                    block = True
            # jeżeli to nie lewy kraniec to czy z lewej storny jest przeciwnik

            elif board[pos_start_pion - k_pion * 1][pos_start_poziom - k_poziom * 1] == -player_sign:
                closure += 1
                if left_most:
                    block = True

            if pos_end_pion == 8 or pos_end_poziom == 8 or (pos_start_poziom==0 and k_poziom==-1) or (pos_start_pion==0 and k_pion==-1):  # prawy kraniec
                closure += 1
                if right_most:
                    block = True
            # jeżeli to nie prawy kraniec to czy z prawej storny jest przeciwnik
            elif board[pos_end_pion + k_pion * 1][pos_end_poziom + k_poziom * 1] == -player_sign:
                closure += 1
                if right_most:
                    block = True

            # funkcja zależna od my_sum, consisnte, block i clousre i returnuje best_move
            # zwraca piatke i wygrywamy
        if my_sum == 5:
            return (1000, True, enemy_four)
        if enemy_sum == 0:
            possible_best = count_my_best(my_sum, consistent, block, closure, chromosome)
            if possible_best > best_move:
                best_move = possible_best
        elif my_sum == 1:
            # dla przeciwnika
            closure = 0  # closure dla przeciwnika
            if pos_start_pion == 0 or pos_start_poziom == 0 or (pos_start_poziom==8 and k_poziom==-1) or (pos_start_pion==8 and k_pion==-1):  # lewy kraniec
                closure += 1
            # jeżeli to nie lewy kraniec to czy z lewej storny jest przeciwnik
            elif board[pos_start_pion - k_pion * 1][pos_start_poziom - k_poziom * 1] == -player_sign:
                closure += 1
            if pos_end_pion == 8 or pos_end_poziom == 8 or (pos_start_poziom==0 and k_poziom==-1) or (pos_start_pion==0 and k_pion==-1):  # prawy kraniec
                closure += 1
            # jeżeli to nie prawy kraniec to czy z prawej storny jest przeciwnik
            elif board[pos_end_pion + k_pion * 1][pos_end_poziom + k_poziom * 1] == -player_sign:
                closure += 1

            # czwórka przeciwnika
            if enemy_sum == 4:
                enemy_four = True
            # trojki przeciwnika
            elif enemy_sum == 3:
                possible_best = count_my_best_enemy(closure, chromosome)
                if possible_best > best_move:
                    best_move = possible_best

    return best_move, False, enemy_four


def count_sums(current_slice, player_sign):
    my_sum = 0
    enemy_sum = 0
    for k in range(0, 5):  # zliczenie ilości pionków gracza i przeciwnika
        if current_slice[k] == player_sign:
            my_sum += 1
        if current_slice[k] == -player_sign:  # pole przeciwnika
            enemy_sum += 1
    return (my_sum, enemy_sum)


def count_consistent(slice):
    for pos in slice:
        if pos == 0:
            return False
    return True


def count_my_best_enemy(closure, chromosome):
    best_move = 0
    if closure == 0:
        if chromosome[4] > best_move:
            best_move = chromosome[4]
            # jednostronnie otwarta trojka
    if closure == 1:
        if chromosome[5] > best_move:
            best_move = chromosome[5]
            # dwustronnie zamknieta trojka
    if closure == 2:
        if chromosome[6] > best_move:
            best_move = chromosome[6]
    return best_move


def count_my_best(my_sum, consistent, block, closure, chromosome):
    best_move = 0
    # nieblokowalna spojna czwórka
    if my_sum == 4 and consistent and not block and closure != 2:  # ten not block to troche taki closure -1
        if chromosome[0] > best_move:
            best_move = chromosome[0]
    # blokowalna spójna czwórka
    if my_sum == 4 and consistent and block:
        if chromosome[0] > best_move:
            best_move = chromosome[0]
    # otwarta niespójna czwórka
    if my_sum == 4 and not consistent and closure == 0:
        if chromosome[1] > best_move:
            best_move = chromosome[1]
            # jednostronnie otwarta niespójna czwórka
    if my_sum == 4 and closure == 1:
        if chromosome[2] > best_move:
            best_move = chromosome[2]
            # zamknieta czwórka
    if my_sum == 4 and closure == 2:
        if chromosome[3] > best_move:
            best_move = chromosome[3]
            # dwustronnie otwarta trójka
    if my_sum == 3 and closure == 0:
        if chromosome[4] > best_move:
            best_move = chromosome[4]
            # jednostronnie otwarta trojka
    if my_sum == 3 and closure == 1:
        if chromosome[5] > best_move:
            best_move = chromosome[5]
            # dwustronnie zamknieta trojka
    if my_sum == 3 and closure == 2:
        if chromosome[6] > best_move:
            best_move = chromosome[6]
    if my_sum == 2:
        if chromosome[7] > best_move:
            best_move = chromosome[7]
    return best_move
