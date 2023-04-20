from decimal import Decimal
from fractions import Fraction
""""
A classe Simplex é criada com três parâmetros: o número de variáveis, as restrições do problema e a função objetivo. 
A função init armazena esses parâmetros e inicializa algumas variáveis ​​importantes. Em seguida, ele chama o método 
construct_matrix_from_constraints para construir a matriz de coeficientes que será usada no algoritmo simplex.
"""
class Simplex(object):

    """
    calcula a solução final do problema de programação linear e armazena o resultado na variável solution. Se o problema 
    de programação linear for um problema de minimização, o método objetivo_minimize é usado. Caso contrário, o método 
    objetivo_maximize é usado. A função objetivo final é armazenada na variável optimize_val. Se a solução final for 
    solução inviável ou não limitada, o código irá gerar um erro.
    """
    def __init__(self, num_vars, constraints, objective_function):
        """
        num_vars: Número de variáveis

        equações: uma lista de strings representando restrições
        cada variável deve começar com x seguido por um sublinhado
        e um número
        ex. de restrições
        ['1x_1 + 2x_2 >= 4', '2x_3 + 3x_1 <= 5', 'x_3 + 3x_2 = 6']
        Observe que em x_num, num não deve ser maior que num_vars.
        Também espaços simples devem ser usados ​​em expressões.

        função_objetiva: deve ser uma tupla com o primeiro elemento
        seja 'min' ou 'max', e o segundo elemento seja a equação
        por exemplo
        ('min', '2x_1 + 4x_3 + 5x_2')

        Para encontrar a solução, o algoritmo usa o método simplex de duas fases
        """
        self.num_vars = num_vars
        self.constraints = constraints
        self.objective = objective_function[0]
        self.objective_function = objective_function[1]
        self.coeff_matrix, self.r_rows, self.num_s_vars, self.num_r_vars = self.construct_matrix_from_constraints()
        del self.constraints
        self.basic_vars = [0 for i in range(len(self.coeff_matrix))]
        self.phase1()
        r_index = self.num_r_vars + self.num_s_vars

        for i in self.basic_vars:
            if i > r_index:
                raise ValueError("Infeasible solution")

        self.delete_r_vars()

        if 'min' in self.objective.lower():
            self.solution = self.objective_minimize()

        else:
            self.solution = self.objective_maximize()
        self.optimize_val = self.coeff_matrix[0][-1]

    """"
    Este método é responsável por construir a matriz de coeficientes a partir das restrições do problema. Ele itera 
    através de cada restrição e adiciona variáveis de folga, variáveis excedentes e variáveis ​​artificiais, conforme 
    necessário. A matriz resultante é retornada.
    """
    def construct_matrix_from_constraints(self):
        num_s_vars = 0  # Número de variáveis ​​de folga e excedente
        num_r_vars = 0  # número de variáveis ​​adicionais para equilibrar a igualdade e menor que igual a 0
        for expression in self.constraints:
            if '>=' in expression:
                num_s_vars += 1

            elif '<=' in expression:
                num_s_vars += 1
                num_r_vars += 1

            elif '=' in expression:
                num_r_vars += 1
        total_vars = self.num_vars + num_s_vars + num_r_vars

        coeff_matrix = [[Fraction("0/1") for i in range(total_vars+1)] for j in range(len(self.constraints)+1)]
        s_index = self.num_vars
        r_index = self.num_vars + num_s_vars
        r_rows = [] # stores the non -zero index of r
        for i in range(1, len(self.constraints)+1):
            constraint = self.constraints[i-1].split(' ')

            for j in range(len(constraint)):

                if '_' in constraint[j]:
                    coeff, index = constraint[j].split('_')
                    if constraint[j-1] == '-':
                        coeff_matrix[i][int(index)-1] = Fraction("-" + coeff[:-1] + "/1")
                    else:
                        coeff_matrix[i][int(index)-1] = Fraction(coeff[:-1] + "/1")

                elif constraint[j] == '<=':
                    coeff_matrix[i][s_index] = Fraction("1/1")  # add surplus variable
                    s_index += 1

                elif constraint[j] == '>=':
                    coeff_matrix[i][s_index] = Fraction("-1/1")  # slack variable
                    coeff_matrix[i][r_index] = Fraction("1/1")   # r variable
                    s_index += 1
                    r_index += 1
                    r_rows.append(i)

                elif constraint[j] == '=':
                    coeff_matrix[i][r_index] = Fraction("1/1")  # r variable
                    r_index += 1
                    r_rows.append(i)

            coeff_matrix[i][-1] = Fraction(constraint[-1] + "/1")

        return coeff_matrix, r_rows, num_s_vars, num_r_vars

    """"
    implementa a primeira fase do algoritmo simplex, que é usada para encontrar uma solução viável inicial. A primeira 
    fase adiciona variáveis ​​artificiais para transformar o problema em um problema equivalente com solução viável. Ele 
    também modifica a função objetivo para minimizar o valor dessas variáveis ​​artificiais. Em seguida, executa as 
    iterações do algoritmo simplex para melhorar a solução atual.
    """
    def phase1(self):
        # A função objetivo aqui é minimizar r1+ r2 + r3 + ... + rn
        r_index = self.num_vars + self.num_s_vars
        for i in range(r_index, len(self.coeff_matrix[0])-1):
            self.coeff_matrix[0][i] = Fraction("-1/1")
        coeff_0 = 0
        for i in self.r_rows:
            self.coeff_matrix[0] = add_row(self.coeff_matrix[0], self.coeff_matrix[i])
            self.basic_vars[i] = r_index
            r_index += 1
        s_index = self.num_vars
        for i in range(1, len(self.basic_vars)):
            if self.basic_vars[i] == 0:
                self.basic_vars[i] = s_index
                s_index += 1

        # Run the simplex iterations
        key_column = max_index(self.coeff_matrix[0])
        condition = self.coeff_matrix[0][key_column] > 0

        while condition is True:

            key_row = self.find_key_row(key_column = key_column)
            self.basic_vars[key_row] = key_column
            pivot = self.coeff_matrix[key_row][key_column]
            self.normalize_to_pivot(key_row, pivot)
            self.make_key_column_zero(key_column, key_row)

            key_column = max_index(self.coeff_matrix[0])
            condition = self.coeff_matrix[0][key_column] > 0

    """
    A função deste método é encontrar a linha da matriz de coeficientes que será usada como a linha chave em uma 
    iteração do algoritmo simplex. O método normalize_to_pivot normaliza a linha chave dividindo cada elemento pelo 
    valor do pivô. O método make_key_column_zero garante que todos os outros elementos na coluna da linha chave são 
    iguais a zero.
    """
    def find_key_row(self, key_column):
        min_val = float("inf")
        min_i = 0
        for i in range(1, len(self.coeff_matrix)):
            if self.coeff_matrix[i][key_column] > 0:
                val = self.coeff_matrix[i][-1] / self.coeff_matrix[i][key_column]
                if val <  min_val:
                    min_val = val
                    min_i = i
        if min_val == float("inf"):
            raise ValueError("Unbounded solution")
        if min_val == 0:
            print("\nDegeneração\n")
        return min_i

    def normalize_to_pivot(self, key_row, pivot):
        for i in range(len(self.coeff_matrix[0])):
            self.coeff_matrix[key_row][i] /= pivot

    def make_key_column_zero(self, key_column, key_row):
        num_columns = len(self.coeff_matrix[0])
        for i in range(len(self.coeff_matrix)):
            if i != key_row:
                factor = self.coeff_matrix[i][key_column]
                for j in range(num_columns):
                    self.coeff_matrix[i][j] -= self.coeff_matrix[key_row][j] * factor

    def delete_r_vars(self):
        for i in range(len(self.coeff_matrix)):
            non_r_length = self.num_vars + self.num_s_vars + 1
            length = len(self.coeff_matrix[i])
            while length != non_r_length:
                del self.coeff_matrix[i][non_r_length-1]
                length -= 1

    def update_objective_function(self):
        objective_function_coeffs = self.objective_function.split()
        for i in range(len(objective_function_coeffs)):
            if '_' in objective_function_coeffs[i]:
                coeff, index = objective_function_coeffs[i].split('_')
                if objective_function_coeffs[i-1] == '-':
                    self.coeff_matrix[0][int(index)-1] = Fraction(Fraction(Decimal(coeff[:-1])), 1)
                else:
                    self.coeff_matrix[0][int(index)-1] = Fraction(Fraction(Decimal("-" + coeff[:-1])), 1)

    def check_alternate_solution(self):
        for i in range(len(self.coeff_matrix[0])):
            if self.coeff_matrix[0][i] and i not in self.basic_vars[1:]:
                # print("\nSolução alternada não existe.\n")
                break

    def objective_minimize(self):
        self.update_objective_function()

        for row, column in enumerate(self.basic_vars[1:]):
            if self.coeff_matrix[0][column] != 0:
                self.coeff_matrix[0] = add_row(self.coeff_matrix[0], multiply_const_row(-self.coeff_matrix[0][column], self.coeff_matrix[row+1]))

        key_column = max_index(self.coeff_matrix[0])
        condition = self.coeff_matrix[0][key_column] > 0

        while condition is True:

            key_row = self.find_key_row(key_column = key_column)
            self.basic_vars[key_row] = key_column
            pivot = self.coeff_matrix[key_row][key_column]
            self.normalize_to_pivot(key_row, pivot)
            self.make_key_column_zero(key_column, key_row)

            key_column = max_index(self.coeff_matrix[0])
            condition = self.coeff_matrix[0][key_column] > 0

        solution = {}
        for i, var in enumerate(self.basic_vars[1:]):
            if var < self.num_vars:
                solution['x_'+str(var+1)] = self.coeff_matrix[i+1][-1]

        for i in range(0, self.num_vars):
            if i not in self.basic_vars[1:]:
                solution['x_'+str(i+1)] = Fraction("0/1")
        self.check_alternate_solution()
        return solution

    def objective_maximize(self):
        self.update_objective_function()

        for row, column in enumerate(self.basic_vars[1:]):
            if self.coeff_matrix[0][column] != 0:
                self.coeff_matrix[0] = add_row(self.coeff_matrix[0], multiply_const_row(-self.coeff_matrix[0][column], self.coeff_matrix[row+1]))

        key_column = min_index(self.coeff_matrix[0])
        condition = self.coeff_matrix[0][key_column] < 0

        while condition is True:

            key_row = self.find_key_row(key_column = key_column)
            self.basic_vars[key_row] = key_column
            pivot = self.coeff_matrix[key_row][key_column]
            self.normalize_to_pivot(key_row, pivot)
            self.make_key_column_zero(key_column, key_row)

            key_column = min_index(self.coeff_matrix[0])
            condition = self.coeff_matrix[0][key_column] < 0

        solution = {}
        for i, var in enumerate(self.basic_vars[1:]):
            if var < self.num_vars:
                solution['x_'+str(var+1)] = self.coeff_matrix[i+1][-1]

        for i in range(0, self.num_vars):
            if i not in self.basic_vars[1:]:
                solution['x_'+str(i+1)] = Fraction("0/1")

        self.check_alternate_solution()

        return solution

def add_row(row1, row2):
    row_sum = [0 for i in range(len(row1))]
    for i in range(len(row1)):
        row_sum[i] = row1[i] + row2[i]
    return row_sum

def max_index(row):
    max_i = 0
    for i in range(0, len(row)-1):
        if row[i] > row[max_i]:
            max_i = i

    return max_i

def multiply_const_row(const, row):
    mul_row = []
    for i in row:
        mul_row.append(const*i)
    return mul_row

def min_index(row):
    min_i = 0
    for i in range(0, len(row)):
        if row[min_i] > row[i]:
            min_i = i

    return min_i