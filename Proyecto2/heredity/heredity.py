import csv
import itertools
import sys

THE_PAPUS = {
    'Harry': {
        'name': 'Harry', 
        'mother': 'Lily', 
        'father': 'James', 
        'trait': None
    },

    'James': {
        'name': 'James', 
        'mother': None, 
        'father': None, 
        'trait': True
    },

    'Lily': {
        'name': 'Lily', 
        'mother': None, 
        'father': None, 
        'trait': False
    }
}


PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def not_have_a_parent(data_set, name):
    """Metodo auxiliar que verifica si una persona tiene padres en el data_Set"""
    return data_set[name]['father'] is None and data_set[name]['mother'] is None

def get_gen_father(parent, one_gen, two_gene):
    """
    Esa mutacion consta de acuerdo a la cantidad de copias del gen
        * Si tiene 2 copias del gen entoces 100% le pasara los genes asi que el calculo es: `1-PROB['mutation]`
        * Si tiene 1 copias del gen entoces 50% le pasará los genes asi que el calculo es `0.5-PROB[mutation]`
        * Si tiene 0 copias del gen le pasara directamente la probabilidad de `PROB['mutation]`
    En caso de que haya un papa con 0 y otro con 1 o 2  se pueden agregar juntos
    """
    from_two_copy = 1   - PROBS['mutation']
    from_one_copy = 0.5 - PROBS['mutation']

    if parent in one_gen:
        #Probabilidad de tener el gen, dada la copia del gen
        return from_one_copy

    if parent in two_gene:
        #La probabilidad de tener 2 copias del gen
        return from_two_copy
    #Si el padre no esta en el set de un gen ni el del 2 gen entoces se regresa solo la mutacion
    return PROBS['mutation'] 
    

def calculate_set_one_gene(people, one_gene, two_gene, have_trait):
    """
    Metodo que calcula todas las probabilidades del set de personas que tengan un gen
    """
    #El extra es la variable cuando un padre no tiene copias, "No estoy seguro si eso correcto"
    trait    = 1
    extra    = 1
    proba    = 0
    the_ones = {} #Toda el set de probabilidades seran guardads en un diccionario, correspondientes a la copia del solo gen

    for member in one_gene:
        if not_have_a_parent(people, member): #Si no tiene padres
            proba = PROBS['gene'][1] #Obtenemos la probabilidad del gen
            #¿Aqui? debemos calcular junto con su trait??, en caso debemos verificar si esta en el trait
        else:
            #Primero hay que conseguir a sus padres
            father = people[member]['father']
            mother = people[member]['mother']
           
            #Segundo, Obtenemos las probabilidades en base a sus genes todos tienen una probabilidad de que mute con 0.01
           
            father_gen = get_gen_father(father, one_gene, two_gene)
            mother_gen = get_gen_father(mother, one_gene, two_gene) 

            #Tercero Juntamos las probabilidades
            if father_gen == PROBS['mutation']:
                extra = (PROBS['mutation'], mother_gen)
            if mother_gen == PROBS['mutation']:
                extra = (PROBS['mutation'],  father_gen)
            
            proba = (father_gen * extra[1] + extra[0] * mother_gen)
        
        if member in have_trait:
            trait = PROBS['trait'][1][people[member]['trait']]    
        
        the_ones.update({member: proba*trait})
    
    return the_ones
        

def calculate_set_two_genes(people, one_gene, two_genes, have_trait):
    """
    Metodo homologo al one gene calcula todas las probabilidades del 
    set de personas que se encuentran en el set de las copias de 2 perosnas
    """
    the_twos = {}
    extra = 1
    proba = 0
    trait = 1

    for member in two_genes:
        if not_have_a_parent(people, member):
            proba = PROBS['gene'][2]
        else:
            #Primero hay que conseguir a sus padres
            father = people[member]['father']
            mother = people[member]['mother']
           
            #Segundo, Obtenemos las probabilidades en base a sus genes todos tienen una probabilidad de que mute con 0.01
           
            father_gen = get_gen_father(father, one_gene, two_genes)
            mother_gen = get_gen_father(mother, one_gene, two_genes) 

            #Tercero Juntamos las probabilidades
            if father_gen == PROBS['mutation']:
                extra = PROBS['mutation'] + mother_gen
            if mother_gen == PROBS['mutation']:
                extra = PROBS['mutation'] + father_gen
            
            #proba = (father_gen * mother_gen) * (extra)
            proba = (father_gen * extra[1] + extra[0] * mother_gen)
        
        if member in have_trait:
            trait = PROBS['trait'][2][people[member]['trait']]
             
        the_twos.update({member: proba*trait})
    
    return the_twos

def calculate_set_no_genes(people, one_gene, two_genes, no_gen_people):
    """
    Metodo que calcula todas las personas que no tienen gen copia ni traits
    """
    the_nones = {}
    
    for member in no_gen_people:
        if not_have_a_parent(people, member):
            proba = PROBS['gene'][0]
        else:
            #Primero hay que conseguir a sus padres
            father = people[member]['father']
            mother = people[member]['mother']
           
            #Segundo, Obtenemos las probabilidades en base a sus genes todos tienen una probabilidad de que mute con 0.01
           
            father_gen = get_gen_father(father, one_gene, two_genes)
            mother_gen = get_gen_father(mother, one_gene, two_genes) 

            #Tercero Juntamos las probabilidades
            if father_gen == PROBS['mutation']:
                extra = PROBS['mutation'] + mother_gen
            if mother_gen == PROBS['mutation']:
                extra = PROBS['mutation'] + father_gen
            
            proba = (father_gen * extra[1] + extra[0] * mother_gen)
        trait = PROBS['trait'][0][people[member]['trait']]

        the_nones.update({member: proba*trait})
        

    return the_nones

def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    
    El trait es otro set al que debemos de calcularle, considerando como en have_trait, todo el set
    de personas a la cual le queremos calcular el si tienen trait o no  como si fuera un set de la copia o no
    """
    name_peoples = list(people.keys())
    
    """
    Estos metodos no contemplan a las personas que tienen  0 copias del gen, ni las que 
    no tienen trair incluso adentro de las funciones
    Asi que vamos a filtrar por aquellos que no tienen copias ni trait
    """

    no_genes = [] #[person for person in people if person not in [one_gene, two_genes, have_trait]]
    for person in name_peoples:
        if person not in one_gene and person not in two_genes and person not in have_trait:
            no_genes.append(person)
    #Por cada persona que no tiene copias del gen ni trair
    


    probabily_non_gen = calculate_set_no_genes(people, one_gene, two_genes, no_genes)
    probabily_one_gen = calculate_set_one_gene(people, one_gene, two_genes, have_trait)
    probabily_two_gen = calculate_set_two_genes(people, one_gene, two_genes, have_trait)
    print(probabily_non_gen)
    print(probabily_one_gen)
    print(probabily_two_gen)



def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    raise NotImplementedError


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    raise NotImplementedError


def nigger():
    joint_probability(THE_PAPUS, {'Harry'}, {'James'}, {'James'})



if __name__ == "__main__":
   # main()
   nigger()
