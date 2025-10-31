import json
import os
import time
from datetime import datetime

# ============================================================================
# SISTEMA DE RANKING - ARMAZENAMENTO E GESTÃO
# ============================================================================

RANKING_FILE_SOLO = 'ranking_solo.json'
RANKING_FILE_COMPETICAO = 'ranking_competicao.json'
MAX_RANKING_ENTRIES = 5

def _load_ranking(filename):
    """Carrega dados do ranking de um arquivo JSON."""
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []

def _save_ranking(filename, ranking_data):
    """Salva dados do ranking em um arquivo JSON."""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(ranking_data, f, indent=4, ensure_ascii=False)

def add_solo_score(nome_usuario, pontuacao, movimentos_totais, movimentos_corretos, tempo_total):
    """Adiciona pontuação do modo solo ao ranking com um ID único."""
    ranking = _load_ranking(RANKING_FILE_SOLO)
    ranking.append({
        'id': time.time(), # Adiciona um ID único
        'nome': nome_usuario,
        'pontuacao': pontuacao,
        'movimentos_totais': movimentos_totais,
        'movimentos_corretos': movimentos_corretos,
        'tempo_total_segundos': tempo_total,
        'taxa_acerto': round((movimentos_corretos / movimentos_totais * 100) if movimentos_totais > 0 else 0, 1),
        'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    })
    # O código original usava pontuação para ordenar, vamos manter
    ranking.sort(key=lambda x: x['pontuacao'], reverse=True)
    ranking = ranking[:MAX_RANKING_ENTRIES]
    _save_ranking(RANKING_FILE_SOLO, ranking)

def get_solo_ranking():
    """Retorna o ranking do modo solo."""
    return _load_ranking(RANKING_FILE_SOLO)

def add_competicao_score(nome_vencedor, pontuacao_vencedor, nome_perdedor, pontuacao_perdedor, tempo_total_segundos, pontuacao_j1, pontuacao_j2):
    """Adiciona resultado da competição ao ranking com um ID único."""
    ranking = _load_ranking(RANKING_FILE_COMPETICAO)
    ranking.append({
        'id': time.time(), # Adiciona um ID único
        'nome_vencedor': nome_vencedor,
        'pontuacao_vencedor': pontuacao_vencedor,
        'nome_perdedor': nome_perdedor,
        'pontuacao_perdedor': pontuacao_perdedor,
        'pontuacao_jogador1': pontuacao_j1,  # Adicionado para salvar pontos do J1
        'pontuacao_jogador2': pontuacao_j2,  # Adicionado para salvar pontos do J2
        'tempo_total_segundos': tempo_total_segundos,
        'diferenca': pontuacao_vencedor - pontuacao_perdedor,
        'data_hora': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    })
    # O código original ordenava por pontuação do vencedor (desc) e tempo total (asc)
    ranking.sort(key=lambda x: (x['pontuacao_vencedor'], -x['tempo_total_segundos']), reverse=True)
    ranking = ranking[:MAX_RANKING_ENTRIES]
    _save_ranking(RANKING_FILE_COMPETICAO, ranking)

def get_competicao_ranking():
    """Retorna o ranking do modo competição."""
    return _load_ranking(RANKING_FILE_COMPETICAO)

def clear_ranking(filename):
    """Apaga o arquivo de ranking especificado."""
    if os.path.exists(filename):
        try:
            os.remove(filename)
            print(f"Ranking '{filename}' foi limpo com sucesso.")
        except OSError as e:
            print(f"Erro ao limpar o ranking '{filename}': {e}")

def remove_ranking_entry(filename, entry_id):
    """Remove uma entrada específica do ranking pelo seu ID."""
    ranking_data = _load_ranking(filename)
    # Converte para string para garantir a comparação correta com os IDs salvos (que são float de time.time())
    entry_id = float(entry_id) 
    updated_ranking = [entry for entry in ranking_data if entry.get('id') != entry_id]
    _save_ranking(filename, updated_ranking)
    return updated_ranking

# Constantes para uso externo
RANKING_FILE_SOLO_CONST = RANKING_FILE_SOLO
RANKING_FILE_COMPETICAO_CONST = RANKING_FILE_COMPETICAO
