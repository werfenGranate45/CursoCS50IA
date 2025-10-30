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
    # if len(sys.argv) != 2:
    #     sys.exit("Usage: python heredity.py data.csv")
    people = load_data('/home/werfengranate45/ProyectsIA/Proyecto2/heredity/data/family1.csv')

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



def get_gen_father(parent, one_gen, two_gene):
    """
    Esa mutacion consta de acuerdo a la cantidad de copias del gen
        * Si tiene 2 copias del gen entoces 100% le pasara los genes asi que el calculo es: `1-PROB['mutation]`
        * Si tiene 1 copias del gen entoces 50% le pasará los genes asi que el calculo es `0.5-PROB[mutation]`
        * Si tiene 0 copias del gen le pasara directamente la probabilidad de `PROB['mutation]`
    En caso de que haya un papa con 0 y otro con 1 o 2  se pueden agregar juntos
    """
    from_two_copy = 1 - PROBS['mutation']
    from_one_copy = 0.5

    if parent in one_gen:
        #Probabilidad de tener el gen, dada la copia del gen
        return from_one_copy

    if parent in two_gene:
        #La probabilidad de tener 2 copias del gen
        return from_two_copy
    #Si el padre no esta en el set de un gen ni el del 2 gen entoces se regresa solo la mutacion
    return PROBS['mutation'] 
    
def calculate_set_one_gene(people, one_gene, two_gene, name,have_trait):
    """
    Metodo que calcula todas las probabilidades del set de personas que tengan un gen
    """
    #El extra es la variable cuando un padre no tiene copias, "No estoy seguro si eso correcto"
    trait    = 1
    extra    = 1
    proba    = 0

   
    if not_have_a_parent(people, name): #Si no tiene padres
        proba = PROBS['gene'][1] #Obtenemos la probabilidad del gen
        #¿Aqui? debemos calcular junto con su trait??, en caso debemos verificar si esta en el trait
    else:
        #Primero hay que conseguir a sus padres
        father = people[name]['father']
        mother = people[name]['mother']
       
        #Segundo, Obtenemos las probabilidades en base a sus genes todos tienen una probabilidad de que mute con 0.01
       
        father_gen = get_gen_father(father, one_gene, two_gene)
        mother_gen = get_gen_father(mother, one_gene, two_gene) 
        #Tercero Juntamos las probabilidades
        #Caso uno cuando el gen se lo transimete su madre pero no su padre
        given_mom = people[mother][PROBS]
        if father_gen == PROBS['mutation']:
            extra = (PROBS['mutation'], mother_gen)
        if mother_gen == PROBS['mutation']:
            extra = (PROBS['mutation'],  father_gen)
        extra = (1,1)
        proba = (father_gen * extra[1] + extra[0] * mother_gen)
    
    lock = people[name].get('trait')
    if lock is not None:
        trait = PROBS['trait'][1][people[name]['trait']]    
    else:
        trait = PROBS['trait'][1][name in have_trait] 

    return (proba*trait)
        

def calculate_set_two_genes(people, one_gene, two_genes, name, have_trait):
    """
    Metodo homologo al one gene calcula todas las probabilidades del 
    set de personas que se encuentran en el set de las copias de 2 perosnas
    """
    extra = 1
    proba = 0
    trait = 1

 
    if not_have_a_parent(people, name):
        proba = PROBS['gene'][2]
    else:
        #Primero hay que conseguir a sus padres
        father = people[name]['father']
        mother = people[name]['mother']
       
        #Segundo, Obtenemos las probabilidades en base a sus genes todos tienen una probabilidad de que mute con 0.01
        father_gen = get_gen_father(father, one_gene, two_genes)
        mother_gen = get_gen_father(mother, one_gene, two_genes) 
        #Tercero Juntamos las probabilidades
        if father_gen == PROBS['mutation']:
            extra = (PROBS['mutation'] , mother_gen)
        if mother_gen == PROBS['mutation']:
            extra = (PROBS['mutation'] , father_gen)
        extra = (1,1)
        #proba = (father_gen * mother_gen) * (extra)
        proba = (father_gen * extra[1] + extra[0] * mother_gen)
    
    lock = people[name].get('trait') #En esta parte solo es un seguro
    if lock is not None: #ESTA probabilidad sera por aparte, de los traists y tienen que ser calculadas
        trait = PROBS['trait'][2][people[name]['trait']]
    else:
            trait = PROBS['trait'][2][name in have_trait]

    return (proba*trait)

def calculate_set_no_genes(people, one_gene, two_genes, name, have_trait):
    """
    Metodo que calcula todas las personas que no tienen gen copia ni traits
    """
    trait = 1 #Trait desconocido
    extra = 1, 1
    
    #for name in no_gen_people:
    if not_have_a_parent(people, name):
            proba = PROBS['gene'][0]
    else:
        #Primero hay que conseguir a sus padres
        father = people[name]['father']
        mother = people[name]['mother']
           
            #Segundo, Obtenemos las probabilidades en base a sus genes todos tienen una probabilidad de que mute con 0.01
           
        father_gen = get_gen_father(father, one_gene, two_genes)
        mother_gen = get_gen_father(mother, one_gene, two_genes) 

        #Tercero Juntamos las probabilidades, esto es lo unico mierdon a que vamos a corregir
        if father_gen == PROBS['mutation']:
            extra = (PROBS['mutation'],  mother_gen)
            proba = (father_gen * extra[1] + extra[0] * mother_gen)
        if mother_gen == PROBS['mutation']:
            extra = (PROBS['mutation'],  father_gen)
            proba = (father_gen * extra[1] + extra[0] * mother_gen)
        extra = (1,1)
        proba = (father_gen * mother_gen)

    lock = people[name].get('trait') #Conseguir de forma segura el trait para que no haya None 
    if lock is not None:
        trait = PROBS['trait'][0][people[name]['trait']]
    else:
        trait = PROBS['trait'][0][name in have_trait]
        
    return (name, proba*trait)


