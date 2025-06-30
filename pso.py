import json
import random
import numpy as np
from collections import defaultdict
import matplotlib.pyplot as plt
import mplcursors

# --- Carregar dados ---
jsonFile = open("data_mock_1000.json", "r", encoding="utf-8")
data = json.loads(jsonFile.read())["data"]
jsonFile.close()

# --- Processar dados do JSON ---
agent_names = list(data.keys())
project_ids = set()

agent_capacity = []
for agent in agent_names:
    agent_info = data[agent]
    agent_capacity.append(agent_info["capacity"])
    for proj in agent_info["resourceByProject"]:
        project_ids.add(proj)

project_ids = sorted(list(project_ids), key=int)
project_index = {pid: idx for idx, pid in enumerate(project_ids)}
n_projects = len(project_ids)
n_agents = len(agent_names)
agent_name_to_idx = {name: idx for idx, name in enumerate(agent_names)}

cost_matrix = [[float("inf")] * n_projects for _ in range(n_agents)]
for i, agent in enumerate(agent_names):
    for proj, workload in data[agent]["resourceByProject"].items():
        j = project_index[proj]
        cost_matrix[i][j] = workload

# --- Funções do Algoritmo Guloso ---
def createCostByProjectJSON_original():
    peopleData = data
    projectsCost = defaultdict(list)
    professionalsCapacity = {}
    for personName in peopleData.keys():
        professionalsCapacity[personName] = data[personName]["capacity"]
        personData = peopleData[personName]
        for project in personData["resourceByProject"].keys():
            projectsCost[project].append([personName, personData["resourceByProject"][project]])
    return projectsCost, professionalsCapacity

def orderCostByProjectJSONByCost(costByProjectJSON):
    for project in costByProjectJSON:
        costByProjectJSON[project].sort(key=lambda x: x[1])
    return costByProjectJSON

def assignProfessionalToProject(orderedCostByProjectJSON, professionalsCapacity_copy):
    assignedProfessionalToProject = {}
    current_professionals_capacity = professionalsCapacity_copy.copy()
    for projectName in orderedCostByProjectJSON.keys():
        assigned = False
        for projectCosts in orderedCostByProjectJSON[projectName]:
            professionalName = projectCosts[0]
            workload = projectCosts[1]
            if current_professionals_capacity[professionalName] >= workload:
                assignedProfessionalToProject[projectName] = professionalName
                current_professionals_capacity[professionalName] -= workload
                assigned = True
                break
        if not assigned:
            pass
    return assignedProfessionalToProject

# --- Função de avaliação ---
def evaluate(solution):
    total_cost = 0
    loads = [0] * n_agents
    for task_idx, agent_idx in enumerate(solution):
        workload = cost_matrix[agent_idx][task_idx]
        if workload == float("inf"):
            total_cost += 1e9
        else:
            total_cost += workload
            loads[agent_idx] += workload
    penalty = 0
    for i in range(n_agents):
        if loads[i] > agent_capacity[i]:
            penalty += (loads[i] - agent_capacity[i]) * 1000
    return total_cost + penalty

# --- Inicialização das partículas ---
def initialize_particles(num_particles, greedy_solution_map):
    particles = []
    initial_greedy_particle = [0] * n_projects
    for project_id_str, agent_name in greedy_solution_map.items():
        project_idx = project_index[project_id_str]
        agent_idx = agent_name_to_idx[agent_name]
        initial_greedy_particle[project_idx] = agent_idx
    particles.append(initial_greedy_particle)
    for _ in range(num_particles - 1):
        particle = []
        for task_idx in range(n_projects):
            valid_agents = [i for i in range(n_agents) if cost_matrix[i][task_idx] != float("inf")]
            if valid_agents:
                if random.random() < 0.5:
                    particle.append(random.choice(valid_agents))
                else:
                    greedy_agent_for_task = initial_greedy_particle[task_idx]
                    if greedy_agent_for_task in valid_agents:
                        particle.append(greedy_agent_for_task)
                    else:
                        particle.append(random.choice(valid_agents))
            else:
                particle.append(0)
        particles.append(particle)
    return particles

