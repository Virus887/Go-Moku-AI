from moves_counter import make_move
from genetic_service import GeneticService
import numpy as np
from itertools import combinations
from time import time
import multiprocessing as mp

def play(osobnik1, osobnik2, index1, index2,results):
    board=np.zeros((9,9))
    while(True):
        x,y= make_move(board,osobnik1,1)
        if(y):
            results[index1]+=3
            break
        a,b=make_move(board, osobnik2,-1)
        if(b):
            results[index2]+=3
            break
        if not x and not a:
            results[index1]+=1
            results[index2]+=1
            break


def warunek_stopu(current_pop, epsilon):
    return epsilon<np.std(np.array(current_pop))

def getPaires(populationLength):
    return list(combinations(range(populationLength),2))

def get_the_best_person(population):
    results=[0]*len(population)
    for pair in list(combinations(range(len(population)),2)):
        play(population[pair[0]],population[pair[1]],pair[0],pair[1],results)
    
    return population[results.index(max(results))]
        


def train(serwis):
    population = serwis.get_current_population()

    while(warunek_stopu(population,2)):
        results=mp.Array('i', serwis.get_population_size())
        processes=[]
        for pair in list(combinations(range(serwis.get_population_size()),2)):
            processes.append(mp.Process(target=play, args=(population[pair[0]],population[pair[1]],pair[0],pair[1],results)))

        for process in processes:
            process.start()
        for process in processes:
            process.join()
        

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