def get_and_check_trait(people, name, copy_gene, have_trait):
    """
    Metodo que retornade forma segura el trait de una perosna
        * people     -> El set de perosna
        * name       -> El nombre de la persona
        * copy       -> Cuantas copias tiene 0,1,2
        * have_trait -> data set de trait
    """
    
    return PROBS['trait'][copy_gene][people[name]['trait']] if people[name].get('trait') is not None else PROBS['trait'][copy_gene][name in have_trait]

def not_have_a_parent(data_set, name):
    """Metodo auxiliar que verifica si una persona tiene padres en el data_Set"""
    return data_set[name]['father'] is None and data_set[name]['mother'] is None


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    
    El trait ya estan filtrados es un set donde llegan todos los que su trait sea true e ignoran
    los que tengan false o None --> Ojo si es None debes obtener de forma segura
    """
    proba_dicc = {}
    value = 0
    no_copy_gen = [name for name in people.keys() if name not in one_gene and name not in two_genes]
    #En caso de que no tenga copias
    """
    
        1. Verificamos que no tenga padres para calcular su probabilidad incodicional y su trait
        2. Si tiene padres, debemos calcular en base a si esta en one_gene o two_genes 
           -- Obtenemos sus papas, para vericar cuantos gen de la copia tiene los padres
           -- Tenemos observar la probabilidad de recibir una copia por parte de los padres, obtenemos esa info en one_gen o two_gen
        3. Guardar la probabilidad que es: proba(condicional o incondicional) * trait, en un dicc
        4. Al final se multiplica todoas las probabilidades en el diccionario y se manda
    """
    for person in no_copy_gen:
        if not_have_a_parent(people, person):
            #Si no hay padre usamos la probabilidad incondicional apuntando a 0 copias
            proba = PROBS['gene'][0]
            #Obtenemos su trait, checamos en el people su trait
            trait = get_and_check_trait(people, person, 0, have_trait)

            join_proba = proba * trait
        else:
            #Si tiene papas entoces vemos quien es el hijo ?? es persona obtenemos sus papas ya que debemos verificar
            #En este caso estamos en las personas de que cual es la probabilidad 0 copias del gen de sus padres, 
            # ya que el hijo no esta ni en one_gene ni en two_genes
            father = people[person]['father']
            mother = people[person]['mother']
            # if father in one_gene and mother in one_gene: #Ambos tiene una probabilidad de pasarle del 50% su gen
            #     prob_pass_father = get_and_check_trait(people, person, 1, have_trait)
            #     prob_pass_mother = get_and_check_trait(people, person, 1, have_trait)
            # if mother in two_genes and father in two_genes:
            #     pass 

            if mother in no_copy_gen and father in no_copy_gen:
                """
                Esto es una contradicion al fin al cabo, debido a que como tiene 0 copias del gen mutado su "probabilidad" es pasarle al hijo con 0%,
                sin embargo como estamos en los 0 copias ya filtrado, cambia la probabilidad o tarea de no recibir genes mutados pero se espera que 
                pase un gen normal se le quite su proba de mutacion siendo 1 - mutacion
                """
                # Probabilidad de que padre NO pase el gen mutado
                prob_no_pass_father = 0.99  # (1 - mutation) porque tiene 0 copias
                # Probabilidad de que madre NO pase el gen  mutado
                prob_no_pass_mother = 0.99  # (1 - mutation) porque tiene 0 copias
            
            if mother in two_genes and father in two_genes:
               """
               Esto es una contradicion al fin al cabo, debido a que como tiene 2 copias del gen mutado su "probabilidad" es pasarle al hijo con 100%,
               sin embargo como estamos en los 0 copias ya filtrado, cambia la probabilidad o tarea de no recibir genes mutados, por eso se presenta la mutacion
               """
               # Probabilidad de que el padre con 2 copias no las pase al hijo 
               prob_no_pass_father = PROBS['mutation']  # Solo mutacion porque tiene 2 copias mutadas y se ocupa esa pequeña mutacion para que de gen mutado pase a normal
               # Probabilidad de que la madre con 2 copias no las pase al hijo
               prob_no_pass_mother = PROBS['mutation']  # Solo mutacion porque tiene 2 copias mutadas y se ocupa esa pequeña mutacion para que de gen mutado pase a normal
            
            """
            Si ambos tienen una sola copias, ambos tiene una probabilidad del 0.5 de parle el normal, ya que tienen uno chafilla, pero debemos agregar la mutacion del 
            1 - mutacion debido a que esa es la probabilidad de mantenerlo normal el gen OJO SOLO EN ESTE CASO YA QUE EL HIJO SE LE PIDE QUE NO TENGA COPIAS DEL GEN MUTADO
            """

            if mother in one_gene and father in one_gene:
                prob_no_pass_father = 0.5
                prob_no_pass_mother = 0.5
            
            join_proba = (prob_no_pass_father * prob_no_pass_mother) * get_and_check_trait(people, person, 0, have_trait)

        proba_dicc.update({person: join_proba})
        
        #Multiplico todos los valores calculados
        for value in proba_dicc.values():
            value*=value
            
    return value

def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    return 'nigger'


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    return 'penes'


def nigger():
    joint_probability(THE_PAPUS, {'Harry'}, {'James'}, {'James'})



if __name__ == "__main__":
   main()
   #nigger()
