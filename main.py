import json
from collections import defaultdict

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

costByProjectJSON, professionalsCapacity = createCostByProjectJSON()
orderedCostByProjectJSON = orderCostByProjectJSONByCost(costByProjectJSON)
result = assignProfessionalToProject(orderedCostByProjectJSON, professionalsCapacity)

print(result)