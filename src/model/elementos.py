import pymunk
from typing import Tuple, List

# ...Funciones para crear límites, bolas, mesas, rampas, dominós y palancas...

def crear_limites(space: pymunk.Space, width: int, height: int) -> None:
    # ...código de create_boundaries...
    boundaries = [
        [(width / 2, height - 10), (width, 20)],
        [(width / 2, 10), (width, 20)],
        [(10, height / 2), (20, height)],
        [(width - 10, height / 2), (20, height)]
    ]
    for position, size in boundaries:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = position
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.4
        shape.friction = 0.5
        space.add(body, shape)

def crear_bola(space: pymunk.Space, radius: float, mass: float, position: Tuple[float, float]) -> pymunk.Shape:
    # ...código de create_ball...
    body = pymunk.Body()
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.mass = mass
    shape.color = (255, 0, 0, 100)
    shape.elasticity = 0.9
    shape.friction = 0.4
    shape.collision_type = 0
    space.add(body, shape)
    return shape

def crear_mesa(space: pymunk.Space, width: float, y_pos: float, thickness: float = 10) -> None:
    # ...código de create_table...
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = (width / 2, y_pos)
    shape = pymunk.Poly.create_box(body, (width, thickness))
    shape.friction = 0.5
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_rampas(space: pymunk.Space, start_x: float, start_y: float, ramp_length: float = 200, drop_height: float = 80, thickness: float = 5) -> None:
    # ...código de create_ramps...
    body1 = pymunk.Body(body_type=pymunk.Body.STATIC)
    x1, y1 = start_x, start_y
    x2, y2 = x1 + ramp_length, y1 - (drop_height // 2)
    ramp1 = pymunk.Segment(body1, (x1, y1), (x2, y2), thickness)
    ramp1.friction = 0.7
    ramp1.elasticity = 0.2
    space.add(body1, ramp1)
    body2 = pymunk.Body(body_type=pymunk.Body.STATIC)
    x3, y3 = start_x, y2 - drop_height
    x4, y4 = x3 - ramp_length, y3 - (drop_height // 2)
    ramp2 = pymunk.Segment(body2, (x3, y3), (x4, y4), thickness)
    ramp2.friction = 0.7
    ramp2.elasticity = 0.2
    space.add(body2, ramp2)
    body3 = pymunk.Body(body_type=pymunk.Body.STATIC)
    x5, y5 = x4 + 20 + ramp_length, y4 - drop_height
    x6, y6 = x5 + ramp_length, y5 - (drop_height // 2)
    ramp3 = pymunk.Segment(body3, (x5, y5), (x6, y6), thickness)
    ramp3.friction = 0.7
    ramp3.elasticity = 0.2
    space.add(body3, ramp3)
    body4 = pymunk.Body(body_type=pymunk.Body.STATIC)
    x7, y7 = start_x, y6 + 700 - 230
    x8, y8 = x7 - ramp_length - 20, y7 - (drop_height // 2)
    ramp4 = pymunk.Segment(body4, (x7, y7), (x8, y8), thickness)
    ramp4.friction = 0.7
    ramp4.elasticity = 0.2
    space.add(body4, ramp4)

def crear_domino(pos_x: float, pos_y: float, width: float, height: float, mass: float, friction: float, elasticity: float, space: pymunk.Space) -> Tuple[pymunk.Body, pymunk.Shape]:
    # ...código de create_domino...
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, (width, height)))
    body.position = (pos_x, pos_y)
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.friction = friction
    shape.elasticity = elasticity
    shape.collision_type = 1
    space.add(body, shape)
    return body, shape

def crear_palanca(space: pymunk.Space, start: Tuple[float, float] = (899, 626), end: Tuple[float, float] = (1055, 626), thickness: float = 10, mass: float = 1.0) -> None:
    # ...código de create_lever...
    length = end[0] - start[0]
    pivot_x = (start[0] + end[0]) / 2
    pivot_y = (start[1] + end[1]) / 2
    pivot_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    pivot_body.position = (pivot_x, pivot_y)
    moment = pymunk.moment_for_box(mass, (length, thickness))
    lever_body = pymunk.Body(mass, moment)
    lever_body.position = (pivot_x, pivot_y)
    lever_shape = pymunk.Poly.create_box(lever_body, (length, thickness))
    lever_shape.friction = 0.5
    lever_shape.elasticity = 0.2
    pivot_joint = pymunk.PivotJoint(pivot_body, lever_body, (pivot_x, pivot_y))
    space.add(pivot_body, lever_body, lever_shape, pivot_joint)

def crear_botella_guia(space: pymunk.Space, position: Tuple[float, float], height: float = 80, width: float = 30) -> None:
    # Simula una botella vertical como canal guía (rectángulo estático)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Poly.create_box(body, (width, height))
    shape.friction = 0.6
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_plataforma_inclinada(space: pymunk.Space, start: Tuple[float, float], end: Tuple[float, float], thickness: float = 10) -> None:
    # Plataforma inclinada simple (segmento estático)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, start, end, thickness)
    shape.friction = 0.7
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_embudo(space: pymunk.Space, position: Tuple[float, float], width: float = 60, height: float = 40) -> None:
    # Simula un embudo con dos segmentos convergentes
    x, y = position
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    left = pymunk.Segment(body, (x - width // 2, y), (x, y - height), 4)
    right = pymunk.Segment(body, (x + width // 2, y), (x, y - height), 4)
    left.friction = right.friction = 0.7
    left.elasticity = right.elasticity = 0.2
    space.add(body, left, right)

def crear_polea(space: pymunk.Space, position: Tuple[float, float], radius: float = 15) -> None:
    # Simula una polea como un círculo estático
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Circle(body, radius)
    shape.friction = 0.5
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_elevador(space: pymunk.Space, position: Tuple[float, float], size: Tuple[float, float] = (40, 10)) -> pymunk.Body:
    # Simula un elevador como una caja dinámica restringida verticalmente
    mass = 1.0
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
    body.position = position
    shape = pymunk.Poly.create_box(body, size)
    shape.friction = 0.5
    shape.elasticity = 0.2
    # Restringe el movimiento a solo eje Y (simulación simple)
    groove = pymunk.GrooveJoint(space.static_body, body, (position[0], position[1]-100), (position[0], position[1]+100), (0,0))
    space.add(body, shape, groove)
    return body

def crear_carrito(space: pymunk.Space, position: Tuple[float, float], size: Tuple[float, float] = (40, 20)) -> pymunk.Body:
    # Simula un carrito como una caja dinámica
    mass = 1.0
    body = pymunk.Body(mass, pymunk.moment_for_box(mass, size))
    body.position = position
    shape = pymunk.Poly.create_box(body, size)
    shape.friction = 0.7
    shape.elasticity = 0.2
    space.add(body, shape)
    return body

def crear_pilas(space: pymunk.Space, position: Tuple[float, float], size: Tuple[float, float] = (20, 20)) -> None:
    # Simula un par de pilas como una caja estática
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Poly.create_box(body, size)
    shape.friction = 0.5
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_botella_final(space: pymunk.Space, position: Tuple[float, float], size: Tuple[float, float] = (60, 20)) -> None:
    # Simula la botella final horizontal (puedes animar su inclinación después)
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = position
    shape = pymunk.Poly.create_box(body, size)
    shape.friction = 0.5
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_rampa(space: pymunk.Space, start: Tuple[float, float], end: Tuple[float, float], thickness: float = 6) -> None:
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, start, end, thickness)
    shape.friction = 0.7
    shape.elasticity = 0.2
    space.add(body, shape)

def crear_cuerda(space: pymunk.Space, puntos: List[Tuple[float, float]], radio: float = 3, body_fijo: pymunk.Body = None) -> List[pymunk.Body]:
    # Crea una cuerda como una serie de pequeños círculos conectados por PinJoint
    cuerpos = []
    prev_body = None
    for i, pos in enumerate(puntos):
        body = pymunk.Body(0.1, pymunk.moment_for_circle(0.1, 0, radio))
        body.position = pos
        shape = pymunk.Circle(body, radio)
        shape.friction = 0.9
        shape.elasticity = 0.1
        space.add(body, shape)
        if i == 0 and body_fijo is not None:
            # Engancha el primer segmento a la polea (body_fijo)
            joint = pymunk.PinJoint(body_fijo, body, (0,0), (0,0))
            space.add(joint)
        elif prev_body:
            joint = pymunk.PinJoint(prev_body, body, (0,0), (0,0))
            space.add(joint)
        cuerpos.append(body)
        prev_body = body
    return cuerpos

def crear_pentagono(space: pymunk.Space, position: Tuple[float, float], size: float = 20) -> pymunk.Body:
    # Crea un pentágono dinámico
    from math import pi, cos, sin
    mass = 1.0
    points = [(size * cos(2 * pi * i / 5), size * sin(2 * pi * i / 5)) for i in range(5)]
    body = pymunk.Body(mass, pymunk.moment_for_poly(mass, points))
    body.position = position
    shape = pymunk.Poly(body, points)
    shape.friction = 0.7
    shape.elasticity = 0.2
    space.add(body, shape)
    return body

def crear_palanca_animada(space: pymunk.Space, pivote: Tuple[float, float], extremo: Tuple[float, float], thickness: float = 8, mass: float = 1.0) -> pymunk.Body:
    # Palanca con pivote fijo en un extremo
    length = ((extremo[0] - pivote[0])**2 + (extremo[1] - pivote[1])**2)**0.5
    moment = pymunk.moment_for_box(mass, (length, thickness))
    body = pymunk.Body(mass, moment)
    body.position = ((pivote[0] + extremo[0]) / 2, (pivote[1] + extremo[1]) / 2)
    shape = pymunk.Poly.create_box(body, (length, thickness))
    shape.friction = 0.7
    shape.elasticity = 0.2
    # Pivote fijo
    static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    static_body.position = pivote
    joint = pymunk.PivotJoint(static_body, body, pivote)
    space.add(body, shape, static_body, joint)
    return body

# Aquí puedes agregar funciones adicionales para los mecanismos específicos de tu máquina de Goldberg (botellas, elevador, polea, carrito, etc.)
