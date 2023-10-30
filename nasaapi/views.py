from django.shortcuts import render
from django.http import JsonResponse
import json

import requests

API_KEY = '0wAntSmVVl7GRk0fXP86yc3o2SAPaQc6sGLV5DIi'

START_DATE = '2023-10-29'  # A data de hoje como exemplo
END_DATE = '2023-11-05'  # 7 dias após a data de início


def index(request):
    info_rover = obter_info_rover_curiosity()
    sol_atual = obter_sol_mais_recente()
    error_message = None
    info_fotos_sol = None

    if 'sol' in request.GET:
        sol = request.GET['sol']

        if not sol.isdigit():
            error_message = "Use como base para pesquisa a quantidade de sois que o rover está em Marte. Apenas números dentro deste valor vão funcionar."
        else:
            sol = int(sol)
            if sol > int(info_rover['rover']['max_sol']):
                error_message = "O valor inserido é maior do que a quantidade máxima de sois disponíveis."

        if not error_message:
            info_fotos_sol = obter_fotos_rover_sol(sol=sol)
    else:
        info_fotos_sol = obter_fotos_rover_sol(sol=2000)

    info_asteroides = asteroides_proximos_terra()
    asteroid_labels = []
    asteroid_miss_distances = []
    asteroid_sizes = []

    if info_asteroides:
        for asteroide in info_asteroides['near_earth_objects']['2023-10-30']:
            asteroid_labels.append(asteroide['name'])
            asteroid_miss_distances.append(
                float(asteroide['close_approach_data'][0]['miss_distance']['kilometers']))
            asteroid_sizes.append(
                float(asteroide['estimated_diameter']['meters']['estimated_diameter_max']))

    asteroid_sizes_json = json.dumps(asteroid_sizes)
    asteroid_miss_distances_json = json.dumps(asteroid_miss_distances)
    asteroid_labels_json = json.dumps(asteroid_labels)
    url_imagem_do_dia = obter_imagem_do_dia()
    return render(request, 'index.html', {
        "error_message": error_message,
        "url_imagem_do_dia": url_imagem_do_dia,
        "info_asteroides": info_asteroides,
        "info_fotos_sol": info_fotos_sol,
        "sol_atual": sol_atual,
        "info_rover": info_rover,
        "asteroid_labels": asteroid_labels_json,
        "asteroid_miss_distances": asteroid_miss_distances_json,
        "asteroid_sizes_json": asteroid_sizes_json
    })


def obter_imagem_do_dia():
    url = "https://api.nasa.gov/planetary/apod"
    params = {
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data['url']  # Isso retornará a URL direta da imagem do dia
    else:
        print("Erro ao recuperar a imagem:", response.status_code)
        return None


def asteroides_proximos_terra():
    url = f"https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        "start_date": START_DATE,
        "end_date": END_DATE,
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        return data  # Isso retornará informações sobre os asteroides próximos à Terra
    else:
        print("Erro ao recuperar os asteroides:", response.status_code)
        return None


def obter_fotos_rover_sol(sol):
    url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/photos"
    params = {
        "sol": sol,
        "api_key": API_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()

        # Atribuindo índice às fotos
        photos_with_index = []
        for index, photo in enumerate(data['photos']):
            photo['index'] = index + 1
            photos_with_index.append(photo)

        # Retorna as informações sobre as fotos do rover em Marte com índices
        return photos_with_index
    else:
        print("Erro ao recuperar fotos do rover:", response.status_code)
        return None


def obter_info_rover_curiosity():
    url = "https://api.nasa.gov/mars-photos/api/v1/rovers/curiosity/"
    params = {"api_key": API_KEY}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Verifica se a resposta tem status 200
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("Erro ao recuperar informações do rover Curiosity:", e)
        return None


def obter_sol_mais_recente():
    info_rover = obter_info_rover_curiosity()
    if info_rover:
        max_sol = info_rover['rover']['max_sol']
        return max_sol
    else:
        return None


def asteroid_chart_data(asteroides):
    chart_data = []

    for asteroide in asteroides:
        chart_data.append({
            'name': asteroide['name'],
            'miss_distance': float(asteroide['close_approach_data'][0]['miss_distance']['kilometers']),
            'asteroid_size': float(asteroide['estimated_diameter']['meters']['estimated_diameter_max'])
        })

    return JsonResponse(chart_data, safe=False)
