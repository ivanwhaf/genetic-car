import sys
import time
import math
import pygame as pg  # install
from pygame.locals import *
from nn import *

pg.init()
size = width, height = 1060, 700  # 屏幕大小
screen = pg.display.set_mode(size)
pg.display.set_caption("Genetic algorithm car")

background = pg.image.load('bg4.png')

num = 50  # 每轮样本数量
generation = 100  # 迭代轮数
pm = 0.5  # 变异率
ratio = 0.25  # 变异比率
FPS = 60  # fps设定值
count = 0
fps = 0
start = time.time()
clock = pg.time.Clock()

my_font = pg.font.Font(None, 25)  # 字体设置

x, y = 380, 406  # 小车初始位置
max_speed = 15  # 小车最大速度


def change_angle(gs):
    # 调整角度
    global angle
    angle = 0

    if angle <= -180:
        angle = 180


def draw_text(text, pos, color):
    # 绘制字符
    img = my_font.render(
        text, True, color)
    screen.blit(img, pos)


def boundary_detect():
    # 边界检测
    # 到达边界则停下
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
    car class,including position
    """

    def __init__(self):
        # position and angle
        self.x = x
        self.y = y
        self.angle = 45
        self.speed = 1

        # live status
        self.isAlive = True

        # three distance indicator lines' postions
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

        self.flag = False

    def set_position(self):
        # 根据角度和速度更新坐标、行驶距离
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

    def detect_markline(self):
        if screen.get_at((int(self.x), int(self.y))) == ((255, 243, 0, 255) or (255, 242, 0, 255)):
            if not self.flag:
                self.distance += 300
                print('wow')
                self.flag = True
        else:
            if self.flag == True:
                self.flag = False

    def draw_indicator_line(self):
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x1, self.y1), 1)
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x2, self.y2), 1)
        pg.draw.line(screen, (0, 255, 0), (self.x, self.y),
                     (self.x3, self.y3), 1)

    def calculate_distance(self):
        """
        calculate car's three angles' distances form the track boundary
        """
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
        if color == 'blue':
            pg.draw.circle(screen, (0, 0, 255), (int(
                self.x), int(self.y)), 7, 0)  # 绘制圆代替小车
        elif color == 'yellow':
            pg.draw.circle(screen, (255, 255, 0), (int(
                self.x), int(self.y)), 7, 0)  # 绘制圆代替小车


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

                temp = nets[i]
                nets[i] = nets[j]
                nets[j] = temp
    return cars, nets


def main_loop():
    global start, fps, count
    run = True  # 运行标志
    pause = False  # 暂停标志

    gen = 1
    # 生成车
    cars = []
    for i in range(num):
        car = Car()
        cars.append(car)

    # 生成神经网络
    nets = []
    for i in range(num):
        nets.append(NeuralNetwork())

    # 主循环
    while run:
        clock.tick(FPS)  # 设置fps
        for event in pg.event.get():
            if event.type == pg.QUIT:
                run = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:  # P键暂停
                    pause = not pause

        if pause:
            continue

        # 计算fps
        count += 1
        now = time.time()
        if now-start > 0.1:
            fps = count/(now-start)
            start = now
            count = 0

        screen.blit(background, (0, 0))  # 绘制背景地图

        for i in range(len(cars)):
            if cars[i].isAlive:
                cars[i].calculate_distance()  # 计算与车道边缘距离
                angle, speed = nets[i].feedforward(
                    [cars[i].dis1, cars[i].dis2, cars[i].dis3])  # get network's output
                # update car's properties
                speed = abs(speed)*8

                cars[i].angle = angle*180
                if speed > max_speed:
                    speed = max_speed

                cars[i].speed = speed
                cars[i].set_position()  # 更新位置
                cars[i].detect_markline()  # 检测加分线
                cars[i].detect_track_boundary()  # 碰撞检测
                nets[i].score = cars[i].distance

        cars, nets = sort_car_nets(cars, nets)

        # 绘图部分
        alive = 0  # 存活数量
        for i in range(len(cars)):
            if i == 0:
                cars[i].draw('yellow')  # 第一名用黄色
            else:
                cars[i].draw()  # 绘制小车自身
            if cars[i].isAlive:
                alive += 1
                cars[i].draw_indicator_line()  # 绘制距离指示线

        draw_text("Gen: "+str(gen), (900, 10), (0, 0, 255))
        draw_text("All: "+str(len(cars)), (900, 30), (0, 0, 255))
        draw_text("Alive: "+str(alive), (900, 50), (0, 0, 255))
        draw_text("top1 distance: " +
                  str(int(cars[0].distance)), (900, 70), (0, 0, 255))

        draw_text("fps:"+str(round(fps, 5)), (10, 10), (0, 0, 255))  # 绘制fps
        mouse_pos_x, mouse_pos_y = pg.mouse.get_pos()  # 获取鼠标坐标
        draw_text('pos_x:'+str(mouse_pos_x)+'  pos_y:' +
                  str(mouse_pos_y), (10, 30), (0, 0, 255))  # 绘制鼠标坐标
        draw_text(str(screen.get_at((mouse_pos_x, mouse_pos_y))),
                  (10, 70), (0, 0, 255))  # 绘制鼠标坐标

        draw_text("press 'p' to pause!", (10, 50), (0, 0, 255))  # 绘制注意事项

        # pg.display.flip() #  重新绘制窗口
        pg.display.update()

        # this gen over
        if alive == 0:
            # top 1/4 elite networks
            elites = get_elites(nets, 0.1)

            # next generation's networks list
            next_gen_nets = []

            # add this generation's elites directly to next generation
            next_gen_nets.extend(elites)

            # create hybrid children and add them to next geration until enough
            for i in range(num-len(elites)):
                child = crossover(nets)
                next_gen_nets.append(child)

            # mutate next generation's every network including elites
            next_gen_nets = mutation(next_gen_nets, pm, ratio)

            cars = []
            for i in range(num):
                car = Car()
                cars.append(car)

            nets = next_gen_nets
            gen += 1

    pg.quit()


main_loop()
