from logic import *

AKnight = Symbol("A is a Knight")
AKnave = Symbol("A is a Knave")

BKnight = Symbol("B is a Knight")
BKnave = Symbol("B is a Knave")

CKnight = Symbol("C is a Knight")
CKnave = Symbol("C is a Knave")

# Puzzle 0
# A says "I am both a knight and a knave."
character_A = Symbol("I am both a knight and a knave.")
knowledge0 = And( #Esta es la informacion inicial done no pueden ser ambos
    Implication(AKnight, Not(character_A)), #Es una falacia la declaracion que dijo, por ende el cabellero no debio decirlo
    Implication(AKnave, (character_A)), #Al ser una falacia tuvo que decirlo el sota
    Or(AKnave, AKnight), #Solo puedo ser uno de los 2
    character_A # Es la declaracion que dijo
)

# Puzzle 1
# A says "We are both knaves."
# B says nothing.
character_1A = Symbol("We are both knaves.")
character_1B = Symbol("")
knowledge1 = And(
    Implication(AKnight, Not(character_1A)),
    Implication(AKnave, character_1A),
    Or(AKnave, AKnight),
    character_1A,
)
knowledge1.add(And(
    #Implication(character_1A, And(AKnave, Not(AKnight))),
    BKnight
))

# knowledge1.add(And(
#     Or(BKnight, BKnave),
#     character_1B
# ))

# Puzzle 2
# A says "We are the same kind."
# B says "We are of different kinds."
charA2 = Symbol("We are the same kind")
charB2 = Symbol("We are of different kinds")
knowledge2 = And(
    Implication(AKnight, Not(charA2)),
    #Biconditional((AKnight, Not(charB2)), (BKnight, charB2)),
    Or(AKnave, AKnight),
    charA2,
)

knowledge2.add(And(
    Implication(BKnave, Not(charB2)),
    Or(BKnave, BKnight),
    charB2)
)

# Puzzle 3
# A says either "I am a knight." or "I am a knave.", but you don't know which.
# B says "A said 'I am a knave'."
# B says "C is a knave."
# C says "A is a knight."
charA3  = Symbol("I am a knight. or I am a knave.")
charB31 = Symbol("A said 'I am a knave'")
charB32 = Symbol("C is a Knave")
charC3  = Symbol("A is a knight.")
knowledge3 = And(
    Or(CKnave, CKnight),
    Or(AKnight, AKnave),
    Or(BKnight, BKnave)
)

#Logica para determinar el PersonajeA
knowledge3.add(And(
    Implication(AKnave, Not(charA3)),
    charA3
))

#Logica para determinar el C
knowledge3.add(And(
    Implication(CKnave, Not(AKnight)),
    charC3
))

knowledge3.add(And(
   Implication(BKnight, CKnave),
   Implication(BKnight, Not(charA3))
   
))


def main():
    symbols = [AKnight, AKnave, BKnight, BKnave, CKnight, CKnave]
    puzzles = [
        ("Puzzle 0", knowledge0),
        ("Puzzle 1", knowledge1),
        ("Puzzle 2", knowledge2),
        ("Puzzle 3", knowledge3)
    ]
    for puzzle, knowledge in puzzles:
        print(puzzle)
        if len(knowledge.conjuncts) == 0:
            print("    Not yet implemented.")
        else:
            for symbol in symbols:
                if model_check(knowledge, symbol):
                    print(f"    {symbol}")


if __name__ == "__main__":
    main()
