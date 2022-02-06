import math
import random
from turtle import width
import pygame

import time

from sympy import false, true

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# initialize pygame
pygame.init()
SCREEN_HEIGHT = 720
SCREEN_LENGTH = 500
screen_size = (SCREEN_LENGTH, SCREEN_HEIGHT)

# create a window
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("pygame Test")

# clock is used to set a max fps
clock = pygame.time.Clock()
prev_time = time.time()

# sprites
background = pygame.transform.scale(pygame.image.load(
    "cheese background.png").convert(), (SCREEN_LENGTH, SCREEN_HEIGHT))
becky_ball = pygame.transform.scale(pygame.image.load(
    "becky ball.png").convert(), (15, 15))
paddle_sprite = pygame.transform.scale(pygame.image.load(
    "paddle.png").convert(), (60, 10))
cheese_sprites = [pygame.transform.scale(pygame.image.load("cheese.png").convert(), (0, 0)),
                  pygame.transform.scale(pygame.image.load(
                      "cheese.png").convert(), (60, 30)),
                  pygame.transform.scale(pygame.image.load(
                      "cheese2.png").convert(), (60, 30)),
                  pygame.transform.scale(pygame.image.load("cheese1.png").convert(), (60, 30))]


class Paddle:
    def __init__(self):
        self.length = 60
        self.width = 10
        self.x = 220
        self.y = 710
        self.LEFT = False
        self.RIGHT = False
        self.speed = 2

    def render(self, screen):
        pygame.draw.rect(screen, WHITE, pygame.Rect(
            self.x, self.y, self.length, self.width))
        screen.blit(paddle_sprite, (self.x, self.y))

    def update(self):
        if self.LEFT:
            self.x -= self.speed * 1
        if self.RIGHT:
            self.x += self.speed * 1

        if self.x < 0:
            self.x = 0
        elif self.x + self.length > SCREEN_LENGTH:
            self.x = SCREEN_LENGTH - self.length


paddle = Paddle()


class Ball:
    def __init__(self, x, y, velocity=[3, -3]):
        self.size = 15
        self.x = x
        self.y = y
        self.speed = 0.4
        self.velocity = velocity

    def hflip(self):
        self.velocity = [self.velocity[0] * -1, self.velocity[1]]

    def vflip(self):
        self.velocity = [self.velocity[0], self.velocity[1] * -1]

    def render(self, screen):
        pygame.draw.rect(screen, BLACK, pygame.Rect(
            self.x, self.y, self.size, self.size), 5)
        screen.blit(becky_ball, (self.x, self.y))

    def update(self, bricks):
        self.x += self.velocity[0] * self.speed
        self.y += self.velocity[1] * self.speed

        # wall detection
        if self.x < 0:
            self.x = 0
            self.hflip()
        elif self.x + self.size > SCREEN_LENGTH:
            self.x = SCREEN_LENGTH - self.size
            self.hflip()
        if self.y < 0:
            self.y = 0
            self.vflip()

        # paddle detection
        if self.y > SCREEN_HEIGHT - paddle.width:
            ballpos = self.x+self.size/2
            padpos = paddle.x + paddle.length/2
            vector_size = (self.velocity[0]**2+self.velocity[1]**2)**(1/2)
            if abs(padpos-ballpos) < paddle.length/6:
                print("a")
                self.velocity[1] = vector_size * math.sin(math.pi/2)
                self.velocity[0] = vector_size * math.cos(math.pi/2)
                
            elif abs(padpos-ballpos) < paddle.length*2/6:
                print("b")
                self.velocity[1] = vector_size * math.sin(math.pi/4)
                self.velocity[0] = vector_size * math.cos(math.pi/4)
            else:
                print("c")
                self.velocity[1] = vector_size * math.sin(math.pi/6)
                self.velocity[0] = vector_size * math.cos(math.pi/6)
            if padpos-ballpos > 0:
                self.velocity[0]*=-1
            if self.x+self.size/2 > paddle.x and self.x+self.size/2 < paddle.x + paddle.length:
                self.vflip()
        if self.y > SCREEN_HEIGHT:
            print("LOSER")
            return True

        # brick detection
        for brick in bricks:
            hitbox = pygame.Rect(self.x, self.y, self.size, self.size)
            if hitbox.colliderect(brick.rect):
                self.vflip()
                delete = brick.hit()
                if delete:
                    bricks.remove(brick)


balls = [Ball(220, 700)]


class Brick:
    def __init__(self, x, y, health=1):
        self.x = x
        self.y = y
        self.width = 60
        self.height = 30
        self.health = health
        self.alive = True
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.showHitbox = False

    def render(self, screen):
        screen.blit(cheese_sprites[self.health], (self.x, self.y))
        if self.showHitbox:
            pygame.draw.rect(screen, RED, pygame.Rect(
                self.x, self.y, self.width, self.height))

    def hit(self):
        self.health -= 1

        if self.health <= 0:
            self.alive = False
            return True


