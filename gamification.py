import time
import math

# ============================================================================
# CLASSE DE GAMIFICAÇÃO (MODO SOLO)
# ============================================================================

class GamificationSystem:
    def __init__(self, nome_usuario, meta_polichinelos):
        self.nome_usuario = nome_usuario
        self.meta_polichinelos = meta_polichinelos
        self.movimentos_totais = 0
        self.movimentos_corretos = 0
        self.tempo_inicio = time.time()
        self.taxa_acerto = 0.0
        self.pontuacao_base = 0
        self.pontuacao_bonus = 0
        self.pontuacao_total = 0

    def avaliar_movimento(self, arms_up, legs_open, arms_down, legs_closed, is_correct):
        self.movimentos_totais += 1
        if is_correct:
            self.movimentos_corretos += 1
            self.pontuacao_base += 50 # 50 pontos por polichinelo correto
        
        # Lógica de bônus (simplificada do original)
        if self.movimentos_totais > 0:
            self.taxa_acerto = (self.movimentos_corretos / self.movimentos_totais) * 100
        
        # Bônus por meta atingida (será calculado no final)

    def get_nota_final(self):
        tempo_total = time.time() - self.tempo_inicio
        
        # Bônus por meta atingida
        if self.movimentos_corretos >= self.meta_polichinelos:
            self.pontuacao_bonus += 200 # Bônus por completar a meta
        
        # Bônus por velocidade (cada 10 segundos abaixo de 60 segundos por polichinelo)
        if self.movimentos_corretos > 0:
            tempo_por_movimento = tempo_total / self.movimentos_corretos
            if tempo_por_movimento < 60:
                bonus_velocidade = math.floor((60 - tempo_por_movimento) / 10) * 50
                self.pontuacao_bonus += bonus_velocidade
        
        self.pontuacao_total = self.pontuacao_base + self.pontuacao_bonus
        
        # Lógica de nota e descrição (baseada na taxa de acerto e meta)
        if self.taxa_acerto >= 90 and self.movimentos_corretos >= self.meta_polichinelos:
            nota = "A+"; descricao = "Impecavel"
        elif self.taxa_acerto >= 80 and self.movimentos_corretos >= self.meta_polichinelos:
            nota = "A"; descricao = "Excelente"
        elif self.taxa_acerto >= 70 and self.movimentos_corretos >= self.meta_polichinelos:
            nota = "B"; descricao = "Muito Bom"
        elif self.taxa_acerto >= 60:
            nota = "C"; descricao = "Bom"
        else:
            nota = "D"; descricao = "Precisa Praticar Mais"
            
        return nota, self.pontuacao_total, descricao

# ============================================================================
# CLASSE DE COMPETIÇÃO (MODO COMPETIÇÃO)
# ============================================================================

class CompetitionSystem:
    def __init__(self, jogador1, jogador2, meta_polichinelos):
        self.jogador1 = jogador1
        self.jogador2 = jogador2
        self.meta_polichinelos = meta_polichinelos
        self.tempo_inicio = time.time()
        self.tempo_final = None
        self.vencedor = None # 1 para jogador 1, 2 para jogador 2
        
    def registrar_polichinelo(self, jogador_num):
        if self.vencedor is None:
            # A contagem real dos polichinelos é feita no loop principal, aqui só registramos a vitória
            # Se o loop principal detectar que a meta foi atingida, ele deve chamar esta função.
            # No código original, a contagem é feita no loop e a vitória é determinada lá.
            # Vamos manter a lógica do original: esta função é chamada *após* o polichinelo ser contado.
            pass

    def set_vencedor(self, vencedor_num):
        if self.vencedor is None:
            self.vencedor = vencedor_num
            self.tempo_final = time.time() - self.tempo_inicio
