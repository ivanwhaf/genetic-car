import sys
import time
import math
import pygame as pg  # install
from pygame.locals import *
from nn import *

pg.init()
size = width, height = 1060, 700  # screen size
screen = pg.display.set_mode(size)
pg.display.set_caption("Genetic algorithm car")

background = pg.image.load('resources/bg2.png')  # lodad background imgage

num = 100  # samples number per loop
generation = 100  # iteration round number

cross_ratio = 0.3  # ratio of top performers when crossovering
elite_ratio = 0.1  # elite ratio of all samples
mutate_ratio = 0.2  # mutation ratio

pm = 0.4  # probability of mutation
mutation_range = 0.2  # range of mutation -~+

FPS = 60  # fps setting
count = 0
fps = 0
start = time.time()
clock = pg.time.Clock()

my_font = pg.font.Font(None, 25)  # font setting

x, y = 385, 400  # car's initial position
max_speed = 10  # car's max limit speed


def change_angle(gs):
    # modify angle
    global angle
    angle = 0

    if angle <= -180:
        angle = 180


def draw_text(text, pos, color):
    img = my_font.render(
        text, True, color)
    screen.blit(img, pos)


def boundary_detect():
    # arrive at the boundary then stop
    global speed, x, y
    if x <= 0:
        x = 0
        speed = 0
    if x >= width:
        x = width
        speed = 0
    if y <= 0:
        y = 0
        speed = 0
    if y >= height:
        y = height
        speed = 0


