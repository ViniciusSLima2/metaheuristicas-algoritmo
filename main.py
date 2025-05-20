import json
from collections import defaultdict
import matplotlib.pyplot as plt
import random
import math
import copy
import mplcursors
jsonFile = open("data_mock_1000.json", "r", encoding="utf-8")
data = json.loads(jsonFile.read())
jsonFile.close()

def createCostByProjectJSON():
    peopleData = data["data"]
    projectsCost = defaultdict(list)
    professionalsCapacity = {}
    for personName in peopleData.keys():
        professionalsCapacity[personName] = data["data"][personName]["capacity"]
        personData = peopleData[personName]
        for index, project in enumerate(personData["resourceByProject"].keys()):
            projectsCost[project].append([personName, personData["resourceByProject"][project]])
    return projectsCost, professionalsCapacity

def orderCostByProjectJSONByCost(costByProjectJSON):
    for project in costByProjectJSON:
        costByProjectJSON[project].sort(key=lambda x: x[1])
    return costByProjectJSON

def assignProfessionalToProject(orderedCostByProjectJSON, professionalsCapacity):
    assignedProfessionalToProject = {}
    for projectName in orderedCostByProjectJSON.keys():
        for projectCosts in orderedCostByProjectJSON[projectName]:
            if(professionalsCapacity[projectCosts[0]] >= projectCosts[1]):
                assignedProfessionalToProject[projectName] = projectCosts[0]
                break
    return assignedProfessionalToProject

def plotResult(result):
    rows = [[project_id, person] for project_id, person in result.items()]

    # Cria a figura e o eixo
    fig, ax = plt.subplots()
    ax.axis('off')
    ax.axis('tight')

    # Cabeçalhos da tabela
    columns = ["Projeto ID", "Pessoa"]

    # Cria a tabela
    table = ax.table(cellText=rows, colLabels=columns, loc='center', cellLoc='center')

    # Estética
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1.2, 1.5)

    plt.title("Responsáveis por Projeto", pad=20)
    plt.show()



def calculate_total_cost(assignments, costByProjectJSON, professionalsCapacity, penalty_factor=1000):
    used_capacity = defaultdict(float)
    total_cost = 0

    for project, person in assignments.items():
        project_cost = next((c for p, c in costByProjectJSON[project] if p == person), None)
        if project_cost is None:
            continue

        used_capacity[person] += project_cost

        # Aplica penalidade se exceder a capacidade
        if used_capacity[person] > professionalsCapacity[person]:
            penalty = penalty_factor * (used_capacity[person] - professionalsCapacity[person])
            total_cost += project_cost + penalty
        else:
            total_cost += project_cost

    return total_cost

def is_valid_assignment(project, person, professionalsCapacity, assignments, costByProjectJSON):
    used_capacity = defaultdict(float)
    for proj, assigned_person in assignments.items():
        if assigned_person:
            for p, cost in costByProjectJSON[proj]:
                if p == assigned_person:
                    used_capacity[p] += cost
                    break

    # Verificar se adicionar este projeto ao profissional excede a capacidade
    for p, cost in costByProjectJSON[project]:
        if p == person:
            if used_capacity[person] + cost <= professionalsCapacity[person]:
                return True
    return False

def generate_neighbor(solution, costByProjectJSON):
    neighbor = copy.deepcopy(solution)

    # Escolhe um projeto aleatoriamente
    project = random.choice(list(neighbor.keys()))

    # Seleciona aleatoriamente uma pessoa possível para esse projeto
    possible_people = [p for p, _ in costByProjectJSON[project]]
    if possible_people:
        neighbor[project] = random.choice(possible_people)

    return neighbor

import time
def simulated_annealing(initial_solution, costByProjectJSON, professionalsCapacity, T=6000, alpha=0.99, T_min=0.1, penalty_factor=1000):
    current_solution = initial_solution
    best_solution = initial_solution
    current_cost = calculate_total_cost(current_solution, costByProjectJSON, professionalsCapacity, penalty_factor)
    best_cost = current_cost

    history = [best_cost]  # histórico de custos
    start_time = time.time()
    while T > T_min:
        if(time.time() - start_time > 600): #máximo de 10 minutos para o algoritmo rodar, caso estourar, retorna a melhor solução obtida
            break
        for _ in range(100):
            neighbor = generate_neighbor(current_solution, costByProjectJSON)
            neighbor_cost = calculate_total_cost(neighbor, costByProjectJSON, professionalsCapacity, penalty_factor)

            delta = neighbor_cost - current_cost
            if delta < 0 or random.uniform(0, 1) < math.exp(-delta / T):
                current_solution = neighbor
                current_cost = neighbor_cost
                if neighbor_cost < best_cost:
                    best_solution = neighbor
                    best_cost = neighbor_cost
                    history.append(best_cost)
        T *= alpha

    return best_solution, history

def plot_cost_history(history):
    plt.figure(figsize=(10, 5))
    line, = plt.plot(history, marker='o', label='Custo da Melhor Solução')
    plt.title('Evolução do Custo no Simulated Annealing')
    plt.xlabel('Iterações de melhoria')
    plt.ylabel('Custo')
    plt.grid(True)
    plt.tight_layout()

    cursor = mplcursors.cursor(line, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f"Custo: {history[int(sel.index)]}"))

    plt.show()


costByProjectJSON, professionalsCapacity = createCostByProjectJSON()
orderedCostByProjectJSON = orderCostByProjectJSONByCost(costByProjectJSON)
result = assignProfessionalToProject(orderedCostByProjectJSON, professionalsCapacity)
optimized_result, cost_history = simulated_annealing(result, costByProjectJSON, professionalsCapacity)
plotResult(optimized_result)
plot_cost_history(cost_history)