import os
from simplex import Simplex

# Exemplo de inputs:
#  - Informe o número de váriaveis: 2
#  - Informe a função objetiva: max=4x_1 + 3x_2
#  - Adicionar outra restrição: 2x_1 + 1x_2 <= 1000

if __name__ == '__main__':
    running = True
    while running:
        print("MÉTODO SIMPLEX\n")

        num_vars = int(input('Informe o número de váriaveis: '))
        objective_function = input('Informe a função objetiva: ')
        constraints = []

        adding_constraints = True

        while adding_constraints:
            constraint = input('Informe uma restrição: ')
            constraints.append(constraint)

            ac: str = input('Adicionar outra restrição? (s/n): ')

            if ac != 's' and ac != 'S':
                adding_constraints = False

        obj_parts = objective_function.split('=')

        try:
            simplex = Simplex(
                num_vars=num_vars,
                constraints=constraints,
                objective_function=(obj_parts[0].lower(), obj_parts[1]))
            
            print('\n')
            print(f'Solução: {simplex.solution}')
            print(f'Valor otimizado: {simplex.optimize_val}')
        except ValueError:
            print('\nDados adicionados são inválidos')

        ac: str = input('\nDeseja resolver novamente? (s/n): ')

        if ac != 's' and ac != 'S':
            running = False

        os.system('clear')
