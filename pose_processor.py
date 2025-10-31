import cv2
import mediapipe as mp
import copy
import numpy as np

# ============================================================================
# DETECÇÃO E PROCESSAMENTO DE POSE
# ============================================================================

def detectar_multiplas_pessoas_corrigido(image, pose_model):
    """
    Detecta poses em duas metades separadas do frame (para modo competição).
    Retorna os landmarks para cada jogador e a posição da linha central.
    """
    h, w = image.shape[:2]
    meio_x = w // 2
    
    jogador1_landmarks, jogador2_landmarks = None, None
    jogador1_original, jogador2_original = None, None
    
    # Processa lado esquerdo (Jogador 1)
    frame_esquerdo = image[:, :meio_x].copy()
    resultado_esquerda = pose_model.process(cv2.cvtColor(frame_esquerdo, cv2.COLOR_BGR2RGB))
    if resultado_esquerda.pose_landmarks:
        jogador1_landmarks = copy.deepcopy(resultado_esquerda.pose_landmarks)
        jogador1_original = copy.deepcopy(resultado_esquerda.pose_landmarks)
        # Ajusta coordenadas para o frame completo (x vai de 0 a 0.5)
        for landmark in jogador1_landmarks.landmark:
            landmark.x = landmark.x * 0.5
    
    # Processa lado direito (Jogador 2)
    frame_direito = image[:, meio_x:].copy()
    resultado_direita = pose_model.process(cv2.cvtColor(frame_direito, cv2.COLOR_BGR2RGB))
    if resultado_direita.pose_landmarks:
        jogador2_landmarks = copy.deepcopy(resultado_direita.pose_landmarks)
        jogador2_original = copy.deepcopy(resultado_direita.pose_landmarks)
        # Ajusta coordenadas para o frame completo (x vai de 0.5 a 1.0)
        for landmark in jogador2_landmarks.landmark:
            landmark.x = (landmark.x * 0.5) + 0.5
    
    return jogador1_landmarks, jogador2_landmarks, jogador1_original, jogador2_original, meio_x

def validar_pose_melhorada(landmarks):
    """Verifica se a pose detectada possui visibilidade suficiente nos pontos críticos."""
    if not landmarks: return False, 0.0
    
    # Pontos críticos: Ombros (11, 12), Quadris (23, 24), Pulsos (15, 16), Tornozelos (27, 28)
    pontos_criticos = [11, 12, 23, 24, 15, 16, 27, 28]
    visibilidades = [landmarks.landmark[idx].visibility for idx in pontos_criticos if idx < len(landmarks.landmark)]
    
    if not visibilidades: return False, 0.0
    
    vis_media = sum(visibilidades) / len(visibilidades)
    vis_minima = min(visibilidades)
    
    # Critérios de visibilidade do código original
    return vis_media >= 0.35 and vis_minima >= 0.25, vis_media

def detectar_postura_polichinelo_competicao(landmarks, w, h):
    """Detecta a postura de polichinelo para o modo competição (usa landmarks do frame completo)."""
    def pt(lm_id): return (landmarks.landmark[lm_id].x * w, landmarks.landmark[lm_id].y * h, landmarks.landmark[lm_id].visibility)
    
    l_sh_x, l_sh_y, l_sh_vis = pt(11); r_sh_x, r_sh_y, r_sh_vis = pt(12)
    l_hp_x, l_hp_y, l_hp_vis = pt(23); r_hp_x, r_hp_y, r_hp_vis = pt(24)
    l_wr_x, l_wr_y, l_wr_vis = pt(15); r_wr_x, r_wr_y, r_wr_vis = pt(16)
    l_an_x, l_an_y, l_an_vis = pt(27); r_an_x, r_an_y, r_an_vis = pt(28)
    l_el_x, l_el_y, l_el_vis = pt(13); r_el_x, r_el_y, r_el_vis = pt(14)
    
    shoulder_mid_y = (l_sh_y + r_sh_y) / 2.0; hip_mid_y = (l_hp_y + r_hp_y) / 2.0
    shoulder_width = abs(r_sh_x - l_sh_x); body_height = abs(hip_mid_y - shoulder_mid_y)
    wrist_mid_y = (l_wr_y + r_wr_y) / 2.0; elbow_mid_y = (l_el_y + r_el_y) / 2.0
    
    tolerance_up, tolerance_down = 0.15 * body_height, 0.10 * body_height
    
    # Posição dos braços (Acima ou Abaixo)
    arms_up = (wrist_mid_y < shoulder_mid_y + tolerance_up and elbow_mid_y < shoulder_mid_y + tolerance_up)
    arms_down = (wrist_mid_y > hip_mid_y - tolerance_down)
    
    # Distância normalizada dos tornozelos
    normalized_distance = abs(r_an_x - l_an_x) / shoulder_width if shoulder_width > 20 else 0
    
    # Posição das pernas (Abertas ou Fechadas)
    legs_open = (normalized_distance > 1.3 and l_an_vis > 0.3 and r_an_vis > 0.3)
    legs_closed = (normalized_distance < 1.5 and l_an_vis > 0.3 and r_an_vis > 0.3)
    
    return arms_up, legs_open, arms_down, legs_closed

def detectar_postura_polichinelo_solo(landmarks, w, h):
    """Detecta a postura de polichinelo para o modo solo (usa landmarks do frame completo)."""
    # A função original do modo solo usava landmarks.landmark, mas a chamada no main.py passa results.pose_landmarks.landmark
    # Para ser compatível com a chamada do main.py, a função precisa aceitar a lista de landmarks, não o objeto PoseLandmarks.
    # No entanto, a lógica interna é quase idêntica à de competição, mas sem a verificação de visibilidade na perna.

    def pt(lm_id): return (landmarks[lm_id].x * w, landmarks[lm_id].y * h)
    
    l_sh_x, l_sh_y = pt(11); r_sh_x, r_sh_y = pt(12)
    l_hp_x, l_hp_y = pt(23); r_hp_x, r_hp_y = pt(24)
    l_wr_x, l_wr_y = pt(15); r_wr_x, r_wr_y = pt(16)
    l_an_x, r_an_x = pt(27)[0], pt(28)[0] # Apenas coordenada x do tornozelo
    l_el_y = pt(13)[1]; r_el_y = pt(14)[1]
    
    shoulder_mid_y = (l_sh_y + r_sh_y) / 2.0
    hip_mid_y = (l_hp_y + r_hp_y) / 2.0
    body_width = max(abs(r_sh_x - l_sh_x), 1)
    body_height = abs(hip_mid_y - shoulder_mid_y)
    wrist_mid_y = (l_wr_y + r_wr_y) / 2.0
    elbow_mid_y = (l_el_y + r_el_y) / 2.0

    tolerance_up = 0.15 * body_height
    tolerance_down = 0.10 * body_height

    arms_up = (wrist_mid_y < shoulder_mid_y + tolerance_up and elbow_mid_y < shoulder_mid_y + tolerance_up)
    arms_down = (wrist_mid_y > hip_mid_y - tolerance_down)
    
    normalized_distance = abs(r_an_x - l_an_x) / body_width if body_width > 20 else 0

    legs_open = (normalized_distance > 1.3)
    legs_closed = (normalized_distance < 1.5)

    return arms_up, legs_open, arms_down, legs_closed
