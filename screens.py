import cv2
import numpy as np
import time
from tkinter import Tk, filedialog
from ui_utils import show_fullscreen, draw_filled_transparent_rect, putText_outline, draw_button, draw_gradient_rect, draw_label_box
from ranking_manager import get_solo_ranking, get_competicao_ranking, remove_ranking_entry, add_solo_score, add_competicao_score, RANKING_FILE_SOLO_CONST, RANKING_FILE_COMPETICAO_CONST

# Variável global para comunicação entre o callback do mouse e o loop principal
click_info = {'clicked': False, 'file': None, 'id': None}

# ============================================================================
# TELAS DE RANKING E CONFIRMAÇÃO
# ============================================================================
def handle_mouse_click_ranking(event, x, y, flags, param):
    """Callback para detectar cliques nos botões de exclusão do ranking."""
    global click_info
    if event == cv2.EVENT_LBUTTONDOWN:
        buttons = param['buttons']
        filename = param['file']
        for rect, entry_id in buttons:
            x1, y1, x2, y2 = rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                click_info['clicked'] = True
                click_info['file'] = filename
                click_info['id'] = entry_id
                break

def show_confirmation_screen(window_title, message):
    """Mostra uma tela de confirmação e aguarda a resposta do usuário (S/N)."""
    confirm_window_name = f"Confirmar - {window_title}"
    
    # --- CORREÇÃO: Lógica para quebrar a linha da mensagem ---
    lines = []
    if message == "Tem certeza que deseja excluir esta entrada do ranking?":
        lines.append("Tem certeza que deseja excluir")
        lines.append("esta entrada do ranking?")
    else:
        # Caso seja outra mensagem, apenas adiciona
        lines.append(message) 

    # Define a altura da tela dinamicamente
    base_height = 300
    if len(lines) > 1:
        base_height = 320 # Aumenta a altura se tiver mais de 1 linha
    
    while True:
        tela = np.ones((base_height, 700, 3), dtype=np.uint8) * 24
        draw_filled_transparent_rect(tela, (0, 0), (700, 80), (80, 40, 40), 0.9)
        putText_outline(tela, "CONFIRMACAO", (40, 55), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 100, 100), 2)
        
        # --- CORREÇÃO: Desenha as linhas ---
        y_text = 130
        for line in lines:
            putText_outline(tela, line, (40, y_text), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2)
            y_text += 35 # Incrementa o Y para a próxima linha
        
        # --- CORREÇÃO: Ajusta a posição Y dos botões ---
        y_buttons = y_text + 10 # Coloca os botões abaixo do texto
        
        draw_button(tela, (100, y_buttons, 300, y_buttons + 50), (0, 180, 0), "[S] Sim", label_color=(20, 22, 25))
        draw_button(tela, (400, y_buttons, 600, y_buttons + 50), (200, 50, 50), "[N] Nao", label_color=(255, 255, 255))
        # --- FIM DA CORREÇÃO ---

        show_fullscreen(confirm_window_name, tela)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('s') or key == ord('S'):
            cv2.destroyWindow(confirm_window_name)
            return True
        elif key == ord('n') or key == ord('N') or key == 27: # ESC
            cv2.destroyWindow(confirm_window_name)
            return False

