import pymunk
from typing import Tuple, List

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

def crear_rampa(space: pymunk.Space, start: Tuple[float, float], end: Tuple[float, float], thickness: float = 6) -> None:
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    shape = pymunk.Segment(body, start, end, thickness)
    shape.friction = 0.7
    shape.elasticity = 0.2
    space.add(body, shape)

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
    shape.friction = 0.12
    shape.elasticity = 0.2
    space.add(body, shape)
    return body

def crear_cuerda(space: pymunk.Space, puntos: List[Tuple[float, float]], radio: float = 3, body_fijo: pymunk.Body = None) -> List[pymunk.Body]:
    # Crea una cuerda como una serie de pequeños círculos conectados por SlideJoint con longitud fija (no se estira ni comprime)
    cuerpos = []
    prev_body = None
    for i, pos in enumerate(puntos):
        body = pymunk.Body(1.0, pymunk.moment_for_circle(1.0, 0, radio))
        body.position = pos
        shape = pymunk.Circle(body, radio)
        shape.friction = 0.9
        shape.elasticity = 0
        space.add(body, shape)
        if i == 0 and body_fijo is not None:
            dist = ((body.position[0] - body_fijo.position[0])**2 + (body.position[1] - body_fijo.position[1])**2)**0.5
            joint = pymunk.SlideJoint(body_fijo, body, (0,0), (0,0), dist, dist)
            space.add(joint)
        elif prev_body:
            dist = ((body.position[0] - prev_body.position[0])**2 + (body.position[1] - prev_body.position[1])**2)**0.5
            joint = pymunk.SlideJoint(prev_body, body, (0,0), (0,0), dist, dist)
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
    shape.friction = 0.14
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
    shape.friction = 5
    shape.elasticity = 0.2
    # Pivote fijo
    static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    static_body.position = pivote
    joint = pymunk.PivotJoint(static_body, body, pivote)
    space.add(body, shape, static_body, joint)
    return body
