import random


class GeneticService:
    __population = []
    __population_size = 0
    __features_size = 0
    __feature_min = 0
    __feature_max = 0
    __mutation_chance = 0 ## mutation chance in %
    __reproduction_chance = 0 ## crossing-over chance in %

    def get_population_size(self):
        return self.__population_size
        
    def get_features_size(self):
        return self.__features_size

    def __generate_random_population(self, population_size, features_size, feature_max, feature_min):
        return [[random.randrange(feature_min, feature_max + 1) for i in range(features_size)]
                for j in range(population_size)]

    def __init__(self, population_size, features_size, feature_max, feature_min, reproduction_chance, mutation_chance):
        if mutation_chance < 0 or mutation_chance > 100:
            raise ValueError("Given mutation chance is invalid")

        self.__features_size = features_size
        self.__feature_max = feature_max
        self.__feature_min = feature_min
        self.__mutation_chance = mutation_chance
        self.__reproduction_chance = reproduction_chance
        self.__population_size = population_size
        self.__population = self.__generate_random_population(population_size, features_size, feature_max, feature_min)

    def get_current_population(self):
        return [tuple(chromosome) for chromosome in self.__population]

    def get_next_population(self, results): # tu musi być argument z tournamentów

        #print("Wyniki turnieju:")  # Usunać
        if (len(results) == 0): results = self.__get_random_tournament_results(10)
        #print(results)  # Usunąć

        #print("Populacja po ruletce:")  # Usunać
        self.__reduce_population_with_roulette(results)
        #print(self.get_current_population()) #Usunac

        #print("Populacja po mutacji:") # Usunać
        self.__mutate_population()
        #print(self.get_current_population()) #Usunac

        #print("Populacja po crossing-over:") #Usunąć
        self.__reproduce_population()
        #print(self.get_current_population()) #Usunąć

        return self.get_current_population()


    # Ruletka:
    def __reduce_population_with_roulette(self, results):
        score_sum = sum(results)
        roulette_fixed_point = random.randrange(0, score_sum)

        #stwórz tuple (index, wynik), aby można było posortować osobniki po wynikach
        tmp = [(i, results[i]) for i in range(len(results))]
        tuples = [tuple(x) for x in tmp]
        sorted_tuples = sorted(tuples, key=lambda tup: tup[1], reverse=True)

        new_population = []

        for x in range(self.__population_size): #chcemy po prostu żeby wykonało się population_size razy
            partial_sum = 0

            for i in range(len(sorted_tuples)):
                partial_sum += (sorted_tuples[i][1])
                if partial_sum > roulette_fixed_point:
                    index = sorted_tuples[i][0]
                    new_population += [self.__population[index]]
                    roulette_fixed_point -= sorted_tuples[i][1]
                    sorted_tuples.remove(sorted_tuples[i])
                    break


        self.__population = new_population
        self.__population_size=len(new_population)



    # Mutacja:
    def __mutate_population(self):
        mutation_indexes = self.__choose_chromosomes_by_chance(self.__mutation_chance)

        for i in mutation_indexes:
            self.__population[i] = self.__mutate_chromosome(self.__population[i])

    def __mutate_chromosome(self, chromosome):
        mutation_place_index = random.randrange(0, len(chromosome))
        chromosome[mutation_place_index] = random.randrange(self.__feature_min, self.__feature_max + 1)
        return chromosome

   # Crossing-over:

    def __reproduce_population(self):
        reproduction_indexes = self.__choose_chromosomes_by_chance(self.__reproduction_chance)
        pairs_number = int(len(reproduction_indexes) / 2)
        #TU SPRAWDZ CO SIE DZIEJE 
        pairs_indexes = [random.sample(reproduction_indexes, 2) for i in range(pairs_number)]

        for pair_index in pairs_indexes:
            kids = self.__crossing_over(pair_index)
            self.__add_kids_to_population(kids)


    def __crossing_over(self, pair_indexes):
        crossing_over_point = random.randrange(1, self.__features_size)
        print(pair_indexes)
        print(self.__population)
        print(self.__population_size)
        parent_1 = self.__population[pair_indexes[0]]
        parent_2 = self.__population[pair_indexes[1]]

        kid_1 = parent_1[0:crossing_over_point] + parent_2[crossing_over_point:]
        kid_2 = parent_2[0:crossing_over_point] + parent_1[crossing_over_point:]

        return [kid_1, kid_2]

    def __add_kids_to_population(self, kids):
        self.__population += kids


    def __choose_chromosomes_by_chance(self, chance):
        chromosomes_count = 0
        for i in range(self.__population_size):
            p = random.randrange(0, 100)
            if p < chance:
                chromosomes_count += 1
        return random.sample(range(0, self.__population_size), chromosomes_count)


    #Random tournament:

    def __get_random_tournament_results(self, draw_chance):
        win_chance = (100-draw_chance)/2
        tournament_results = [0 for i in range(self.__population_size)]

        for i in range(self.__population_size):
            for j in range(self.__population_size):
                if j>=i : break

                p = random.randrange(0, 100)
                if p<=win_chance:
                    tournament_results[i] += 3      #i-ty wygrał
                elif p <= draw_chance + win_chance:
                    tournament_results[i] += 1      #remis
                    tournament_results[j] += 1
                else:
                    tournament_results[j] += 3      #j-ty wygrał
        return tournament_results




#serwis = GeneticService(5, 4, 20, 1, 50, 5)

#print("Nowa losowa populacja:\n")
#print(serwis.get_current_population())

#results = []

#print(serwis.get_next_population(results))
#print(serwis.get_next_population(results))





