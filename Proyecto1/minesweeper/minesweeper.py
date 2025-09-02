import itertools
import random


board_moves = [
    [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)], 
    [(1, 0), (1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7)], 
    [(2, 0), (2, 1), (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7)], 
    [(3, 0), (3, 1), (3, 2), (3, 3), (3, 4), (3, 5), (3, 6), (3, 7)], 
    [(4, 0), (4, 1), (4, 2), (4, 3), (4, 4), (4, 5), (4, 6), (4, 7)], 
    [(5, 0), (5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6), (5, 7)], 
    [(6, 0), (6, 1), (6, 2), (6, 3), (6, 4), (6, 5), (6, 6), (6, 7)], 
    [(7, 0), (7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
]
"""
    Representacion de los movimietos del tablero, ojo 8x8
    TODO Que se aplique al ancho y alto dado por el usuario 
"""
class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """
    #Cells que me la pase como una lista
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        """
        Este metodo se llama automaticamente para comparar si la sentencia de abajo
        es verdadera usando el ==, comparando 2 objetos entre si
        """
        return self.cells == other.cells and self.count == other.count
    
    def __sub__(self, other):
        """Método que soporta el operador de resta y devuelve un objeto de la misma clase"""
        # Restar las celdas y el count
        new_cell  = self.cells - other.cells
        new_count = abs(self.count - other.count)
    
        return self.__class__(new_cell, new_count)

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #Si el contador es 0, ninguna es una mina por ende no hay minas
        # if self.count == 0:
        #     return set()
        
        #Si numero de celdas es igual al contador, todas son minas
        if self.count == len(self.cells): #Esta puta mierda esta mal no me caste bien el set
            return self.cells
        
        #En caso de que no hay tocado las condiciones, no podemos saber nada ???
        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #Si el numero de celdas es igual a 0, entoces todas son seguras
        if self.count == 0:
            return self.cells
        
        #Si el numero de celdas es igual al, contador, entoces todas son minas, y regresamos un set vacio
        #if self.count == len(self.cells):
        #     return set()
        
        #De lo contrario, no sabemos con certeza si son celdas seguras
        return set()
        

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:
            self.cells.remove(cell) #Pase lo que pase siguen siendo oreaciones corrctas o True
            self.count -= 1 #Esto es por el momento en caso de que otro algoritmo lo cambie
            
    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
       
        if cell in self.cells: #Pase lo que pase siguen siendo oraciones correctas
            self.cells.remove(cell)
        
    def config_sentence(self, cell, count):
        #En caso de que solo entregue una celda una tupla no podemos concluir nada
        #Si no es 0 ni uno no sabes por ende es indeterminada y la agregegas a la oracion
        if count != 0 and count != 1:
            self.cells.add(cell)
        
class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

     #Aqui implementar la funcion get_vecinos
    def make_sentence(self, cell, count) -> list:
        """Funcion que te entrega las celdas necesarias del movimiento seleccionado"""
        #Agrega las celdas vecinas
        neighbors = []

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if board_moves[i][j] in self.mines:
                        count -= 1
                    if board_moves[i][j] not in self.safes and board_moves[i][j] not in self.mines:
                        neighbors.append(board_moves[i][j])
        
        return neighbors, count

    def make_infer(self, sentence: Sentence, new_sentence: Sentence):
        #El chico es el de cells y no el de new cells
        # {A,B,C}     = 2 cells
        # {A,B,C,D,E} = 1 new_cells
        is_sub = sentence.cells.issubset(new_sentence.cells)
        #Solo se puede aplicar esta logica si es un subset
        #Y el residuo siempre sera el chiquito o lo que se pierde
        if is_sub and not sentence == new_sentence:
            return new_sentence - sentence

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)            
        cells, n_count = self.make_sentence(cell, count)
        new_sentence   = Sentence(cells, n_count)
        mines, safes   = new_sentence.known_mines(), new_sentence.known_safes()
        #TODO No iterar y mejor la forma de agregar las celadas al buscar como hacerlo
        if mines: #Iteracion de mierda no hacer esto, papu da errores
            for mine in mines:
                self.mark_mine(mine)
        elif safes:
            for safe in safes:
                self.mark_safe(safe)
        else:
            if new_sentence: #Si la oreacion esta vacía la neta no la metas caon
                self.knowledge.append(new_sentence)
            knowledge = self.knowledge.copy()
            n = len(knowledge)
            if not n == 1:
                for i in range(n):
                    for j in range(0, n-i-1):
                        #Creo una inferencia
                        infer = self.make_infer(knowledge[j], knowledge[j+1])
                        #En caso de que haya una, verifica si con certeza sus celdas son minas o seguras
                        if infer: 
                            mines, safes   = infer.known_mines(), infer.known_safes()
                            if mines:
                                for mine in mines:
                                    self.mark_mine(mine)
                            elif safes:
                                for safe in safes:
                                    self.mark_safe(safe)
                            else: # En caso de que no haya certeza la agregas al conocimento
                                self.knowledge.append(infer)
            #Aqui ultima verificada en caso de que alguna oracion haya cambiado y puedas crear un inferencia existosa
        for setence in self.knowledge:
            mines, safes   = setence.known_mines(), setence.known_safes()
            if mines:
                for mine in mines: #Igual logica de mierda
                    self.mark_mine(mine)
                self.knowledge.remove(setence)
            elif safes:
                for safe in safes:
                    self.mark_safe(safe)
                self.knowledge.remove(setence)


        # for i in range(len(knowledge)):
        #     for j in range(len(knowledge)):
        #         pass
        #     mines, safes = knowledge[i].known_mines(), knowledge[i].known_safes()
        #     #Con esto yo me aseguro que esta inderterminado me debo de asegurar de no agregar las 
        #     #Indeterminadas 
        #     if mines:
        #         for mine in mines:
        #             self.mark_mine(mine)
        #     if safes:
        #         for safe in safes:
        #             self.mark_safe(safe)
        #     else:
        #         """TODO COMPARAR CON TODAS LAS ORACIONES EN EL FOR PERO LA ESTRUCTURA ES LA MISMA"""
        #         #Que pasa si la oracion esta indeterminada, tenemos que usar el metodo de atras
        #         if not sentence == new_sentence: #En este caso pues no se infiere nada no pasa nada
        #             #Ya que esta infiriendo
        #             infer = self.make_infer(sentence, new_sentence)

        #             if infer:
        #                 mines, safes = infer.known_mines(), infer.known_safes()

        #                 #Si con la inferencia determinanos que minas o seguras entonces
        #                 #Las agregamos, sin embargo no se como esta el de las minas, el agregado
        #                 #TODO AGREGAR CORRECTAMENTE LAS MINAS, y las celdas segurar encontrar la forma
        #                 if mines:
        #                     for mine in mines:
        #                         self.mines.add(mine)
        #                 if safes:
        #                     for safe in safes:
        #                         self.safes.add(safe)
        #                         #Cualquier inferencia que pueda ser

        #                 #Agregas la nueva inferencia
        #                 self.knowledge.append(infer)

    def make_safe_move(self):
        #Lo mas importante no modifico nada
        #Pero se contradice por que los self.safes son movientos ya hechos
        #Los movientos seguros los debe inferir en base al conocimentos
        #Que es el que me puede indicar si todo esta correcto

        for safe in self.safes: #Primero
            if safe not in self.moves_made and safe not in self.mines:
                return safe
        else:
            return None
        
    def get_moves(self):
        return [(i,j) for i in range(3) for j in range(3) if (i,j) not in self.moves_made and not self.mines]

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #Obtengo todos los movimientos del tabler
        moves          = self.get_moves()
        possible_moves = []

        #Busco en las oraciones de mi base
        #for sen in self.knowledge:
        for move in moves:
            #Por cada movimento si no esta en los movimentos hechos 
            if move not in self.moves_made:
                #Y que en el knowledge sepa que no son minas, los añada a un set de posibles acciones 
                if move not in self.mines:
                    possible_moves.append(move)

        #Una vez obtenido mis movimentos, elegimos en caso de que no este vacio posible moves
        if not len(possible_moves) == 0:
            #Elijo el movimeinto aleatorio, y lo meto al set de moviemntos hechos
            move = random.choice(possible_moves)
            self.moves_made.add(move) #No se si modificar yo creo que si caon Pero !CUIDADO!
            return move
        
        return None

        

                
        