class Car:
    """
    car class,including position,speed,and some status.
    """

    def __init__(self):
        # position and angle
        self.x = x
        self.y = y
        self.angle = 45
        self.speed = 1

        # live status
        self.isAlive = True

        # three distance indicator lines' end point positions
        self.x1 = 0
        self.y1 = 0
        self.y2 = 0
        self.y2 = 0
        self.x3 = 0
        self.y3 = 0

        # three distance from the track boundary
        self.dis1 = 0
        self.dis2 = 0
        self.dis3 = 0

        # total running distance
        self.distance = 0

        # judge reward line flag
        self.flag = False

    def set_position(self):
        # update position and distance according to angle and speed
        if not self.isAlive:
            return
        angle = math.pi*(-self.angle)/180
        x = self.x + self.speed*math.cos(angle)
        y = self.y + self.speed*math.sin(angle)
        distance = math.sqrt((x-self.x)**2+(y-self.y)**2)
        self.distance += distance
        self.x = x
        self.y = y

    def detect_track_boundary(self):
        # if screen.get_at((int(self.x), int(self.y))) == (0, 0, 0, 255):
        pixel = screen.get_at((int(self.x), int(self.y)))
        if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
            self.isAlive = False
        if self.distance <= 0:
            self.isAlive = False

    def detect_markline(self, i):
        # detect yellow reward line then reward
        if screen.get_at((int(self.x), int(self.y))) == ((255, 243, 0, 255) or (255, 242, 0, 255)):
            if not self.flag:
                self.distance += 500  # reward
                print('reward '+str(i))
                self.flag = True
        else:
            if self.flag == True:
                self.flag = False

        # detect red start line then punish
        pixel = screen.get_at((int(self.x), int(self.y)))
        if abs(pixel[0]-237) <= 1 and abs(pixel[1]-29) <= 1 and abs(pixel[2]-36) <= 1:
            self.distance -= 1000  # punish
            print('punish '+str(i))

    def draw_indicator_line(self):
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x1, self.y1), 1)
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x2, self.y2), 1)
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x3, self.y3), 1)

    def calculate_distance(self):
        # calculate car's three angles' distances form the track boundary
        if not self.isAlive:
            return
        x = self.x
        y = self.y
        angle = self.angle

        ang1 = angle+55
        ang2 = angle
        ang3 = angle-55

        angle1 = math.pi*(ang1)/180
        angle2 = math.pi*(ang2)/180
        angle3 = math.pi*(ang3)/180

        d = 12
        for i in range(1000):
            x1 = x+i*math.cos(angle1)
            y1 = y-i*math.sin(angle1)
            # detect track boundary (black color)
            pixel = screen.get_at((int(x1), int(y1)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                # if screen.get_at((int(x1), int(y1))) == ((0, 0, 0, 255) or (0, 1, 0, 255)):
                self.x1, self.y1 = x1, y1
                self.dis1 = math.sqrt((x-x1)**2+(y-y1)**2)/d
                break

        for i in range(1000):
            x2 = x+i*math.cos(angle2)
            y2 = y-i*math.sin(angle2)
            # detect track boundary (black color)
            pixel = screen.get_at((int(x2), int(y2)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                # if screen.get_at((int(x2), int(y2))) == ((0, 0, 0, 255) or (0, 1, 0, 255)):
                self.x2, self.y2 = x2, y2
                self.dis2 = math.sqrt((x-x2)**2+(y-y2)**2)/d
                break

        for i in range(1000):
            x3 = x+i*math.cos(angle3)
            y3 = y-i*math.sin(angle3)
            # detect track boundary (black color)
            pixel = screen.get_at((int(x3), int(y3)))
            if pixel[0] <= 1 and pixel[1] <= 1 and pixel[2] <= 1:
                # if screen.get_at((int(x3), int(y3))) == ((0, 0, 0, 255) or (0, 1, 0, 255)):
                self.x3, self.y3 = x3, y3
                self.dis3 = math.sqrt((x-x3)**2+(y-y3)**2)/d
                break

    def draw(self, color='blue'):
        # draw car itself
        if color == 'blue':
            pg.draw.circle(screen, (0, 0, 255), (int(
                self.x), int(self.y)), 7, 0)  # replace car as circle
        elif color == 'yellow':
            pg.draw.circle(screen, (255, 255, 0), (int(
                self.x), int(self.y)), 7, 0)  # replace car as circle


def sort_car_nets(cars, nets):
    """
    sort cars,nets by their running distance, big-->small
    """
    for i in range(len(cars)-1):
        for j in range(i+1, len(cars)):
            if cars[i].distance < cars[j].distance:
                # swap
                temp = cars[i]
                cars[i] = cars[j]
                cars[j] = temp
                # swap
                temp = nets[i]
                nets[i] = nets[j]
                nets[j] = temp
    return cars, nets


def main_loop():
    global start, fps, count
    run = True  # running status
    pause = False  # pause status
    begin = time.time()
    last_round_time = begin
    gen = 1

    # create cars
    cars = []
    for i in range(num):
        car = Car()
        cars.append(car)

    # create networks
    nets = []
    for i in range(num):
        nets.append(NeuralNetwork())

    # main loop
    while run:
        clock.tick(FPS)  # set fps
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:  # Key 'P' to pause
                    pause = not pause

        if pause:
            continue

        # calculate fps
        count += 1
        now = time.time()
        if now-start > 0.1:
            fps = count/(now-start)
            start = now
            count = 0

        screen.blit(background, (0, 0))  # draw background

        for i in range(len(cars)):
            if cars[i].isAlive:
                # calculate distance from car to track boundary
                cars[i].calculate_distance()
                angle, speed = nets[i].feedforward(
                    [cars[i].dis1, cars[i].dis2, cars[i].dis3])  # get network's output

                # update car's properties
                speed = abs(speed)*10
                cars[i].angle = angle*180
                if speed > max_speed:
                    speed = max_speed
                cars[i].speed = speed

                cars[i].set_position()  # update position
                cars[i].detect_markline(i)  # detect reward line and start line
                cars[i].detect_track_boundary()  # detect collide
                nets[i].score = cars[i].distance  # update network's score

        print(cars[0].angle)
        if time.time()-last_round_time > 30:
            for i in range(len(cars)):
                if cars[i].isAlive:
                    cars[i].distance = 0
                    cars[i].isAlive = False
        cars, nets = sort_car_nets(cars, nets)

        # drawing part
        alive = 0  # survive numbers
        for i in range(len(cars)):
            if i == 0:
                cars[i].draw('yellow')  # No.1 marked yellow
            else:
                cars[i].draw()  # draw car itself
            if cars[i].isAlive:
                alive += 1
                cars[i].draw_indicator_line()  # draw three indicator line

        draw_text("Gen: "+str(gen), (900, 10), (0, 0, 255))
        draw_text("All: "+str(len(cars)), (900, 30), (0, 0, 255))
        draw_text("Alive: "+str(alive), (900, 50), (0, 0, 255))
        draw_text("top1 distance: " +
                  str(int(cars[0].distance)), (900, 70), (0, 0, 255))
        draw_text("total time: " +
                  str(int(time.time()-begin)), (900, 90), (0, 0, 255))
        draw_text("this round time: " +
                  str(int(time.time()-last_round_time)), (900, 110), (0, 0, 255))

        draw_text("fps:"+str(round(fps, 5)), (10, 10), (0, 0, 255))
        mouse_pos_x, mouse_pos_y = pg.mouse.get_pos()  # get mouse's position
        draw_text('pos_x:'+str(mouse_pos_x)+'  pos_y:' +
                  str(mouse_pos_y), (10, 30), (0, 0, 255))
        draw_text(str(screen.get_at((mouse_pos_x, mouse_pos_y))),
                  (10, 70), (0, 0, 255))
        draw_text("press 'p' to pause!", (10, 50), (0, 0, 255))

        # pg.display.flip() #  redraw window
        pg.display.update()

        # when this gen was over
        if alive == 0:
            # top 1/4 elite networks
            elites = get_elites(nets, elite_ratio)

            # next generation's networks list
            next_gen_nets = []

            # add this generation's elites directly to next generation
            next_gen_nets.extend(elites)

            # create hybrid children and add them to next geration until enough
            for i in range(num-len(elites)):
                child = crossover(nets, cross_ratio)
                next_gen_nets.append(child)

            # mutate next generation's every network including elites and children
            next_gen_nets = mutation(next_gen_nets, pm, mutate_ratio)

            # recreate new cars
            cars = []
            for i in range(num):
                car = Car()
                cars.append(car)

            nets = next_gen_nets
            gen += 1
            last_round_time = time.time()
            # quit when gen was enough
            if gen > generation:
                break
    pg.quit()


main_loop()
