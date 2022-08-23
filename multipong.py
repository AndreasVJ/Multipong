import pygame
import math
import random

pygame.init()

clock = pygame.time.Clock()
max_fps = 60

window_width = 500
window_height = 700
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Multipong")

colors = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255)]

class Block:
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color

    def draw(self, window):
        pygame.draw.rect(window, self.color, (self.x, self.y, self.width, self.height))


class MovableBlock(Block):
    def __init__(self, x, y, width, height, color, vel, θ):
        super().__init__(x, y, width, height, color)
        self.vel = vel
        self.θ = θ

    def move(self, Δt):
        self.x += self.vel*math.cos(self.θ) * (Δt/1000)
        self.y += self.vel*math.sin(self.θ) * (Δt/1000)
    
    def horizontal_overlap(self, block):
        # Returns how much overlap there is on the x-axis
        if (self.x >= block.x and self.x <= block.x + block.width):
            return block.x + block.width - self.x
        if (self.x + self.width >= block.x and self.x + self.width <= block.x + block.width):
            return self.x + self.width - block.x
        return False

    def vertical_overlap(self, block): 
        # Returns how much overlap there is on the y-axis
        if (self.y + self.height >= block.y and self.y + self.height <= block.y + block.height):
            return self.y + self.height - block.y
        if (self.y >= block.y and self.y <= block.y + block.height):
            return block.y + block.height - self.y
        return False

    
    def flip_horizontal_vel(self):
        self.θ = math.pi - self.θ

    def flip_vertical_vel(self):
        self.θ = 2*math.pi - self.θ


wall_thickness = 20
wall_north = Block(0, -wall_thickness, window_width, wall_thickness, (0, 0, 255))
wall_east = Block(window_width, 0, wall_thickness, window_height, (0, 0, 255))
wall_south = Block(0, window_height, window_width, wall_thickness, (0, 0, 255))
wall_west = Block(-wall_thickness, 0, wall_thickness, window_height, (0, 0, 255))


player = MovableBlock(round(window_height*0.4), round(window_height*0.9), 
                      round(window_height/10), round(window_height/40),
                      (255, 0, 0), window_height * 0.75, 0)


# balls = []
balls = [MovableBlock(round(window_width/2), 100, 25, 25, (0, 255, 0), 200, math.pi/4)]


def addBall():
    balls.append(MovableBlock(round(window_width/2), window_height*0.1, 25, 25,
                 colors[random.randint(0, len(colors))], 200, random.uniform(math.pi/4, 3*math.pi/4)))


addBall()
addBall()
addBall()
    


game_over = False
previous_t = pygame.time.get_ticks()

while not game_over:

    current_t = pygame.time.get_ticks() + 1
    Δt = current_t - previous_t
    previous_t = current_t

    keys = pygame.key.get_pressed()

    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_q]:
            game_over = True

    if keys[pygame.K_LEFT]:
        player.move(-Δt)
        if player.horizontal_overlap(wall_west):
            player.x = wall_west.x + wall_west.width

    elif keys[pygame.K_RIGHT]:
        player.move(Δt)
        if player.horizontal_overlap(wall_east):
            player.x = wall_east.x - player.width


    for i, ball in enumerate(balls):

        ball.move(Δt)

        if ball.horizontal_overlap(wall_east) or ball.horizontal_overlap(wall_west):
            ball.flip_horizontal_vel()

        if ball.vertical_overlap(wall_north):
            ball.flip_vertical_vel()

        if ball.vertical_overlap(wall_south):
            ball.flip_vertical_vel()

        # Check collision with all other balls
        for n, ba in enumerate(balls):
            if n != i:
                horizontal_overlap = ball.horizontal_overlap(ba)
                vertical_overlap = ball.vertical_overlap(ba)

                if horizontal_overlap and vertical_overlap:
                    if (horizontal_overlap > vertical_overlap):
                        ball.flip_vertical_vel()
                    elif (vertical_overlap > horizontal_overlap):
                        ball.flip_horizontal_vel()


        # Check collision with player
        horizontal_overlap = ball.horizontal_overlap(player)
        vertical_overlap = ball.vertical_overlap(player)

        if horizontal_overlap and vertical_overlap:
            if (horizontal_overlap > vertical_overlap):
                ball.flip_vertical_vel()
            elif (vertical_overlap > horizontal_overlap):
                ball.flip_horizontal_vel()
    
    
    # Clear previous frame
    window.fill((0, 0, 0))

    # Draw new frame
    for ball in balls:
        ball.draw(window)

    pygame.draw.rect(window, (255, 0, 0), (player.x, player.y, player.width, player.height))

    clock.tick(max_fps)
    pygame.display.update()