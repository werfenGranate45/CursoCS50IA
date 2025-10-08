import os
import random
import re
import sys

DAMPING       = 0.85
SAMPLES       = 10_000
ACCURATE_ITER = 0.001

def number_links(corpus, page_i):
    """
    Numero de links de la pagina dada, usanda para la pagina page,
    es parte del denominador
    """
    for key, values in corpus.items():
        
        if key == page_i:
            return len(values)
        
    return len(corpus) #sI no tiene links salientes

def add_factor(damping_factor, number_pages):
    """Ayuda al factor en el que se elimina el damping factor"""
    return (1 - damping_factor) / number_pages

def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")

def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages



def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    dict_pages   = {}
    number_pages = len(corpus)

    #Obtenemos los valores claves dada la pagina, page es la clave
    #Si la pagina tiene links salientes eligimos la probabilidad entre 1-damping_factor
    values_page = corpus.get(page)
    if values_page:
        number_link_to_page = len(values_page)

        #Todos tienen la misma probabilidad igual de que salgan asi que la dividimos pasa obtener sus probabilidades
        proba = (damping_factor) / number_link_to_page
        #Solo se tiene que meter la probabilidad de arriba a las paginas que vienen en los valores
        #Ademas a todas la probabilidad se le agrega su facotor de 0.05 correspondiente
        for key in corpus.keys():
            #Si es la misma pagina solo se añade el factor
            if key in values_page:
                dict_pages.update({key: proba + add_factor(damping_factor, number_pages)})
            else:
                #Si no se encuentra su link solo se le da el factor para que exista probabilidad
                dict_pages.update({key: add_factor(damping_factor, number_pages)})
    else:
        #En caso de que no tenga linkis salientes la probabilidad de distribucion entre el numero de paginas incluida la misma
        #Si no tiene paginas salientes entoces, el retorno de probabilidad debe ser igual la probabilidad de distribucion
        #Igual ese resultado sera igual a 1 sin el damping factor
        proba = 1 / number_pages
        for key in corpus.keys():
            dict_pages.update({key: proba})
    
    # suma = 0
    # for values in dict_pages.values():
    #     suma+= values
    
    # print(suma)

    return dict_pages

def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    _____________________________________________________________
    1: El primer ejemplo es usado una pagina forma aleatoria
    2: Por cada muestra restantes, el siguiente ejemplo debera generar
    del previo ejemplo basado en la muestra anterior del modelo de transicion
        2.1: Debes pasar el ejemplo previo en el modelo transisional para obtener las
        probaabilidades del siguiente ejemplo
    """
    track_visit = {page: 0 for page in corpus}
    if not n >= 1:
        raise Exception("n debe ser almenos 1")
    
    #Primero debo de ciclar entre las muestras n
    #Esta es la parte en la que tomo de forma aleatoria de una pagina
    current_page = random.choice(list(corpus.keys()))
    track_visit[current_page] += 1
    for _ in  range(n):
       probabilty = transition_model(corpus, current_page, damping_factor)
        #Aqui se crea la cadena de markov y hace la union en la que el que das eleccion a distibucion de probabilidad
        #De todos las llaves de la muesta anterior, donde el peso da un parametro extra de probabilidad, tendiendo
        #A determinada pagina, por ejemplo {html1: 0.05, html2: 0.475}, con el peso se le da que habra una probabilidad del 47.5% 
        #De mas probabilidad cuando toque dicha pagina
       current_page = random.choices(
           population=list(probabilty.keys()),
           weights=list(probabilty.values()),
           k=1
       )[0]

       """
       Esta es parte del metodo del sample y de page rank, ya que debemos dividir el numero de veces que se visito esa pagina
       Entre la cantidad de total de todas las paginas visitidas
       """

       track_visit[current_page] += 1

    total_visits = sum(track_visit.values())
    page_rank = {page: count / total_visits for page, count in track_visit.items()}

    return page_rank
    
def get_i(corpus, page_target):
    """Obtengo el rango de las paginas que linkean con la pagina dada"""
    pages = []

    for key, values in corpus.items():
        if not (key == page_target) and page_target in values:
            pages.append(key)

    return pages 

def calcute_sigma_componet(d, corpus, target_page, current_pr):
    """Esta es la parte en la que solo se calcula la segunda condicion"""
    link_componet = 0
    pages_i       = get_i(corpus, target_page)
    
    if not len(corpus[target_page]): #Si una pagina no tiene links, se debe tomar en cuenta que puede acceder a todas las paginas incluyendose
        pages_i = [page for page in list(corpus.keys())]

    for page_i in pages_i:
        num_links_i = number_links(corpus, page_i)
        
        if not num_links_i: #Si una pagina no tiene links, se debe tomar en cuenta que puede acceder a todas las paginas incluyendose
            num_links_i = len(corpus)

        link_componet += current_pr[page_i] / num_links_i
    
    return link_componet


def page_rank(d, corpus, page_target: str, current_pr: dict):
    """
    Hago la formula iterativa para el calculo de la page range 
    Dada una pagina dada cual es la probabilidad de que alguien le pique a la pagina caon
    __________________________________________________________
    1. Obtengo el primer valor con la primera condicion
    2. En base a la pagina objetivo, obtengo las paginas que enlazan, representando el rango `i`
    3. Gracias a una funcion adentro con argumentos value: Representa la primera parte, y las iteraciones: Representa rango i
    
    No es recursiva tenemos en cuenta que la sigma de I es la cantidad de paginas adentro
    del conjunto de las paginas i, osea iterar sobre las paginas i
    """
    N = len(corpus)
    #Primer se calcula la primera condicion de la formula, guarda en la variable primero
    #Obtengo todas las paginas la cual linkean a la pagina target
    random_component = add_factor(d, N) 

    return random_component + d*(calcute_sigma_componet(d, corpus, page_target, current_pr))

def please_stop(new_values, old_values):
    """
    Este metodo hace que termine el ciclo ya que nos debemos asegurar que la diferencia se menor de lo acordado 0.001
    Los agregamos una lista en caso de que si, de lo contrario 0 y ya con all nos aseguramos que efectivamente
    todos los valores sean 1, que significa que acabado el procedimiento
    """
    
    diferencias = [( values - new_values[page] ) for page, values in old_values.items()]

    penes = [1 if abs(dif) < ACCURATE_ITER else 0 for dif in diferencias]

    return all(penes)

def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.


    La forma iterativa es el conjunto de la pagina i que tiene en las lista que se obtiene del get_pagei
    Iteramos sobre la lista ya que el i si representa el conjunto de las paginas que enlazan ademas de 
    seguir las indicaciones de los requerimientos
    """
    N         = len(corpus)
    #Toda la probabilidad de las paginas
    #Una pagina que no tiene links saliente debe crerse que esta enlazada a todas incluidad asi mismo
    
    pr             = {keys: 1 / N for keys in corpus.keys()}
    llaves         = list(corpus.keys())
    old_values     = {}

    while True: #Mientras haya llaves
        for page in llaves:
            new_value = page_rank(damping_factor, corpus, page, pr)
            old_value = pr.get(page)

            old_values.update({page: old_value})            
            pr.update({page: new_value})
        
        stop = please_stop(pr, old_values)
        if stop:
            break
    return pr

if __name__ == "__main__":
    main()
