import cv2 as cv
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

def getHandMove(hand_landmarks):
    landmarks = hand_landmarks.landmark
    if all([landmarks[i].y < landmarks[i+3].y for i in range (9, 20, 4)]): return "pedra"
    elif landmarks[13].y < landmarks[16].y and landmarks[17].y < landmarks[20].y: return "tesoura"
    else: return "papel"

#video
vid = cv.VideoCapture(0)

#Relógio para controlar o jogo
clock = 0

#Jogada que cada player
p1_move = p2_move = None

#Texto do jogo
gameText = ""

#Placar do jogo
p1_score = 0
p2_score = 0

#Aconteceu um jogo
success = True



#Confidence do detector
with mp_hands.Hands(model_complexity = 0,
                    min_detection_confidence = 0.5,
                    min_tracking_confidence  = 0.5) as hands:
    #laço infinito para ler frames
    while True:
        ret, frame = vid.read()
        if not ret or frame is None: break

        #É necessário converter as cores
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)

        #Roda o modelo nos frames e descobre onde estão as mãos, retornando para esta variável
        results = hands.process(frame)

        #Voltar a cor ao normal para mostrar ao vídeo
        frame = cv.cvtColor(frame, cv.COLOR_RGB2BGR)

        #Desenhar as landmarks das mãos em cima delas
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks (frame,
                                           hand_landmarks,
                                           mp_hands.HAND_CONNECTIONS,
                                           mp_drawing_styles.get_default_hand_landmarks_style(),
                                           mp_drawing_styles.get_default_hand_connections_style())

        #Reverter câmera que foi flipada
        frame = cv.flip(frame, 1)

        #Resetar jogo
        if 0 <= clock < 20:
            success = True
            gameText = "Preparados?"
        elif clock < 30: gameText = "3..."
        elif clock < 40: gameText = "2..."
        elif clock < 50: gameText = "1..."
        elif clock < 60: gameText = "JOGAR!"
        elif clock == 60:
            hls = results.multi_hand_landmarks
            #Verificar se tem landmark de duas mãos (ou seja, duas listas)
            if hls and len(hls) == 2:
                p1_move = getHandMove(hls[0])
                p2_move = getHandMove(hls[1])
            else:
                success = False
        elif clock < 100:
            #Mostrar quem ganhou
            if success:
                gameText = f"Jogador 1 jogou {p1_move}. Jogador 2 jogou {p2_move}."
                if p1_move == p2_move: 
                    gameText = f"{gameText} O jogo empatou!"
                if p1_move == "papel" and p2_move == "pedra": 
                    gameText = f"{gameText} O jogador 1 ganhou!"
                    p1_score = p1_score + 1
                if p1_move == "pedra" and p2_move == "tesoura": 
                    gameText = f"{gameText} O jogador 1 ganhou!"
                    p1_score = p1_score + 1
                if p1_move == "tesoura" and p2_move == "papel": 
                    gameText = f"{gameText} O jogador 1 ganhou!"
                    p1_score = p1_score + 1
                else: 
                    gameText = f"{gameText} O jogador 2 ganhou!"
                    p2_score = p2_score + 1
            else:
                gameText = "Jogaram de forma errada!"

        #Colocar textos na tela
        cv.putText(frame, f"Relogio:  {clock}", (50,50), cv.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv.LINE_AA)
        cv.putText(frame, f"Pontos jogador 1:  {p1_score}", (50,80), cv.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv.LINE_AA)
        cv.putText(frame, f"Pontos jogador 2:  {p2_score}", (50,110), cv.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv.LINE_AA)
        cv.putText(frame, gameText, (50,140), cv.FONT_HERSHEY_PLAIN, 1, (0,0,255), 1, cv.LINE_AA)
        clock = (clock + 1) % 100

        cv.imshow('jokenpo', frame)

        #Se clicarmos 'q' irá sair do loop
        if cv.waitKey(1) & 0xFF == ord('q'):break
    
vid.release()
cv.destroyAllWindows()