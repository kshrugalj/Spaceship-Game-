import random as r
import pygame as pg
import sched
import time

gameEnded = False
score = 0
scoreMultiplier = 1

pg.init()

SCREENWIDTH = 1400
SCREENHEIGHT =  800

screen = pg.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
currVelocity = {'x': -0.5, 'y': 0}

# Load and resize player image
player_image = pg.image.load("spaceship_red.png")  # Assuming it's in the same directory
original_size = player_image.get_size()
scaled_size = (original_size[0] // 4, original_size[1] // 4)
player_image = pg.transform.scale(player_image, scaled_size)
player_image = pg.transform.rotate(player_image, 90)

# Load and resize asteroid image
asteroid_image = pg.image.load("asteroid.png")  # Assuming it's in the same directory
asteroid_image = pg.transform.scale(asteroid_image, (30, 30))

# Load and resize background image
background_image = pg.image.load("stars.jpg")  # Assuming it's in the same directory
background_image = pg.transform.scale(background_image, (SCREENWIDTH, SCREENHEIGHT))

player_rect = player_image.get_rect(topleft=(300, 250))

class Asteroid:
    def __init__(self, x, y, velocity):
        self.x = x
        self.y = y
        self.velocity = velocity

asteroids = []

def generate_asteroid():
    x = r.randrange(SCREENWIDTH)
    y = -50  # Start above the screen
    velocity = r.uniform(0.5, 1.5)  # Adjust the velocity range as needed
    asteroids.append(Asteroid(x, y, velocity))
    increase_score()

my_scheduler = sched.scheduler(time.time, time.sleep)

def call_generate_asteroid(scheduler):
    generate_asteroid()
    scheduler.enter(0.25, 1, call_generate_asteroid, (scheduler,))

my_scheduler.enter(1.0, 1, call_generate_asteroid, (my_scheduler,))

lost_text = pg.font.Font(None, 36).render('You Lost!', True, (255, 0, 0))
font = pg.font.Font(None, 36)

def increase_score():
    global score
    score += 1

def display_score():
    score_text = font.render(f"Current Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

def write_score_to_file(score):
    with open("scores.txt", "a") as file:
        file.write(str(score) + "\n")

def read_high_score_from_file():
    try:
        with open("scores.txt", "r") as file:
            scores = [int(line.strip()) for line in file.readlines()]
            return max(scores)
    except FileNotFoundError:
        return 0

while not gameEnded:
    screen.blit(background_image, (0, 0))  # Set the background image

    rotated_player = pg.transform.rotate(player_image, 90)
    screen.blit(rotated_player, player_rect)

    display_score()

    for asteroid in asteroids:
        screen.blit(asteroid_image, (asteroid.x, asteroid.y))
        asteroid.y += asteroid.velocity
        if asteroid.y > SCREENHEIGHT:
            asteroids.remove(asteroid)
        if player_rect.colliderect(pg.Rect(asteroid.x, asteroid.y, 30, 30)):
            screen.blit(lost_text, (SCREENWIDTH // 2 - 50, SCREENHEIGHT // 2))
            write_score_to_file(score)
            time.sleep(2)
            gameEnded = True

    high_score = read_high_score_from_file()
    high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 255))
    screen.blit(high_score_text, (SCREENWIDTH - 200, 10))

    for event in pg.event.get():
        if event.type == pg.QUIT:
            gameEnded = True
        if event.type == pg.KEYDOWN and event.key == pg.K_a:
            if not gameEnded:
                player_rect.x -= 10

    key = pg.key.get_pressed()
    if key[pg.K_a] and not gameEnded:
        player_rect.move_ip(-1, 0)
    if key[pg.K_d] and not gameEnded:
        player_rect.move_ip(1, 0)
    if key[pg.K_s] and not gameEnded:
        if player_rect.y > SCREENHEIGHT:
            player_rect.y = 0
        player_rect.move_ip(0, 1)
    if key[pg.K_w] and not gameEnded:
        if player_rect.y < 0:
            player_rect.y = SCREENHEIGHT
        player_rect.move_ip(0, -1)

    pg.display.update()
    my_scheduler.run(blocking=False)

pg.quit()