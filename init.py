from moves_counter import make_move
from genetic_service import GeneticService
import numpy as np
from itertools import combinations
from time import time

def play(osobnik1, osobnik2, index1, index2):
    board=np.zeros((9,9))
    while(True):
        x,y= make_move(board,osobnik1,1)
        if(y):
            return index1
        a,b=make_move(board, osobnik2,-1)
        if(b):
            return index2
        if not x and not a:
            return -1, 

def warunek_stopu(current_pop, epsilon):
    return epsilon<np.std(np.array(current_pop))


def get_the_best_person(population):
    results=[0]*len(population)
    for pair in list(combinations(range(len(population)),2)):
        index=play(population[pair[0]],population[pair[1]],pair[0],pair[1])
        if(index==-1):
            results[pair[0]]+=1
            results[pair[1]]+=1
        else:
            results[index]+=3
    
    return population[results.index(max(results))]
        


def train(serwis):
    population = serwis.get_current_population()
    while(warunek_stopu(population,2)):
        results=[0]*serwis.get_population_size()
        for pair in list(combinations(range(serwis.get_population_size()),2)):
            index=play(population[pair[0]],population[pair[1]],pair[0],pair[1])
            if(index==-1):
                results[pair[0]]+=1
                results[pair[1]]+=1
            else:
                results[index]+=3
        population=serwis.get_next_population(results)
    
    return population

def main():
    start_time=time()
    serwis = GeneticService(5, 8, 20, 1, 50, 5)
    best_population=train(serwis)
    best_person=get_the_best_person(best_population)
    print(best_person)
    print(round(start_time-time(),4))
    
if __name__=='__main__':
    main()