# --- PSO discreto ---
def discrete_pso_gap_with_coefficients(num_particles=50, num_iterations=200):
    projectsCost, professionalsCapacity_initial = createCostByProjectJSON_original()
    orderedCostByProjectJSON = orderCostByProjectJSONByCost(projectsCost)
    greedy_solution_map = assignProfessionalToProject(orderedCostByProjectJSON, professionalsCapacity_initial.copy())
    c1, c2 = 1.5, 2
    w = 0.4
    particles = initialize_particles(num_particles, greedy_solution_map)
    personal_best = [p[:] for p in particles]
    personal_best_scores = [evaluate(p) for p in particles]
    global_best = personal_best[np.argmin(personal_best_scores)][:]
    global_best_score = min(personal_best_scores)
    cost_history = [global_best_score]
    for iteration in range(num_iterations):

        for i, particle in enumerate(particles):
            score = evaluate(particle)
            if score < personal_best_scores[i]:
                personal_best[i] = particle[:]
                personal_best_scores[i] = score
        best_idx = np.argmin(personal_best_scores)
        if personal_best_scores[best_idx] < global_best_score:
            global_best = personal_best[best_idx][:]
            global_best_score = personal_best_scores[best_idx]
            cost_history.append(global_best_score)
            print(global_best_score)
        for i in range(num_particles):
            new_particle = []
            for j in range(n_projects):
                r1 = random.uniform(0, 1)
                r2 = random.uniform(0, 1)
                attraction_scores = defaultdict(float)
                attraction_scores[particles[i][j]] += w
                attraction_scores[personal_best[i][j]] += c1 * r1
                attraction_scores[global_best[j]] += c2 * r2
                valid_agents_for_j = [k for k in range(n_agents) if cost_matrix[k][j] != float("inf")]
                if not valid_agents_for_j:
                    new_particle.append(0)
                    continue
                filtered_attraction_scores = {
                    agent: score for agent, score in attraction_scores.items() if agent in valid_agents_for_j
                }
                if not filtered_attraction_scores or sum(filtered_attraction_scores.values()) == 0:
                    chosen = random.choice(valid_agents_for_j)
                elif random.random() < 0.05:
                    chosen = random.choice(valid_agents_for_j)
                else:
                    total = sum(filtered_attraction_scores.values())
                    probs = [score / total for score in filtered_attraction_scores.values()]
                    chosen = random.choices(list(filtered_attraction_scores), weights=probs, k=1)[0]
                new_particle.append(chosen)
            particles[i] = new_particle
    return global_best, global_best_score, cost_history

# --- Plotar evolução ---
def plot_cost_history(history):
    plt.figure(figsize=(12, 6))
    line, = plt.plot(history, marker='o', linestyle='-', color='b', label='Melhor Custo Encontrado')
    plt.title('Evolução do Custo no PSO Discreto com Inicialização Gulosa', fontsize=16)
    plt.xlabel('Iterações', fontsize=14)
    plt.ylabel('Custo', fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(fontsize=12)
    plt.tight_layout()
    mplcursors.cursor(line, hover=True).connect(
        "add", lambda sel: sel.annotation.set_text(f"Iteração: {int(sel.index)}\nCusto: {history[int(sel.index)]:.2f}")
    )
    plt.show()

# --- Executar ---
best_solution_coeffs, best_cost_coeffs, cost_history_coeffs = discrete_pso_gap_with_coefficients()
print(f"Melhor custo final (com coeficientes e inicialização gulosa): {best_cost_coeffs}")
print(f"Solução (primeiros 10 projetos): {best_solution_coeffs[:10]}")
plot_cost_history(cost_history_coeffs)
