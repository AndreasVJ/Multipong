import pygame
import math
import random

pygame.init()

clock = pygame.time.Clock()
max_fps = 60

max_balls = 10
ball_spawn_rate = 5

window_width = 500
window_height = 700
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Multipong")

colors = [(0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), 
          (128, 255, 0), (255, 128, 0), (128, 0, 255), (255, 0, 128), (0, 255, 128), (0, 128, 255)]

font32 = pygame.font.Font("freesansbold.ttf", 32)
font20 = pygame.font.Font("freesansbold.ttf", 20)
game_over_text = font32.render("GAME OVER", True, (255, 0, 0))
restart_text = font20.render("Press 'r' to play again", True, (255, 255, 255))


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


player = MovableBlock(round(window_width/2) - round(window_width/6), round(window_height*0.9), 
                      round(window_width/3), round(window_height/40),
                      (255, 0, 0), window_width*2, 0)


balls = [MovableBlock(round(window_width/2), 100, 25, 25, (0, 255, 0), 200, math.pi/4)]


def addBall():

    if random.randint(0, 1):
        θ = random.uniform(math.pi/6, math.pi/3)
    else:
        θ = random.uniform(2*math.pi/3, 5*math.pi/6)

    size = round(25*(1 + random.uniform(-0.25, 0.25)))

    balls.append(MovableBlock(round(window_width*(0.5 + random.uniform(-0.3, 0.3))),
                              round(window_height*(0.1 + random.uniform(-0.1, 0.1))),
                              size, size, colors[random.randint(0, len(colors)-1)], 200, θ))
    


game_over = False
start_t = pygame.time.get_ticks()
previous_t = start_t

while True:

    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT or keys[pygame.K_q]:
            exit()

    if keys[pygame.K_r]:

        # Restart game
        player.x = round(window_height*0.4)
        balls = [MovableBlock(round(window_width/2), 100, 25, 25, (0, 255, 0), 200, math.pi/4)]
        start_t = pygame.time.get_ticks()
        game_over = False

    if not game_over:

        current_t = pygame.time.get_ticks()
        Δt = current_t - previous_t
        previous_t = current_t

        if (current_t - start_t) / (1000 * ball_spawn_rate) > len(balls) and len(balls) < max_balls:
            addBall()


        # Move player left
        if keys[pygame.K_LEFT]:
            player.move(-Δt)
            if player.horizontal_overlap(wall_west):
                player.x = wall_west.x + wall_west.width

        # Move player right
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
                game_over = True

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
        player.draw(window)

        if game_over:
            window.blit(game_over_text, (round(window_width/2)-100, round(window_height/2)))
            window.blit(restart_text, (round(window_width/2)-105, round(window_height/2) + 40))

        pygame.display.update()

    clock.tick(max_fps)