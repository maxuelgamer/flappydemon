import pygame
from pygame.locals import *
import random
import pickle

def main():
    SCREEN_WIDTH = 400
    SCREEN_HEIGHT = 800

    SPEED = 0
    GRAVITY = 0
    GAME_SPEED = 0

    GROUND_WIDTH = 2 * SCREEN_WIDTH
    GROUND_HEIGHT = 100

    PIPE_WIDTH = 100
    PIPE_HEIGHT = 500
    PIPE_GAP = 200

    TIMER = 0
    TIME_SECONDS = 0

    STARTED = False

    
    SCORE = open(r'files\score.pkl', 'rb')
    HIGHSCORE = pickle.load(SCORE)
    


    class Bird(pygame.sprite.Sprite):
        
        def __init__(self):
            pygame.sprite.Sprite.__init__(self)

            self.images = [pygame.image.load(r'files\bluebird-upflap.png').convert_alpha(),
                        pygame.image.load(r'files\bluebird-midflap.png').convert_alpha(),
                        pygame.image.load(r'files\bluebird-downflap.png').convert_alpha()]

            self.speed = SPEED               

            self.current_image = 0               

            self.image = pygame.image.load(r'files\bluebird-upflap.png').convert_alpha()
            self.mask = pygame.mask.from_surface(self.image)

            self.rect = self.image.get_rect()
            self.rect[0] = SCREEN_WIDTH / 2
            self.rect[1] = SCREEN_HEIGHT / 2


        def update(self):
            self.current_image = (self.current_image + 1) % 3
            self.image = self.images[ self.current_image ]

            self.speed += GRAVITY

            # Update Height // Altura

            self.rect[1] += self.speed


        def bump(self):
            wing_sound = pygame.mixer.Sound(r'files\sfx_wing.wav')            
            wing_sound.play()
            self.speed = -SPEED

    class Pipe(pygame.sprite.Sprite):

        def __init__(self, inverted, xpos, ysize):
            pygame.sprite.Sprite.__init__(self)

            self.image = pygame.image.load(r'files\pipe-red.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (PIPE_WIDTH, PIPE_HEIGHT))

            self.rect = self.image.get_rect()
            self.rect[0] = xpos

            if inverted:
                self.image = pygame.transform.flip(self.image,False, True)
                self.rect[1] = - (self.rect[3] - ysize)
            else:
                self.rect[1] = SCREEN_HEIGHT - ysize    

            self.mask = pygame.mask.from_surface(self.image)    
        def update(self):
            self.rect[0] -= GAME_SPEED

    class Ground(pygame.sprite.Sprite):

        def __init__(self, xpos):
            pygame.sprite.Sprite.__init__(self)
            
            self.image = pygame.image.load(r'files\base.png').convert_alpha()
            self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))
            self.mask = pygame.mask.from_surface(self.image)

            self.rect = self.image.get_rect()
            self.rect[0] = xpos
            self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

        def update(self):
            self.rect[0] -= GAME_SPEED

    def is_off_screen(sprite):
        return sprite.rect[0] < -(sprite.rect[2])   

    def get_random_pipes(xpos):
        size = random.randint(100, 300)
        pipe = Pipe(False, xpos, size)
        pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
        return(pipe, pipe_inverted)

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 

    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)

    ground_group = pygame.sprite.Group()
    for i in range(2): 
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range(2): 
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    font = pygame.font.SysFont('arial-black', 30)
    texto = font.render("Tempo: 0",True,(255,255,255),None)
    fontscore = pygame.font.SysFont('arial-black', 40)
    
    highscoretxt = fontscore.render(str(HIGHSCORE),True,(255,255,255),None)
    
    
    while True:
        pygame.time.delay(25)
        for event in pygame.event.get():
            if STARTED:
                highscoretxt = fontscore.render("",True,(255,255,255),None)
                if event.type == QUIT:
                    pygame.quit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        bird.bump()
            else:
                if event.type == QUIT:
                    pygame.quit()
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        SPEED = 10
                        GRAVITY = 1
                        GAME_SPEED = 10    
                        STARTED = True        

        if STARTED:
            BACKGROUND = pygame.image.load(r'files\background-day.png')
            BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT)) 
        else:    
            BACKGROUND = pygame.image.load(r'files\startscreen.png')
            BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))
            
            
        
        screen.blit(BACKGROUND, (0, 0))  

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDTH * 2)

            pipe_group.add(pipes[0]) 
            pipe_group.add(pipes[1])

        screen.blit(highscoretxt, dest=(SCREEN_WIDTH/2-15, 100))

        if STARTED:
            bird_group.update()      
            ground_group.update()      
            pipe_group.update()      

            bird_group.draw(screen)
            pipe_group.draw(screen)
            ground_group.draw(screen)
            screen.blit(texto, dest=(20, 10))
            if (TIMER < 40):
                TIMER += 1
            else: 
                TIME_SECONDS += 1 
                texto = font.render("Tempo: "+str(TIME_SECONDS),True,(255,255,255),None)
                TIMER = 0 


        

        if (pygame.sprite.groupcollide(bird_group, ground_group, True, True, pygame.sprite.collide_mask) or 
        pygame.sprite.groupcollide(bird_group, pipe_group, True, True, pygame.sprite.collide_mask)) :
            # Read the highscore from a file using pickle

            if TIME_SECONDS > HIGHSCORE:
                scorefile = open(r'files\score.pkl', 'wb')
                scorew = TIME_SECONDS
                pickle.dump(scorew, scorefile) # Saving in external file
                scorefile.close()

            hit_sound = pygame.mixer.Sound(r'files\sfx_hit.wav')            
            hit_sound.play()    
            GAME_SPEED = 0
            pygame.time.delay(1000)    
            die_sound = pygame.mixer.Sound(r'files\sfx_die.wav')            
            die_sound.play()
            pygame.time.delay(500)  

            main()


        pygame.display.update()
        pygame.display.set_caption("FlappyDemon")

main()        
