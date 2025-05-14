import sys
import os
# Añadir el directorio raíz del proyecto al sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
import pygame
import pymunk
import pymunk.pygame_util

from src.model.elementos import *

# Configuración global
GRAVEDAD = 981
ANCHO, ALTO = 1800, 1000
FPS = 60
DELTA_T = 1 / FPS

def dibujar(space: pymunk.Space, window: pygame.Surface, draw_options: pymunk.pygame_util.DrawOptions) -> None:
    window.fill("white")
    space.debug_draw(draw_options)
    pygame.display.update()


def main(window: pygame.Surface, width: int, height: int) -> None:
    pygame.init()
    clock = pygame.time.Clock()
    space = pymunk.Space()
    space.gravity = (0, GRAVEDAD)
    space.damping = 0.99
    space.iterations = 60  # <-- Aumenta las iteraciones del solver
    draw_options = pymunk.pygame_util.DrawOptions(window)

    # 1. Bola 1 (azul) desde arriba
    bola1 = crear_bola(space, radius=15, mass=3, position=(120, 60))

    # 2. Rampas R1-R5 (ajusta posiciones según tu boceto)
    crear_rampa(space, (70, 150), (150, 200))   # R1
    crear_rampa(space, (270, 210), (190, 260))   # R2
    crear_rampa(space, (70, 270), (150, 320))   # R3
    crear_rampa(space, (270, 320), (190, 380))   # R4
    crear_rampa(space, (70, 440), (500, 480))   # R5

    # 3. Polea 1 (verde)
    # Guardar el cuerpo estático de la polea para enganchar la cuerda
    polea1_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    polea1_body.position = (680, 150)
    polea1_shape = pymunk.Circle(polea1_body, 25)
    polea1_shape.friction = 3
    polea1_shape.elasticity = 0
    space.add(polea1_body, polea1_shape)

    # 4. Cuerda 1 (muchos puntos equidistantes a lo largo del trayecto real)
    import math
    # Definir los puntos clave de la trayectoria
    recipiente_pos = (650, 400)
    primer_punto_arco = (700, 200)  # <-- Cambia este punto para acortar la cuerda
    cx, cy, r = 680, 150, 25
    ang_inicio = math.atan2(primer_punto_arco[0] - cy, primer_punto_arco[0] - cx)
    ang_fin = math.radians(360)
    punto_palanca = (800, 250)  # <-- Cambia este punto para acortar la cuerda

    # Trayectoria: recipiente → primer_punto_arco → arco sobre polea → palanca
    trayecto = []
    trayecto.append(recipiente_pos)
    trayecto.append(primer_punto_arco)
    # Arco sobre la polea (de primer_punto_arco hasta el punto más a la derecha de la polea)
    num_puntos_arco = 5
    for i in range(num_puntos_arco + 1):
        ang = ang_inicio + (ang_fin - ang_inicio) * (i / num_puntos_arco)
        x = cx + r * math.cos(ang)
        y = cy + r * math.sin(ang)
        trayecto.append((x, y))
    # Desde el final del arco hasta la palanca
    trayecto.append(punto_palanca)

    # Ahora, interpola muchos puntos a lo largo de todo el trayecto, con distancia máxima entre puntos (ej: 10 px)
    def interpola_trayecto(trayecto, distancia_max=10):
        puntos = []
        for i in range(len(trayecto) - 1):
            x0, y0 = trayecto[i]
            x1, y1 = trayecto[i+1]
            dx = x1 - x0
            dy = y1 - y0
            dist = math.hypot(dx, dy)
            pasos = max(1, int(dist // distancia_max))
            for j in range(pasos):
                t = j / pasos
                x = x0 + dx * t
                y = y0 + dy * t
                puntos.append((x, y))
        puntos.append(trayecto[-1])
        return [(int(x), int(y)) for x, y in puntos]

    # Puedes aumentar distancia_max para menos puntos (más separados)
    puntos_cuerda1 = interpola_trayecto(trayecto, distancia_max=15)
    cuerda1 = crear_cuerda(space, puntos_cuerda1, radio=3)

    # Crear el recipiente (dinámico, animado)
    recipiente_pos = (650, 400)
    recipiente_size = (150, 30)
    recipiente_mass = 2
    recipiente_body = pymunk.Body(recipiente_mass, float('inf'))  # <-- Evita rotación
    recipiente_body.position = recipiente_pos
    recipiente_shape = pymunk.Poly.create_box(recipiente_body, recipiente_size)
    recipiente_shape.friction = 100
    recipiente_shape.elasticity = 0.2
    space.add(recipiente_body, recipiente_shape)

    # Fijar el PRIMER segmento de la cuerda al recipiente animado (no el último)
    if cuerda1:
        joint_cuerda_recipiente = pymunk.PinJoint(cuerda1[0], recipiente_body, (0,0), (0,0))
        space.add(joint_cuerda_recipiente)

    # Si quieres que el recipiente solo se mueva verticalmente (como un elevador), añade un GrooveJoint:
    groove = pymunk.GrooveJoint(
        space.static_body,
        recipiente_body,
        (recipiente_pos[0], recipiente_pos[1] + 200),
        (recipiente_pos[0], recipiente_pos[1] + 400),
        (0, 0)
    )
    space.add(groove)

    # 5. Bola 2 (azul) sobre palanca
    bola2 = crear_bola(space, radius=15, mass=0.1, position=(840, 120))

    # 6. Palanca animada (línea café, pivote fijo en punto amarillo)
    # Cambia el orden de pivote y extremo para que la palanca quede orientada correctamente
    pivote = (1050, 120)
    extremo = (850, 220)
    palanca = crear_palanca_animada(space, pivote=pivote, extremo=extremo, thickness=8, mass=1)

    # Enganchar el último segmento de la cuerda a un extremo de la palanca
    if cuerda1:
        # El cuerpo de la palanca está centrado en el punto medio entre pivote y extremo
        # El extremo móvil local es la mitad del vector desde pivote al extremo, pero hay que considerar el sentido
        # Para que el enganche sea justo en el extremo visible, calcula:
        palanca_pos = palanca.position
        # Vector del centro de la palanca al extremo (en el sistema local de la palanca)
        local_extremo = (extremo[0] - (pivote[0] + extremo[0]) / 2, extremo[1] - (pivote[1] + extremo[1]) / 2)
        joint_cuerda_palanca = pymunk.PinJoint(cuerda1[-1], palanca, (0,0), local_extremo)
        space.add(joint_cuerda_palanca)

    # 7. Rampa R15 (horizontal)
    # crear_rampa(space, (820, 120), (950, 120), thickness=8)  # R15

    # # 8. Rampas R6-R11 (zigzag)
    crear_rampa(space, (1050, 200), (1100, 300)) # R6
    crear_rampa(space, (1200, 200), (1150, 300))   # R7
    crear_rampa(space, (1050, 320), (1120, 420))   # R8
    crear_rampa(space, (1200, 400), (1150, 500))   # R9
    crear_rampa(space, (1050, 500), (1120, 600))  # R10
    crear_rampa(space, (1120, 600), (1600, 603)) # R11

    # 9. Rampa R12 (larga)
    crear_rampa(space, (1780, 700), (1128, 760))  # R12

    # 10. Polea 2 (verde)
    # crear_polea(space, position=(250, 650), radius=25)

    # 11. Cuerda 2 (realista, segmentos)
    # puntos_cuerda2 = [(500, 350), (400, 500), (350, 600)]
    # cuerda2 = crear_cuerda(space, puntos_cuerda2, radio=3)

    # 12. Elevador (rectángulo azul)
    # elevador = crear_elevador(space, position=(300, 600), size=(80, 20))

    # 13. Peso pentágono rojo (dinámico)
    pentagono = crear_pentagono(space, position=(450, 890), size=20)

    # 14. Rampa R13 (carrito)
    crear_rampa(space, (1060, 850), (400, 905))   # R13

    # 15. Carrito (morado con ruedas)
    carrito = crear_carrito(space, position=(975, 850), size=(60, 30))
    # Ruedas del carrito (puedes crear bolas pequeñas y unirlas con joints si quieres más realismo)

    # 16. Rampa R14 (debajo del elevador)
    # crear_rampa(space, (250, 650), (350, 650))   # R14

    # Límites
    crear_limites(space, width, height)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                x, y = pygame.mouse.get_pos()
                print((x, y))
        dibujar(space, window, draw_options)
        space.step(DELTA_T)
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    pygame.init()
    window = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Simulación Máquina de Goldberg")
    main(window, ANCHO, ALTO)
