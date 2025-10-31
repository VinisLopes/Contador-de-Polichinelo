import cv2
import mediapipe as mp
import time
from ui_utils import show_fullscreen, putText_outline
from screens import escolher_modo, show_solo_ranking, show_competicao_ranking, obter_nome_usuario, obter_nomes_jogadores, escolher_meta, escolher_video, mostrar_resultado_final, mostrar_resultado_competicao
from pose_processor import validar_pose_melhorada, detectar_postura_polichinelo_solo, detectar_multiplas_pessoas_corrigido, detectar_postura_polichinelo_competicao
from gamification import GamificationSystem, CompetitionSystem

if __name__ == "__main__":
    mp_drawing = mp.solutions.drawing_utils
    mp_pose = mp.solutions.pose
    
    WINDOW_NAME = "Contador de Polichinelos"
    
    # Inicializa o modelo de pose fora do loop para reutilização
    pose_model = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

    while True:
        modo = escolher_modo()
        if modo is None:
            break
        
        if modo == 3:
            show_solo_ranking()
            continue
        
        if modo == 4:
            show_competicao_ranking()
            continue

        # --- MODO SOLO (0) ---
        if modo == 0: 
            nome_usuario = obter_nome_usuario()
            if not nome_usuario:
                continue
            
            meta = escolher_meta()
            if not meta:
                continue
            
            gamification = GamificationSystem(nome_usuario, meta)
            cap = cv2.VideoCapture(0)
            
            counter1 = 0
            stage1 = "down"
            open_frames1 = 0
            closed_frames1 = 0
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Inverte o frame para que o usuário se veja como em um espelho
                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]
                image = frame.copy()
                
                # Processamento da Pose
                results = pose_model.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                if results.pose_landmarks:
                    pose_valida, _ = validar_pose_melhorada(results.pose_landmarks)
                    
                    if pose_valida:
                        # Usando a função de detecção de postura do modo solo
                        arms_up, legs_open, arms_down, legs_closed = detectar_postura_polichinelo_solo(results.pose_landmarks.landmark, w, h)
                        
                        # Lógica de contagem de frames para suavizar a detecção
                        if arms_up and legs_open:
                            open_frames1 = min(open_frames1 + 1, 15)
                            closed_frames1 = max(0, closed_frames1 - 1)
                        elif arms_down and legs_closed:
                            closed_frames1 = min(closed_frames1 + 1, 15)
                            open_frames1 = max(0, open_frames1 - 1)
                        else:
                            open_frames1 = max(0, open_frames1 - 1)
                            closed_frames1 = max(0, closed_frames1 - 1)
                        
                        # Transição de estado e contagem
                        threshold = 3 # Limite de frames para transição
                        if stage1 == "down" and open_frames1 >= threshold and arms_up and legs_open:
                            stage1 = "up"
                            closed_frames1 = 0 # Reinicia o contador de frames fechados
                        elif stage1 == "up" and closed_frames1 >= threshold and arms_down and legs_closed:
                            stage1 = "down"
                            counter1 += 1
                            gamification.avaliar_movimento(arms_up, legs_open, arms_down, legs_closed, True) # Assumindo correto se detectado
                            open_frames1 = 0 # Reinicia o contador de frames abertos
                    
                    # Desenha os landmarks
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # Informações na tela
                putText_outline(image, f"Repeticoes: {counter1}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255))
                putText_outline(image, f"Meta: {gamification.meta_polichinelos}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255))
                
                show_fullscreen(WINDOW_NAME, image)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or counter1 >= gamification.meta_polichinelos:
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Mostra o resultado final e salva no ranking
            mostrar_resultado_final(gamification, counter1)

        # --- MODO COMPETIÇÃO (1) ---
        elif modo == 1:
            nome1, nome2 = obter_nomes_jogadores()
            if not nome1 or not nome2:
                continue
            
            meta = escolher_meta()
            if not meta:
                continue
            
            competition = CompetitionSystem(nome1, nome2, meta)
            cap = cv2.VideoCapture(0)
            
            counter1, counter2 = 0, 0
            stage1, stage2 = "down", "down"
            open_frames1, closed_frames1 = 0, 0
            open_frames2, closed_frames2 = 0, 0
            flash_frames1, flash_frames2 = 0, 0
            
            while cap.isOpened() and competition.vencedor is None:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Não inverte o frame, pois a tela é dividida
                h, w = frame.shape[:2]
                image = frame.copy()
                
                # Desenha a linha divisória
                cv2.line(image, (w // 2, 0), (w // 2, h), (255, 255, 255), 2)
                
                # Detecção de múltiplas poses
                landmarks1, landmarks2, landmarks1_original, landmarks2_original, meio_x = detectar_multiplas_pessoas_corrigido(image, pose_model)
                
                # --- Processamento Jogador 1 ---
                if landmarks1:
                    pose_valida, vis_media = validar_pose_melhorada(landmarks1_original)
                    if pose_valida:
                        arms_up, legs_open, arms_down, legs_closed = detectar_postura_polichinelo_competicao(landmarks1_original, w, h)
                        
                        threshold = 4
                        if arms_up and legs_open:
                            open_frames1 = min(open_frames1 + 1, 15)
                            closed_frames1 = max(0, closed_frames1 - 1)
                        elif arms_down and legs_closed:
                            closed_frames1 = min(closed_frames1 + 1, 15)
                            open_frames1 = max(0, open_frames1 - 1)
                        else:
                            open_frames1, closed_frames1 = max(0, open_frames1 - 1), max(0, closed_frames1 - 1)
                        
                        if stage1 == "down" and open_frames1 >= threshold:
                            stage1 = "up"
                            closed_frames1 = 0
                        elif stage1 == "up" and closed_frames1 >= threshold:
                            stage1 = "down"
                            counter1 += 1
                            flash_frames1 = 15
                            if counter1 >= meta:
                                competition.set_vencedor(1)
                                
                        # Desenha os landmarks
                        mp_drawing.draw_landmarks(image, landmarks1, mp_pose.POSE_CONNECTIONS,
                                                mp_drawing.DrawingSpec(color=(80, 170, 255), thickness=2, circle_radius=2),
                                                mp_drawing.DrawingSpec(color=(80, 170, 255), thickness=2, circle_radius=2))
                    
                    # Informações na tela
                    putText_outline(image, f"{nome1}: {counter1}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 170, 255))
                    putText_outline(image, f"Stage: {stage1}", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200))
                else:
                    putText_outline(image, f"{nome1}: N/A", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (80, 170, 255))
                    
                # --- Processamento Jogador 2 ---
                if landmarks2:
                    pose_valida, vis_media = validar_pose_melhorada(landmarks2_original)
                    if pose_valida:
                        arms_up, legs_open, arms_down, legs_closed = detectar_postura_polichinelo_competicao(landmarks2_original, w, h)
                        
                        threshold = 4
                        if arms_up and legs_open:
                            open_frames2 = min(open_frames2 + 1, 15)
                            closed_frames2 = max(0, closed_frames2 - 1)
                        elif arms_down and legs_closed:
                            closed_frames2 = min(closed_frames2 + 1, 15)
                            open_frames2 = max(0, open_frames2 - 1)
                        else:
                            open_frames2, closed_frames2 = max(0, open_frames2 - 1), max(0, closed_frames2 - 1)
                        
                        if stage2 == "down" and open_frames2 >= threshold:
                            stage2 = "up"
                            closed_frames2 = 0
                        elif stage2 == "up" and closed_frames2 >= threshold:
                            stage2 = "down"
                            counter2 += 1
                            flash_frames2 = 15
                            if counter2 >= meta:
                                competition.set_vencedor(2)
                                
                        # Desenha os landmarks
                        mp_drawing.draw_landmarks(image, landmarks2, mp_pose.POSE_CONNECTIONS,
                                                mp_drawing.DrawingSpec(color=(255, 140, 80), thickness=2, circle_radius=2),
                                                mp_drawing.DrawingSpec(color=(255, 140, 80), thickness=2, circle_radius=2))
                    
                    # Informações na tela
                    putText_outline(image, f"{nome2}: {counter2}", (meio_x + 30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 140, 80))
                    putText_outline(image, f"Stage: {stage2}", (meio_x + 30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200))
                else:
                    putText_outline(image, f"{nome2}: N/A", (meio_x + 30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 140, 80))
                    
                # Efeito flash ao contar
                if flash_frames1 > 0:
                    cv2.circle(image, (w//4, h//2), 100, (0, 255, 0), -1)
                    flash_frames1 -= 1
                if flash_frames2 > 0:
                    cv2.circle(image, (w//2 + w//4, h//2), 100, (0, 255, 0), -1)
                    flash_frames2 -= 1
                    
                # Informação de Meta (no canto inferior esquerdo)
                putText_outline(image, f"Meta: {meta}", (30, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255))
                
                show_fullscreen(WINDOW_NAME, image)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Mostra o resultado final e salva no ranking
            # REMOVIDA A CONDIÇÃO "if competition.vencedor is not None:"
            mostrar_resultado_competicao(competition, counter1, counter2)
            
        # --- MODO ANÁLISE DE VÍDEO (2) ---
        elif modo == 2:
            video_path = escolher_video()
            if not video_path:
                continue
                
            # Cria um objeto Gamification para rastrear estatísticas
            # Meta alta para não interferir, nome "Video_Analise"
            gamification = GamificationSystem("Video_Analise", 9999)
            
            cap = cv2.VideoCapture(video_path)
            
            counter1 = 0
            stage1 = "down"
            open_frames1 = 0
            closed_frames1 = 0
            start_time = time.time()
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                h, w = frame.shape[:2]
                image = frame.copy()
                
                # Processamento da Pose
                results = pose_model.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
                if results.pose_landmarks:
                    pose_valida, _ = validar_pose_melhorada(results.pose_landmarks)
                    
                    if pose_valida:
                        # Usando a função de detecção de postura do modo solo
                        arms_up, legs_open, arms_down, legs_closed = detectar_postura_polichinelo_solo(results.pose_landmarks.landmark, w, h)
                        
                        # Lógica de contagem de frames para suavizar a detecção
                        if arms_up and legs_open:
                            open_frames1 = min(open_frames1 + 1, 15)
                            closed_frames1 = max(0, closed_frames1 - 1)
                        elif arms_down and legs_closed:
                            closed_frames1 = min(closed_frames1 + 1, 15)
                            open_frames1 = max(0, open_frames1 - 1)
                        else:
                            open_frames1 = max(0, open_frames1 - 1)
                            closed_frames1 = max(0, closed_frames1 - 1)
                        
                        # Transição de estado e contagem
                        threshold = 3 # Limite de frames para transição
                        if stage1 == "down" and open_frames1 >= threshold and arms_up and legs_open:
                            stage1 = "up"
                            closed_frames1 = 0 # Reinicia o contador de frames fechados
                        elif stage1 == "up" and closed_frames1 >= threshold and arms_down and legs_closed:
                            stage1 = "down"
                            counter1 += 1
                            # Avalia o movimento para as estatísticas
                            gamification.avaliar_movimento(arms_up, legs_open, arms_down, legs_closed, True)
                            open_frames1 = 0 # Reinicia o contador de frames abertos
                    
                    # Desenha os landmarks
                    mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                
                # Informações na tela
                putText_outline(image, f"Repeticoes: {counter1}", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255))
                putText_outline(image, f"Tempo: {int(time.time() - start_time)}s", (30, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255,255,255))
                
                show_fullscreen(WINDOW_NAME, image)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            # Mostra a tela de resultado final, mas NÃO salva no ranking
            mostrar_resultado_final(gamification, counter1, save_to_ranking=False)
            
    # Libera o modelo de pose ao sair do loop principal
    pose_model.close()
    cv2.destroyAllWindows()