import json
import random


def gerar_mock(num_profissionais=100, num_projetos_totais=100):
    mock = {"data": {}}

    for i in range(1, num_profissionais + 1):
        nome = f"Pessoa {i}"
        capacidade = random.randint(50, 200)

        # Escolher entre 1 e 5 projetos únicos para esta pessoa
        projetos_ids = random.sample([str(j) for j in range(1, num_projetos_totais + 1)], random.randint(1, 5))

        resource_by_project = {
            projeto_id: random.randint(10, 150) for projeto_id in projetos_ids
        }

        mock["data"][nome] = {
            "capacity": capacidade,
            "resourceByProject": resource_by_project
        }

    return mock


# Gerar o mock e salvar em um arquivo
mock_data = gerar_mock()

with open("data_mock_1000.json", "w", encoding="utf-8") as f:
    json.dump(mock_data, f, indent=2, ensure_ascii=False)

print("Mock com 1000 profissionais gerado com sucesso.")
