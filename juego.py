import pygame
import serial
import threading
import queue
import random
import sys

WIDTH, HEIGHT = 400, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
FAST_FALL_STRENGTH = 10
PIPE_GAP = 150
PIPE_WIDTH = 70
PIPE_SPEED = 3

puerto_serial = "COM4"
baud_rate = 9600

jump_queue = queue.Queue()

def leer_serial(arduino, queue):
    try:
        while True:
            if arduino.in_waiting > 0:
                linea = arduino.readline().decode('utf-8', errors='ignore').strip()
                if linea:
                    print(f"[Arduino]: '{linea}'")
                    if linea == "JUMP":
                        queue.put(True)
    except serial.SerialException as e:
        print(f"Error serial: {e}")
    except OSError as e:
        if e.errno == 9:
            print(f"Error serial OSError (puerto cerrado): {e}")
        else:
            print(f"Error OSError inesperado: {e}")
    except Exception as e:
        print(f"Error inesperado en hilo serial: {e}")

class Bird:
    def __init__(self):
        self.x = 100
        self.y = HEIGHT // 2
        self.velocity = 0
        self.radius = 20

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def fast_fall(self):
        self.velocity = FAST_FALL_STRENGTH

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (self.x, int(self.y)), self.radius)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.height = random.randint(100, HEIGHT - PIPE_GAP - 100)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen):
        pygame.draw.rect(screen, (0, 255, 0), (self.x, 0, PIPE_WIDTH, self.height))
        bottom = self.height + PIPE_GAP
        pygame.draw.rect(screen, (0, 255, 0), (self.x, bottom, PIPE_WIDTH, HEIGHT - bottom))

    def collide(self, bird):
        bird_rect = pygame.Rect(bird.x - bird.radius, bird.y - bird.radius, bird.radius*2, bird.radius*2)
        top_pipe = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        bottom_pipe = pygame.Rect(self.x, self.height + PIPE_GAP, PIPE_WIDTH, HEIGHT - (self.height + PIPE_GAP))
        return bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe)

def game_loop(screen, clock, font, arduino):
    bird = Bird()
    pipes = [Pipe(WIDTH + 100)]
    score = 0
    running = True

    while running:
        clock.tick(FPS)
        screen.fill((135, 206, 235))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False  # para salir del juego completamente
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    bird.jump()
                elif event.key == pygame.K_DOWN:
                    bird.fast_fall()

        # Procesa saltos Arduino
        while not jump_queue.empty():
            jump_queue.get()
            bird.jump()

        bird.update()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.update()
            if pipe.collide(bird):
                running = False
            if pipe.x + PIPE_WIDTH < 0:
                rem.append(pipe)
            if not pipe.passed and pipe.x < bird.x:
                pipe.passed = True
                add_pipe = True
            pipe.draw(screen)

        if add_pipe:
            score += 1
            pipes.append(Pipe(WIDTH + 100))

        for r in rem:
            pipes.remove(r)

        if bird.y >= HEIGHT or bird.y <= 0:
            running = False

        bird.draw(screen)

        text = font.render(str(score), True, (255, 255, 255))
        screen.blit(text, (WIDTH // 2, 20))

        pygame.display.flip()

    # Pantalla Game Over
    screen.fill((0, 0, 0))
    msg = font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(msg, (WIDTH // 2 - 100, HEIGHT // 2 - 20))
    pygame.display.flip()
    pygame.time.wait(2000)

    return True  # para reiniciar el juego

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Flappy Bird con Arduino y Teclas")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 48)

    try:
        arduino = serial.Serial(puerto_serial, baud_rate, timeout=1)
    except Exception as e:
        print(f"No se pudo abrir el puerto serial: {e}")
        arduino = None

    if arduino:
        thread_serial = threading.Thread(target=leer_serial, args=(arduino, jump_queue), daemon=True)
        thread_serial.start()

    while True:
        continuar = game_loop(screen, clock, font, arduino)
        if not continuar:
            break

    if arduino:
        arduino.close()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Programa interrumpido por usuario")
        pygame.quit()
        sys.exit()
