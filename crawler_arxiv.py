"""Crawler educacional da listagem pública cs.AI do arXiv.

Instalação: pip install requests beautifulsoup4
Execução: python crawler_arxiv.py
"""
import csv
import re
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = 'https://arxiv.org/list/cs.AI/recent'
ARQUIVO = Path(__file__).resolve().parent / 'editais_extraidos.csv'
TOTAL_DESEJADO = 30
POR_PAGINA = 20
PAUSA_SEGUNDOS = 3
MAX_PAGINAS = 10
CAMPOS = ['id', 'titulo', 'autores', 'data_listagem', 'categorias', 'url']


def texto(elemento):
    """Extrai texto e normaliza espaços, sem falhar com tags ausentes."""
    return ' '.join(elemento.stripped_strings) if elemento else ''


def coletar_da_pagina(html):
    """Extrai publicações dos pares <dt>/<dd> do HTML do arXiv."""
    soup = BeautifulSoup(html, 'html.parser')
    resultado = []
    # A listagem é organizada em pares dt (ID e links) / dd (metadados).
    for lista in soup.select('dl'):
        data_atual = ''
        # O h3 anterior delimita o grupo de data na página.
        cabecalho = lista.find_previous('h3')
        if cabecalho:
            m = re.search(r'\b\d{1,2}\s+[A-Za-z]{3}\s+\d{4}\b', texto(cabecalho))
            if m:
                try:
                    data_atual = datetime.strptime(m.group(0), '%d %b %Y').strftime('%Y-%m-%d')
                except ValueError:
                    pass

        # recursive=False previne capturar dd/dt aninhados por engano.
        termos = lista.find_all(['dt', 'dd'], recursive=False)
        for i, termo in enumerate(termos):
            if termo.name != 'dt':
                continue
            link = termo.select_one('a[href^="/abs/"]')
            if not link:
                continue
            caminho = link.get('href', '')
            identificador = caminho.split('/abs/')[-1].strip('/')
            if not re.fullmatch(r'\d{4}\.\d{4,5}(?:v\d+)?', identificador):
                continue
            # O dd correspondente normalmente vem imediatamente depois do dt.
            proximo = termos[i + 1] if i + 1 < len(termos) else None
            if proximo is None or proximo.name != 'dd':
                continue
            titulo = texto(proximo.select_one('.list-title'))
            titulo = re.sub(r'^Title:\s*', '', titulo, flags=re.I).strip()
            autores = texto(proximo.select_one('.list-authors'))
            autores = re.sub(r'^Authors?:\s*', '', autores, flags=re.I).strip()
            categorias = texto(proximo.select_one('.list-subjects'))
            categorias = re.sub(r'^Subjects?:\s*', '', categorias, flags=re.I).strip()
            if not titulo:  # Não grava um registro incompleto sem título.
                continue
            resultado.append({
                'id': identificador, 'titulo': titulo,
                'autores': autores, 'data_listagem': data_atual,
                'categorias': categorias, 'url': urljoin(BASE_URL, caminho),
            })
    return resultado


def executar():
    sessao = requests.Session()
    sessao.headers.update({'User-Agent': 'CrawlerAcademico/1.0 (uso educacional; contato via professor da disciplina)'})
    registros = []
    ids = set()
    for pagina in range(MAX_PAGINAS):
        parametros = {'skip': pagina * POR_PAGINA, 'show': POR_PAGINA}
        try:
            resposta = sessao.get(BASE_URL, params=parametros, timeout=30)
            resposta.raise_for_status()
            itens = coletar_da_pagina(resposta.text)
        except requests.RequestException as erro:
            print(f'Falha de rede na página {pagina + 1}: {erro}')
            break
        print(f'Página {pagina + 1}: {len(itens)} publicações encontradas ({resposta.url})')
        if not itens:
            break
        adicionados = 0
        for item in itens:
            if item['id'] not in ids:
                ids.add(item['id'])
                registros.append(item)
                adicionados += 1
            if len(registros) >= TOTAL_DESEJADO:
                break
        if len(registros) >= TOTAL_DESEJADO or adicionados == 0:
            break
        time.sleep(PAUSA_SEGUNDOS)

    if not registros:
        print('Nenhum registro coletado; o CSV existente foi preservado.')
        return
    with ARQUIVO.open('w', encoding='utf-8-sig', newline='') as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=CAMPOS, delimiter=';')
        escritor.writeheader()
        escritor.writerows(registros)
    print(f'{len(registros)} registros gravados em {ARQUIVO}')
    if len(registros) < TOTAL_DESEJADO:
        print(f'Aviso: foram coletados menos que os {TOTAL_DESEJADO} registros desejados.')


if __name__ == '__main__':
    executar()
