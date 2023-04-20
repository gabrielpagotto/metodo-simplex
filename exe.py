from simplex import Simplex

# Primeira aplicação
funcaoObjetivo = ('maximize', '4x_1 + 3x_2')
restricoes = [
    '2x_1 + 1x_2 <= 1000', 
    '1x_1 + 1x_2 <= 800', 
    '1x_1 + 0x_2 <= 400'
]

simplex = Simplex(num_vars=2, constraints=restricoes, objective_function=funcaoObjetivo)

print(simplex.solution)
print(simplex.optimize_val)

# Segunda aplicação
funcaoObjetivo = ('maximize', '10x_1 + 6.5x_2 + 8_x3 + 9_x4')
restricoes = [
    '1x_1 + 1x_2 + 1x_3 + 1x_4 <= 25', 
    '9x_1 + 25x_2 + 7x_3 + 8x_4 <= 480', 
    '11x_1 + 6x_2 + 11x_3 + 10x_4 <= 240', 
]

simplex = Simplex(num_vars=4, constraints=restricoes, objective_function=funcaoObjetivo)

print(simplex.solution)
print(simplex.optimize_val)
