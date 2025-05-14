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

# Propiedades de ejemplo para dominós (puedes ajustar según tu diseño)
PROPIEDADES_DOMINO = {
    "num_dominoes": 10,
    "width": 10,
    "height": 45,
    "mass": 0.5,
    "friction": 0.4,
    "elasticity": 0.4,
    "spacing_factor": 0.4,
    "start_x": 450,
}
ALTURA_MESA = ALTO - 150
Y_SUELO = ALTURA_MESA - (PROPIEDADES_DOMINO["height"] / 2)
Y_INICIO = ALTURA_MESA - 200

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
    draw_options = pymunk.pygame_util.DrawOptions(window)

    # 1. Bola 1 (azul) desde arriba
    bola1 = crear_bola(space, radius=15, mass=0.2, position=(120, 60))

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
    polea1_shape.friction = 0.5
    polea1_shape.elasticity = 0.2
    space.add(polea1_body, polea1_shape)

    # 4. Cuerda 1 (más puntos entre el recipiente y la polea, pero sin hacerla más larga)
    import math
    # Interpolación densa entre el recipiente y el primer punto antes del arco
    recipiente_pos = (650, 400)
    primer_punto_arco = (750, 155)
    num_puntos_interp = 15  # Más puntos para suavidad
    puntos_cuerda1 = []
    for i in range(num_puntos_interp + 1):
        t = i / num_puntos_interp
        x = int(recipiente_pos[0] + (primer_punto_arco[0] - recipiente_pos[0]) * t)
        y = int(recipiente_pos[1] + (primer_punto_arco[1] - recipiente_pos[1]) * t)
        puntos_cuerda1.append((x, y))
    # Enganchar a la polea (arco por ARRIBA)
    cx, cy, r = 680, 150, 25
    ang_inicio = math.radians(360)
    ang_fin = math.radians(0)
    num_puntos_arco = 12
    for i in range(num_puntos_arco + 1):
        ang = ang_inicio + (ang_fin - ang_inicio) * (i / num_puntos_arco)
        x = int(cx + r * math.cos(ang))
        y = int(cy - r * math.sin(ang))
        puntos_cuerda1.append((x, y))
    puntos_cuerda1 += [
        (700, 140),
        (750, 130),
        (800, 125),
        (850, 123),
        (900, 122),
        (950, 120),
    ]
    cuerda1 = crear_cuerda(space, puntos_cuerda1, radio=3)

    # Crear el recipiente (dinámico, animado)
    recipiente_pos = (650, 400)
    recipiente_size = (150, 30)
    recipiente_mass = 1.5
    recipiente_body = pymunk.Body(recipiente_mass, pymunk.moment_for_box(recipiente_mass, recipiente_size))
    recipiente_body.position = recipiente_pos
    recipiente_shape = pymunk.Poly.create_box(recipiente_body, recipiente_size)
    recipiente_shape.friction = 0.7
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
        (recipiente_pos[0], recipiente_pos[1] - 200),
        (recipiente_pos[0], recipiente_pos[1] + 200),
        (0, 0)
    )
    space.add(groove)

    # 5. Bola 2 (azul) sobre palanca
    bola2 = crear_bola(space, radius=15, mass=0.2, position=(820, 120))

    # 6. Palanca animada (línea café, pivote fijo en punto amarillo)
    pivote = (750, 220)
    extremo = (950, 120)
    palanca = crear_palanca_animada(space, pivote=pivote, extremo=extremo, thickness=8, mass=1.0)

    # Enganchar el último segmento de la cuerda a un extremo de la palanca
    if cuerda1:
        # Calcula la posición local del extremo respecto al centro de la palanca
        palanca_pos = palanca.position
        local_extremo = (extremo[0] - palanca_pos[0], extremo[1] - palanca_pos[1])
        joint_cuerda_palanca = pymunk.PinJoint(cuerda1[-1], palanca, (0,0), local_extremo)
        space.add(joint_cuerda_palanca)

    # 7. Rampa R15 (horizontal)
    # crear_rampa(space, (820, 120), (950, 120), thickness=8)  # R15

    # # 8. Rampas R6-R11 (zigzag)
    # crear_rampa(space, (950, 120), (980, 170))   # R6
    # crear_rampa(space, (980, 170), (950, 200))   # R7
    # crear_rampa(space, (950, 200), (980, 230))   # R8
    # crear_rampa(space, (980, 230), (950, 260))   # R9
    # crear_rampa(space, (950, 260), (1050, 280))  # R10
    # crear_rampa(space, (1050, 280), (1150, 300)) # R11

    # 9. Rampa R12 (larga)
    # crear_rampa(space, (1150, 300), (900, 400))  # R12

    # 10. Polea 2 (verde)
    crear_polea(space, position=(70, 750), radius=25)

    # 11. Cuerda 2 (realista, segmentos)
    puntos_cuerda2 = [(500, 350), (400, 500), (350, 600)]
    cuerda2 = crear_cuerda(space, puntos_cuerda2, radio=3)

    # 12. Elevador (rectángulo azul)
    elevador = crear_elevador(space, position=(300, 600), size=(80, 20))

    # 13. Peso pentágono rojo (dinámico)
    pentagono = crear_pentagono(space, position=(400, 650), size=20)

    # 14. Rampa R13 (carrito)
    crear_rampa(space, (500, 700), (700, 720))   # R13

    # 15. Carrito (morado con ruedas)
    carrito = crear_carrito(space, position=(520, 690), size=(60, 30))
    # Ruedas del carrito (puedes crear bolas pequeñas y unirlas con joints si quieres más realismo)

    # 16. Rampa R14 (debajo del elevador)
    crear_rampa(space, (250, 650), (350, 650))   # R14

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