def show_solo_ranking():
    """Exibe ranking detalhado do modo solo com a coluna de pontuação."""
    global click_info
    click_info = {'clicked': False, 'file': None, 'id': None}
    ranking_data = get_solo_ranking()
    window_name = "Ranking Solo"
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    y_offset = 160
    x_base = 40

    while True:
        delete_buttons = []
        tela = np.ones((700, 1100, 3), dtype=np.uint8) * 20
        draw_gradient_rect(tela, (0, 0), (1100, 120), (40, 60, 80), (20, 30, 40))
        putText_outline(tela, "RANKING - MODO SOLO", (40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (0, 255, 220), 4)
        putText_outline(tela, "TOP 5 MELHORES PONTUACOES", (40, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2)
        cv2.rectangle(tela, (40, 650), (1060, 680), (50, 50, 50), -1)
        putText_outline(tela, "Pressione ESC para voltar", (60, 670), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        # Headers com espaçamento ajustado
        headers = [
            ("POS", 0, 60), ("JOGADOR", 80, 200), ("PONTOS", 300, 100), ("MOV.", 420, 100),
            ("TEMPO", 540, 100), ("DATA", 660, 150), ("EXCLUIR", 830, 120)
        ]
        
        # Coordenadas X para o texto dos dados (para alinhar com os headers)
        x_pos = x_base + 10
        x_jogador = x_base + 90
        x_pontos = x_base + 310
        x_mov = x_base + 430
        x_tempo = x_base + 550
        x_data = x_base + 670
        x_excluir_btn = x_base + 830
        
        for header, x_offset_h, width in headers:
            cv2.rectangle(tela, (x_base + x_offset_h, y_offset - 35), (x_base + x_offset_h + width, y_offset + 5), (60, 60, 60), -1)
            # Centraliza o texto do header (opcional, mas +10 é o padding esquerdo)
            putText_outline(tela, header, (x_base + x_offset_h + 10, y_offset - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            
        y_pos = y_offset + 20
        
        for i, entry in enumerate(ranking_data):
            pos = i + 1
            color = (0, 255, 220) if pos == 1 else (255, 255, 255)
            bg_color = (20, 20, 20) if pos % 2 == 0 else (30, 30, 30)
            
            draw_filled_transparent_rect(tela, (x_base, y_pos - 15), (x_base + 960, y_pos + 25), bg_color, 0.5)
            
            # Desenha os dados usando as coordenadas X definidas
            putText_outline(tela, str(pos), (x_pos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, entry['nome'], (x_jogador, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, str(entry['pontuacao']), (x_pontos, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, f"{entry['movimentos_corretos']}/{entry['movimentos_totais']}", (x_mov, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, f"{entry['tempo_total_segundos']:.0f}s", (x_tempo, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, entry['data_hora'].split(' ')[0], (x_data, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Botão de Excluir
            btn_rect = (x_excluir_btn, y_pos - 10, x_excluir_btn + 100, y_pos + 15)
            draw_button(tela, btn_rect, (50, 50, 200), "X", label_color=(255, 255, 255), scale=0.5, thickness=1)
            delete_buttons.append((btn_rect, entry['id']))
            
            y_pos += 40
            
        cv2.setMouseCallback(window_name, handle_mouse_click_ranking, {'buttons': delete_buttons, 'file': RANKING_FILE_SOLO_CONST})
        show_fullscreen(window_name, tela)
        
        if click_info['clicked']:
            if show_confirmation_screen("Excluir Entrada", "Tem certeza que deseja excluir esta entrada do ranking?"):
                ranking_data = remove_ranking_entry(click_info['file'], click_info['id'])
                click_info = {'clicked': False, 'file': None, 'id': None}
                # Recarrega a tela com os novos dados
                cv2.destroyWindow(window_name)
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                continue
            click_info = {'clicked': False, 'file': None, 'id': None}

        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC
            cv2.destroyWindow(window_name)
            break

def show_competicao_ranking():
    """Exibe ranking detalhado do modo competição."""
    global click_info
    click_info = {'clicked': False, 'file': None, 'id': None}
    ranking_data = get_competicao_ranking()
    window_name = "Ranking Competicao"
    
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    y_offset = 160
    x_base = 40

    while True:
        delete_buttons = []
        tela = np.ones((700, 1300, 3), dtype=np.uint8) * 20
        draw_gradient_rect(tela, (0, 0), (1300, 120), (80, 40, 80), (40, 20, 40))
        putText_outline(tela, "RANKING - MODO COMPETICAO", (40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.5, (255, 100, 255), 4)
        putText_outline(tela, "TOP 5 MELHORES PONTUACOES DE VITORIA", (40, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (180, 180, 180), 2)
        cv2.rectangle(tela, (40, 650), (1260, 680), (50, 50, 50), -1)
        putText_outline(tela, "Pressione ESC para voltar", (60, 670), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        
        headers = [
            ("POS", 0, 60), ("VENCEDOR", 80, 200), ("PONTOS V.", 300, 100), ("PERDEDOR", 420, 200),
            ("PONTOS P.", 640, 100), ("TEMPO", 760, 100), ("DIFERENCA", 880, 120), ("DATA", 1020, 120), ("EXCLUIR", 1160, 100)
        ]
        
        for header, x_offset_h, width in headers:
            cv2.rectangle(tela, (x_base + x_offset_h, y_offset - 35), (x_base + x_offset_h + width, y_offset + 5), (60, 60, 60), -1)
            putText_outline(tela, header, (x_base + x_offset_h + 10, y_offset - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)
            
        y_pos = y_offset + 20
        
        for i, entry in enumerate(ranking_data):
            pos = i + 1
            color = (255, 100, 255) if pos == 1 else (255, 255, 255)
            bg_color = (20, 20, 20) if pos % 2 == 0 else (30, 30, 30)
            
            draw_filled_transparent_rect(tela, (x_base, y_pos - 15), (x_base + 1220, y_pos + 25), bg_color, 0.5)
            
            putText_outline(tela, str(pos), (x_base + 10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, entry['nome_vencedor'], (x_base + 90, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, str(entry['pontuacao_vencedor']), (x_base + 320, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, entry['nome_perdedor'], (x_base + 430, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            putText_outline(tela, str(entry['pontuacao_perdedor']), (x_base + 660, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
            putText_outline(tela, f"{entry['tempo_total_segundos']:.0f}s", (x_base + 780, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, str(entry['diferenca']), (x_base + 900, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            putText_outline(tela, entry['data_hora'].split(' ')[0], (x_base + 1025, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            # Botão de Excluir
            btn_rect = (x_base + 1160, y_pos - 10, x_base + 1260, y_pos + 15)
            draw_button(tela, btn_rect, (50, 50, 200), "X", label_color=(255, 255, 255), scale=0.5, thickness=1)
            delete_buttons.append((btn_rect, entry['id']))
            
            y_pos += 40
            
        cv2.setMouseCallback(window_name, handle_mouse_click_ranking, {'buttons': delete_buttons, 'file': RANKING_FILE_COMPETICAO_CONST})
        show_fullscreen(window_name, tela)
        
        if click_info['clicked']:
            if show_confirmation_screen("Excluir Entrada", "Tem certeza que deseja excluir esta entrada do ranking?"):
                ranking_data = remove_ranking_entry(click_info['file'], click_info['id'])
                click_info = {'clicked': False, 'file': None, 'id': None}
                # Recarrega a tela com os novos dados
                cv2.destroyWindow(window_name)
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                continue
            click_info = {'clicked': False, 'file': None, 'id': None}

        key = cv2.waitKey(1) & 0xFF
        if key == 27: # ESC
            cv2.destroyWindow(window_name)
            break

# ============================================================================
# TELAS DE INPUT E SELEÇÃO
# ============================================================================

def obter_nome_estilizado(prompt_text, window_title, default_name, max_chars=20):
    """Tela de input de texto estilizada com OpenCv."""
    nome = ""
    
    cv2.namedWindow(window_title, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        tela = np.ones((400, 700, 3), dtype=np.uint8) * 24
        draw_filled_transparent_rect(tela, (0, 0), (700, 80), (20, 22, 25), 0.9)
        cv2.putText(tela, window_title, (40, 55), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 220), 2, cv2.LINE_AA)
        cv2.putText(tela, prompt_text, (40, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2, cv2.LINE_AA)
        
        input_box_rect = (40, 170, 660, 230)
        cv2.rectangle(tela, (input_box_rect[0], input_box_rect[1]), (input_box_rect[2], input_box_rect[3]), (45, 45, 45), -1)
        cv2.rectangle(tela, (input_box_rect[0], input_box_rect[1]), (input_box_rect[2], input_box_rect[3]), (150, 150, 150), 2)
        
        (tw, th), _ = cv2.getTextSize(nome, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3)
        text_y = input_box_rect[1] + (input_box_rect[3] - input_box_rect[1] + th) // 2
        cursor = "|" if int(time.time() * 2) % 2 == 0 else ""
        cv2.putText(tela, nome + cursor, (input_box_rect[0] + 15, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 3, cv2.LINE_AA)
        
        draw_label_box(tela, "Pressione ENTER para confirmar ou ESC para sair", (40, 350), font=cv2.FONT_HERSHEY_PLAIN, scale=1.2)
        
        show_fullscreen(window_title, tela)
        
        key = cv2.waitKey(50)
        if key == 13: # ENTER
            cv2.destroyWindow(window_title)
            return nome.strip() if nome.strip() else default_name
        elif key == 27: # ESC
            cv2.destroyWindow(window_title)
            return None
        elif key == 8: # BACKSPACE
            nome = nome[:-1]
        elif key != -1 and len(nome) < max_chars and 32 <= key <= 126: # Caractere imprimível
            nome += chr(key)

def obter_nome_usuario():
    return obter_nome_estilizado("Digite seu nome:", "Modo Solo", "Jogador")

def obter_nomes_jogadores():
    nome1 = obter_nome_estilizado("Digite o nome do JOGADOR 1:", "Modo Competicao", "Jogador1")
    if nome1 is None: return None, None
    nome2 = obter_nome_estilizado("Digite o nome do JOGADOR 2:", "Modo Competicao", "Jogador2")
    if nome2 is None: return nome1, None
    return nome1, nome2

def escolher_modo():
    """Menu principal com as opções de ranking adicionadas."""
    window_name = "Selecao de Modo"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        tela = np.ones((500, 720, 3), dtype=np.uint8) * 24
        draw_filled_transparent_rect(tela, (0, 0), (720, 100), (20, 22, 25), 0.9)
        cv2.putText(tela, "CONTADOR DE POLICHINELOS", (40, 60), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 220), 2, cv2.LINE_AA)
        cv2.putText(tela, "Escolha o modo de uso:", (40, 92), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (230, 230, 230), 2, cv2.LINE_AA)
        
        draw_button(tela, (80, 120, 640, 170), (80, 170, 255), "[1] MODO SOLO", label_color=(20, 22, 25))
        draw_button(tela, (80, 180, 640, 230), (255, 140, 80), "[2] MODO COMPETICAO", label_color=(20, 22, 25))
        draw_button(tela, (80, 240, 640, 290), (0, 210, 180), "[3] ANALISAR VIDEO", label_color=(20, 22, 25))
        draw_button(tela, (80, 300, 640, 350), (200, 200, 0), "[4] RANKING SOLO", label_color=(20, 22, 25))
        draw_button(tela, (80, 360, 640, 410), (0, 200, 200), "[5] RANKING COMPETICAO", label_color=(20, 22, 25))
        
        draw_label_box(tela, "Pressione 1-5 para selecionar ou ESC para sair", (40, 450), font=cv2.FONT_HERSHEY_PLAIN, scale=1.2)
        
        show_fullscreen(window_name, tela)
        
        key = cv2.waitKey(1)
        if key == ord("1"): cv2.destroyWindow(window_name); return 0
        elif key == ord("2"): cv2.destroyWindow(window_name); return 1
        elif key == ord("3"): cv2.destroyWindow(window_name); return 2
        elif key == ord("4"): cv2.destroyWindow(window_name); return 3
        elif key == ord("5"): cv2.destroyWindow(window_name); return 4
        elif key == 27: cv2.destroyWindow(window_name); return None

def escolher_meta():
    window_name = "Escolha da Meta"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        tela = np.ones((500, 650, 3), dtype=np.uint8) * 24
        draw_filled_transparent_rect(tela, (0, 0), (650, 100), (20, 22, 25), 0.9)
        cv2.putText(tela, "ESCOLHA A META", (50, 65), cv2.FONT_HERSHEY_DUPLEX, 1.2, (0, 255, 220), 3, cv2.LINE_AA)
        draw_label_box(tela, "Pressione 1-4 para selecionar", (50, 130), scale=1.0, padding=8, alpha=0.8, text_color=(200, 200, 200))
        
        metas = [10, 20, 30, 50]
        descricoes = ["Iniciante", "Intermediario", "Avancado", "Expert"]
        cores = [(100, 255, 100), (80, 170, 255), (255, 140, 80), (255, 80, 120)]
        y_pos = 180
        
        for i, (meta, desc, cor) in enumerate(zip(metas, descricoes, cores)):
            draw_button(tela, (50, y_pos, 600, y_pos + 55), cor, f"[{i+1}] {meta} Polichinelos - {desc}", label_color=(20, 22, 25), scale=0.85)
            y_pos += 75
            
        show_fullscreen(window_name, tela)
        
        key = cv2.waitKey(1)
        if key in [ord('1'), ord('2'), ord('3'), ord('4')]:
            cv2.destroyWindow(window_name)
            return metas[key - ord('1')]
        elif key == 27:
            cv2.destroyWindow(window_name)
            return None

def escolher_video():
    """Abre a caixa de diálogo para selecionar um arquivo de vídeo."""
    Tk().withdraw()
    video_path = filedialog.askopenfilename(title="Selecione o vídeo para análise", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
    return video_path

# ============================================================================
# TELAS DE RESULTADO
# ============================================================================

def mostrar_resultado_competicao(competition, counter1, counter2):
    """Tela de resultado da competição com salvamento no ranking."""
    tempo_total = int(competition.tempo_final) if competition.tempo_final else int(time.time() - competition.tempo_inicio)
    
    # Só salva no ranking se houver um vencedor
    if competition.vencedor:
        vencedor_nome = competition.jogador1 if competition.vencedor == 1 else competition.jogador2
        perdedor_nome = competition.jogador2 if competition.vencedor == 1 else competition.jogador1
        vencedor_pts = counter1 if competition.vencedor == 1 else counter2
        perdedor_pts = counter2 if competition.vencedor == 1 else counter1
        # Chamada corrigida para incluir os pontos de J1 (counter1) e J2 (counter2)
        add_competicao_score(vencedor_nome, vencedor_pts, perdedor_nome, perdedor_pts, tempo_total, counter1, counter2)
    
    # Lógica de pontuação extra (50 pts por polichinelo + 200 pts de bônus para o vencedor)
    pontuacao1, pontuacao2 = counter1 * 50, counter2 * 50
    status1, status2 = "EM ANDAMENTO", "EM ANDAMENTO"
    if competition.vencedor == 1:
        pontuacao1 += 200; status1, status2 = "VENCEDOR", "2° LUGAR"
    elif competition.vencedor == 2:
        pontuacao2 += 200; status1, status2 = "2° LUGAR", "VENCEDOR"

    velocidade1 = (counter1 / tempo_total * 60) if tempo_total > 0 else 0
    velocidade2 = (counter2 / tempo_total * 60) if tempo_total > 0 else 0
    progresso1 = min((counter1 / competition.meta_polichinelos) * 100, 100)
    progresso2 = min((counter2 / competition.meta_polichinelos) * 100, 100)
    
    window_name = "Resultado da Competicao"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        tela = np.ones((750, 1000, 3), dtype=np.uint8) * 24
        draw_filled_transparent_rect(tela, (0, 0), (1000, 120), (20, 22, 25), 0.9)
        cv2.putText(tela, "RESULTADO DETALHADO DA COMPETICAO", (50, 70), cv2.FONT_HERSHEY_DUPLEX, 1.3, (0, 255, 220), 3)
        cv2.putText(tela, f"Duracao Total: {tempo_total//60}:{tempo_total%60:02d}", (50, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
        
        y_start, col1_x, col2_x = 180, 80, 520
        
        # --- Jogador 1 ---
        cv2.putText(tela, f"{competition.jogador1.upper()}", (col1_x, y_start), cv2.FONT_HERSHEY_DUPLEX, 1.2, (80, 170, 255), 3)
        cv2.putText(tela, status1, (col1_x, y_start + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 170, 255), 2)
        stats1 = [ 
            f"Pontuacao Final: {pontuacao1} pts", 
            f"Polichinelos: {counter1}/{competition.meta_polichinelos}", 
            f"Velocidade: {velocidade1:.1f}/min", 
            f"Progresso: {progresso1:.1f}%", 
            f"Meta Atingida: {'SIM' if counter1 >= competition.meta_polichinelos else 'NAO'}" 
        ]
        y_pos = y_start + 80
        for i, stat in enumerate(stats1):
            color = (0, 255, 100) if i == 0 and competition.vencedor == 1 else (230, 230, 230)
            cv2.putText(tela, stat, (col1_x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2); y_pos += 40
        
        # Barra de Progresso 1
        barra_width, barra_height, barra_y = 300, 25, y_pos + 10
        cv2.rectangle(tela, (col1_x, barra_y), (col1_x + barra_width, barra_y + barra_height), (50, 50, 50), -1)
        cv2.rectangle(tela, (col1_x, barra_y), (col1_x + int(barra_width * progresso1/100), barra_y + barra_height), (80, 170, 255), -1)
        cv2.putText(tela, f"{progresso1:.0f}%", (col1_x + barra_width + 10, barra_y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # --- Jogador 2 ---
        cv2.putText(tela, f"{competition.jogador2.upper()}", (col2_x, y_start), cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 140, 80), 3)
        cv2.putText(tela, status2, (col2_x, y_start + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 140, 80), 2)
        stats2 = [ 
            f"Pontuacao Final: {pontuacao2} pts", 
            f"Polichinelos: {counter2}/{competition.meta_polichinelos}", 
            f"Velocidade: {velocidade2:.1f}/min", 
            f"Progresso: {progresso2:.1f}%", 
            f"Meta Atingida: {'SIM' if counter2 >= competition.meta_polichinelos else 'NAO'}" 
        ]
        y_pos = y_start + 80
        for i, stat in enumerate(stats2):
            color = (0, 255, 100) if i == 0 and competition.vencedor == 2 else (230, 230, 230)
            cv2.putText(tela, stat, (col2_x, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2); y_pos += 40
            
        # Barra de Progresso 2
        cv2.rectangle(tela, (col2_x, barra_y), (col2_x + barra_width, barra_y + barra_height), (50, 50, 50), -1)
        cv2.rectangle(tela, (col2_x, barra_y), (col2_x + int(barra_width * progresso2/100), barra_y + barra_height), (255, 140, 80), -1)
        cv2.putText(tela, f"{progresso2:.0f}%", (col2_x + barra_width + 10, barra_y + 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Linha divisória
        cv2.line(tela, (500, y_start), (500, barra_y + barra_height + 20), (100, 100, 100), 2)
        
        # Mensagem de Vencedor
        if competition.vencedor:
            vencedor_nome = competition.jogador1 if competition.vencedor == 1 else competition.jogador2
            resultado_texto = f"PARABENS {vencedor_nome.upper()}! Resultado salvo no ranking."
            (rw, rh), _ = cv2.getTextSize(resultado_texto, cv2.FONT_HERSHEY_DUPLEX, 1.0, 3)
            cv2.putText(tela, resultado_texto, ((1000 - rw) // 2, barra_y + 80), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 100), 3)
        
        # Botões de Ação
        draw_button(tela, (150, 650, 450, 700), (0, 200, 100), "[ENTER] NOVA PARTIDA", label_color=(20, 22, 25))
        draw_button(tela, (550, 650, 850, 700), (200, 80, 80), "[ESC] SAIR", label_color=(255, 255, 255))
        
        show_fullscreen(window_name, tela)
        key = cv2.waitKey(1)
        
        if key == 13: # ENTER
            cv2.destroyWindow(window_name)
            return True
        elif key == 27: # ESC
            cv2.destroyWindow(window_name)
            return False

def mostrar_resultado_final(gamification, counter_final, save_to_ranking=True):
    """Tela de resultado do modo solo com salvamento no ranking (opcional)."""
    nota, pontuacao, descricao = gamification.get_nota_final()
    tempo_total = time.time() - gamification.tempo_inicio
    
    if save_to_ranking:
        # Salva o resultado no ranking
        add_solo_score(
            gamification.nome_usuario, 
            pontuacao, 
            gamification.movimentos_totais, 
            gamification.movimentos_corretos, 
            tempo_total
        )
    
    window_name = "Resultado Final"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    while True:
        tela = np.ones((500, 850, 3), dtype=np.uint8) * 24
        draw_filled_transparent_rect(tela, (0, 0), (850, 100), (20, 22, 25), 0.9)
        cv2.putText(tela, "RELATORIO FINAL", (50, 65), cv2.FONT_HERSHEY_DUPLEX, 1.4, (0, 255, 220), 3)
        
        y_info = 150
        # O nome do jogador pode ser "Video_Analise", então só mostramos se for um jogador real
        if save_to_ranking:
            cv2.putText(tela, f"Jogador: {gamification.nome_usuario}", (60, y_info), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        else:
            cv2.putText(tela, "Modo: Analise de Video", (60, y_info), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        y_info += 50
        
        stats = [
            f"Pontuacao Total: {pontuacao} pts ({nota} - {descricao})",
            f"Polichinelos Corretos: {gamification.movimentos_corretos}/{gamification.movimentos_totais}",
            f"Taxa de Acerto: {gamification.taxa_acerto:.1f}%",
            f"Tempo: {int(tempo_total//60)}:{int(tempo_total%60):02d}"
        ]
        
        y_pos = y_info
        for stat in stats:
            cv2.putText(tela, stat, (60, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (230, 230, 230), 2)
            y_pos += 40
        
        # Mensagem condicional
        if save_to_ranking:
            cv2.putText(tela, "Resultado salvo no ranking!", (60, y_pos + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 100), 2)
        else:
            cv2.putText(tela, "Analise de video concluida.", (60, y_pos + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 2)
        
        draw_button(tela, (80, 400, 380, 450), (0, 200, 100), "[ENTER] REINICIAR", label_color=(20, 22, 25), scale=0.9)
        draw_button(tela, (470, 400, 770, 450), (200, 80, 80), "[ESC] SAIR", label_color=(255, 255, 255), scale=0.9)
        
        show_fullscreen(window_name, tela)
        key = cv2.waitKey(1)
        
        if key == 13: # ENTER
            cv2.destroyWindow(window_name)
            return True
        elif key == 27: # ESC
            cv2.destroyWindow(window_name)
            return False