import json
from collections import defaultdict
import matplotlib.pyplot as plt

jsonFile = open("data.json", "r", encoding="utf-8")
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

costByProjectJSON, professionalsCapacity = createCostByProjectJSON()
orderedCostByProjectJSON = orderCostByProjectJSONByCost(costByProjectJSON)
result = assignProfessionalToProject(orderedCostByProjectJSON, professionalsCapacity)
plotResult(result)


