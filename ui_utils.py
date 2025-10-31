import cv2
import numpy as np

# ============================================================================
# FUNÇÃO DE TELA CHEIA
# ============================================================================

def show_fullscreen(window_name, img):
    """Cria ou atualiza uma janela para ser exibida em tela cheia."""
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, img)

# ============================================================================
# FUNÇÕES DE DESENHO
# ============================================================================

def draw_filled_transparent_rect(img, pt1, pt2, color=(0, 0, 0), alpha=0.65):
    """Desenha um retângulo preenchido e semi-transparente."""
    overlay = img.copy()
    cv2.rectangle(overlay, pt1, pt2, color, -1)
    cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)

def draw_gradient_rect(img, pt1, pt2, color1, color2):
    """Desenha retângulo com gradiente (usado nas telas de ranking)."""
    x1, y1 = pt1
    x2, y2 = pt2
    for i, y in enumerate(range(y1, y2)):
        ratio = (y - y1) / (y2 - y1)
        # Interpolação linear das cores
        color = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(color1, color2))
        cv2.line(img, (x1, y), (x2, y), color, 1)

def draw_label_box(img, text, org, font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.9, thickness=2,
                   text_color=(255, 255, 255), bg_color=(20, 22, 25), alpha=0.7, padding=10):
    """Desenha um texto dentro de uma caixa de fundo semi-transparente."""
    (tw, th), base = cv2.getTextSize(text, font, scale, thickness)
    x, y = org
    x1 = max(x - padding, 0)
    y1 = max(int(y - th - padding), 0)
    x2 = min(int(x + tw + padding), img.shape[1] - 1)
    y2 = min(int(y + base + padding), img.shape[0] - 1)
    draw_filled_transparent_rect(img, (x1, y1), (x2, y2), bg_color, alpha)
    cv2.putText(img, text, (x, y), font, scale, text_color, thickness, cv2.LINE_AA)

def draw_button(canvas, rect, color, label, label_color=(15, 18, 22),
                font=cv2.FONT_HERSHEY_SIMPLEX, scale=0.95, thickness=2):
    """Desenha um botão estilizado com sombra e texto centralizado."""
    x1, y1, x2, y2 = rect
    # Sombra
    overlay = canvas.copy()
    cv2.rectangle(overlay, (x1+4, y1+4), (x2+4, y2+4), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.35, canvas, 0.65, 0, canvas)
    # Botão principal
    overlay = canvas.copy()
    cv2.rectangle(overlay, (x1, y1), (x2, y2), color, -1)
    cv2.addWeighted(overlay, 0.88, canvas, 0.12, 0, canvas)
    # Borda
    cv2.rectangle(canvas, (x1, y1), (x2, y2), (245, 245, 245), 2)
    # Texto
    (tw, th), _ = cv2.getTextSize(label, font, scale, thickness)
    tx = x1 + (x2 - x1 - tw) // 2
    ty = y1 + (y2 - y1 + th) // 2
    cv2.putText(canvas, label, (tx, ty), font, scale, label_color, thickness, cv2.LINE_AA)

def putText_outline(img, text, org, font, scale, color=(255,255,255), thickness=2,
                    outline_color=(0,0,0), outline_thickness=None):
    """Desenha um texto com contorno (outline)."""
    if outline_thickness is None:
        outline_thickness = max(1, thickness + 2)
    cv2.putText(img, text, org, font, scale, outline_color, outline_thickness, cv2.LINE_AA)
    cv2.putText(img, text, org, font, scale, color, thickness, cv2.LINE_AA)