bricks = []


class FrenzyBrick(Brick):
    def __init__(self, x, y, health=1):
        super().__init__(x, y, health)

    def hit(self):
        self.health -= 1

        if self.health <= 0:
            self.alive = False
            for i in range(2):
                angle = random.randint(0, 360)
                balls.append(Ball(self.x+30, self.y,
                             [math.cos(angle)*4.25, 4.25*math.sin(angle)]))
            return True


class LongnessBrick(Brick):
    def __init__(self, x, y, health=1):
        super().__init__(x, y, health)

    def hit(self):
        global paddle_sprite
        self.health -= 1

        if self.health <= 0:
            self.alive = False
            paddle_sprite = pygame.transform.scale(pygame.image.load(
                "paddle.png").convert(), (120, 10))
            paddle.length *= 2
            return True


def update():
    paddle.update()
    for ball in balls:
        delete = ball.update(bricks)
        if delete:
            balls.remove(ball)


def render(msg=None):
    global prev_time
    now = time.time()
    # print(round(1/(now-prev_time)))
    prev_time = now

    screen.fill(BLACK)
    screen.blit(background, (0, 0))
    paddle.render(screen)

    for brick in bricks:
        brick.render(screen)

    for ball in balls:
        ball.render(screen)

    if msg:
        words = pygame.font.SysFont('Comic Sans', 50).render(
            msg, True, GREEN)
        screen.blit(words, (SCREEN_LENGTH/2-80, SCREEN_HEIGHT/2))
    if not game_start:
        pygame.draw.line(screen, BLACK, ((SCREEN_LENGTH/2), SCREEN_HEIGHT),
                         ((SCREEN_LENGTH/2) + math.cos(LAUNCH_ANGLE) * 60, -60*math.sin(LAUNCH_ANGLE) + SCREEN_HEIGHT), 4)


LAUNCH_ANGLE = math.pi/2
ALEFT, ARIGHT = False, False
game_start = False


def load_level(L):
    global bricks, paddle, balls, game_start
    game_start = False
    bricks = []
    paddle = Paddle()
    balls = []
    if 1 == L:
        for i in range(5):
            for j in range(4):
                bricks.append(Brick(55 + j*65, 50 + i*35))
            bricks.append(Brick(55 + 4*65, 50 + i*35, health=2))
            bricks.append(Brick(55 + 5*65, 50 + i*35, health=3))
        bricks.append(FrenzyBrick(300, 500))
        bricks.append(LongnessBrick(100, 500))
        #balls.append(Ball(0, 700))
    elif 2 == L:
        pass
    elif 3 == L:
        pass
    elif 4 == L:
        pass
    elif 5 == L:
        pass


CURRENT_LEVEL = 1
load_level(CURRENT_LEVEL)
message = None


def pause():
    words = pygame.font.SysFont('Comic Sans MS', 35, bold=True).render(
        "YOU LOSE", True, BLACK)
    screen.blit(words, (SCREEN_LENGTH/2-80, SCREEN_HEIGHT/2))
    p = 1
    while p:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    return

        pygame.display.update()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_start:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    paddle.LEFT = True
                if event.key == pygame.K_RIGHT:
                    paddle.RIGHT = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    paddle.LEFT = False
                if event.key == pygame.K_RIGHT:
                    paddle.RIGHT = False
        else:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ALEFT = True
                if event.key == pygame.K_RIGHT:
                    ARIGHT = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    ALEFT = False
                if event.key == pygame.K_RIGHT:
                    ARIGHT = False
                if event.key == pygame.K_SPACE:
                    game_start = True
                    balls.append(Ball(240, 701, velocity=[math.cos(
                        LAUNCH_ANGLE)*4.25, -4.25*math.sin(LAUNCH_ANGLE)]))

    if ALEFT:
        LAUNCH_ANGLE += 0.01
    if ARIGHT:
        LAUNCH_ANGLE -= 0.01
    if LAUNCH_ANGLE < math.pi*.10:
        LAUNCH_ANGLE = math.pi*.10
    if LAUNCH_ANGLE > math.pi*.90:
        LAUNCH_ANGLE = math.pi*.9

    if len(bricks) == 0 and game_start:
        print("Level Cleared")
        render("YOU WIN")
        pygame.time.wait(1000)
        CURRENT_LEVEL += 1

        load_level(CURRENT_LEVEL)

    if len(balls) == 0 and game_start:

        print("A")
        #render("YOU LOSE")
        pause()
        print("B")
        CURRENT_LEVEL = 1
        load_level(CURRENT_LEVEL)

    update()
    render(message)
    pygame.display.flip()
    clock.tick(240)

pygame.quit()
