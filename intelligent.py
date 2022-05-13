import argparse
import math
import random
from statistics import mean
from tkinter import *
import numpy as np
import time
import pickle
class Field:
    WIDTH = 2000
    HEIGHT = 750


# class Coordinate():
#     def __init__(self):
#         self.reset()
#
#     def reset(self):
#         self.pos=np.array([0,0])


class Bird():
    NUM = 40
    smartCount = 10
    RADIAN = 3
    SPEED = 4
    ACCUP = 0.2
    # srcSquare = [25, 325, 125, 425]
    # desSquare = [875, 325, 975, 425]
    srcSquare = [25, 325, 125, 425]
    desSquare = [850, 300, 1000, 450]
    des = np.array([desSquare[2], (desSquare[1]+desSquare[3])/2])

    ## parameters
    r = [1] * 10
    r[0] = 0.1     # cohesion coefficient
    r[1] = 1     # separation coefficient
    r[2] = 1     # alignment coefficient
    r[3] = 0.4        # intelligent coefficient
    #r[4]=1           # acceleration noise
    center_pull = 30
    view = 50



    maxiteration=400
    iteration = 0
    measurement={
        'deviation': [],
        'avevel': [],                # average velocity
        'avevelproj': [],     # average velocity projected to the direction to the destination
        'allarrival': maxiteration+1
    }
    # 생성자
    def __init__(self):

        self.pos = np.random.rand(2)*50+np.array([50, 350])
        #self.poss=[]
        self.v = np.zeros(2)

        # self.r=[0]*10
        # self.r[0] = args.r0
        # self.r[1] = args.r1
        # self.r[2] = args.r2
        # self.r[3] = args.r3
        # self.center_pull = args.center_pull
        # self.view = args.view

        self.neighbors = []
        self.acceleration = 0
        self.smartFlag=0

        self.arriveFlag=0
        self.vf = [np.zeros(2)]*10

    @classmethod
    def neighbors(clc):
        disTable=np.ones([clc.NUM,clc.NUM])*(clc.view+1)
        for i,first in enumerate(Bird.birds):
            for j,second in enumerate(Bird.birds[i+1:]):
                j += i+1
                disTable[i,j]=disTable[j,i]=np.linalg.norm(first.pos-second.pos)
            for i,val in enumerate(disTable[i,:]):
                if val<clc.view:
                    first.neighbors.append(clc.birds[i])


    @classmethod
    def measure(clc):
        poss= [clc.birds[i].pos for i in range(clc.NUM)]    #record all birds' position
        dev=np.std(poss)
        clc.measurement['deviation'].append(dev)

        vels=[clc.birds[i].v for i in range(clc.NUM)]
        velsnorm=np.linalg.norm(vels,axis=1)
        velsnormave=np.average(velsnorm)
        clc.measurement['avevel'].append(velsnormave)

        #provels = [clc.birds[i].v for i in range(clc.NUM)]
        vec2des=poss-clc.des
        vec2desnorm=np.linalg.norm(vec2des,axis=1)

        # projection velocity
        projvels=[np.dot(vels[i],vec2des[i])/vec2desnorm[i]**2*vec2des[i] for i in range(clc.NUM)]
        projvelsnorm=np.linalg.norm(projvels,axis=1)
        projvelsnormave=np.average(projvelsnorm)
        clc.measurement['avevelproj'].append(projvelsnormave)

        clc.iteration +=1
        #[clc.birds[i].arriveFlag for i in range(clc.NUM)]

        if all(onebird.arriveFlag==1 for onebird in clc.birds):
            clc.measurement['allarrival']=clc.iteration


    def dummtest(self):
        print(1)

    def find_neighbors(self):
        self.neighbors = [agent for agent in self.birds if agent is not self and self.calc_distance(agent) <= self.view]

    def calc_distance(self, target):
        #return math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2)
        return np.linalg.norm(target.pos-self.pos)

    def cohesion(self):

        self.vf[0] = np.mean([agent.pos for agent in self.neighbors if agent is not self],axis=0)
        self.vf[0] = (self.vf[0]-self.pos)#/self.center_pull
        #self.vf[0]=self.normalization(self.vf[0])

    def separation(self):

        personal_space = 10
        self.vf[1]=np.zeros(2)
        for bird in self.neighbors:
            if bird == self:
                continue
            dist = self.calc_distance(bird)
            if dist == 0:
                continue
            if dist < personal_space:
                #self.vf[1] = self.vf[1] - (bird.pos-self.pos)
                dirndis=bird.pos - self.pos
                dir=self.normalization(dirndis)
                dis=np.linalg.norm(dirndis)
                newdis=1/(dis/personal_space)
                self.vf[1] -= dir*newdis
                #self.vf[1]=self.normalization(self.vf[1])


    def alignment(self):

        self.vf[2] = np.mean([agent.v for agent in self.neighbors if agent is not self],axis=0)
        self.vf[2]=(self.vf[2] - self.v)
        #self.vf[2]=self.normalization(self.vf[2])

    def noise(self):
        self.vf[4]=np.ones([2])*0.05*self.ACCUP

    def normalization(self, direct, scaleValue=1):
        # print(1)
        # k = pow(dx, 2) + pow(dy, 2) + 0.000001
        # b = math.sqrt(k / self.ACCUP)
        # dx_2 = dx / b
        # dy_2 = dy / b
        norm=np.linalg.norm(direct) + 0.00000000001     #   don't be 0
        return direct/norm*scaleValue



    def smartDirection(self):
        if Bird.desSquare[:2]<list(self.pos)<Bird.desSquare[2:]:
            direction=-self.v
        else:
            direction = Bird.des-self.pos
        self.vf[3]=self.normalization(direction)

    def _collision_detection(self):
        # if self.x - Bird.RADIAN < 0:
        #     self.vx *= -1
        #     self.x = Bird.RADIAN
        # if self.x + Bird.RADIAN > Field.WIDTH:
        #     self.vx *= -1
        #     self.x = Field.WIDTH - Bird.RADIAN
        #
        # if self.y - Bird.RADIAN < 0:
        #     self.vy *= -1
        #     self.y = Bird.RADIAN
        # if self.y + Bird.RADIAN > Field.HEIGHT:
        #     self.vy *= -1
        #     self.y = Field.HEIGHT - Bird.RADIAN
        if self.pos[0] - Bird.RADIAN < 0:
            self.v[0] *= -1
            self.pos[0] = Bird.RADIAN
        if self.pos[0] + Bird.RADIAN > Field.WIDTH:
            self.v[0] *= -1
            self.pos[0] = Field.WIDTH - Bird.RADIAN

        if self.pos[1] - Bird.RADIAN < 0:
            self.v[1] *= -1
            self.pos[1] = Bird.RADIAN
        if self.pos[1] + Bird.RADIAN > Field.HEIGHT:
            self.v[1] *= -1
            self.pos[1] = Field.HEIGHT - Bird.RADIAN


    def step(self):
        self.noise()
        if self.smartFlag == 1:
            self.smartDirection()
        if not self.neighbors:          # following cal neighbors required
            return
        self.cohesion()
        self.separation()
        self.alignment()
        #print(1)


    def update(self):
        d_pos=self.ACCUP*sum([self.r[i] * self.vf[i] for i in range(10) ])
        if np.linalg.norm(d_pos)>self.ACCUP:
            d_pos1=self.normalization( d_pos, self.ACCUP)
            self.v = self.v+d_pos1
        else:
            self.v = self.v +d_pos

        velocitynorm=np.linalg.norm(self.v)
        if velocitynorm > self.SPEED:
            self.v = self.SPEED / velocitynorm * self.v
        self.pos = self.pos+self.v
        if Bird.desSquare[:2] < list(self.pos) < Bird.desSquare[2:]:
            self.arriveFlag=1

        self._collision_detection()

    def executation(self):
        self.step()
        self.update()

    def draw(self, drawer):
        #self.clear_movement()

        if self.smartFlag==1:
            drawer.create_oval(self.pos[0] - Bird.RADIAN,
                               self.pos[1] - Bird.RADIAN,
                               self.pos[0] + Bird.RADIAN,
                               self.pos[1] + Bird.RADIAN,
                               fill="red")
        else:
            drawer.create_oval(self.pos[0] - Bird.RADIAN,
                               self.pos[1] - Bird.RADIAN,
                               self.pos[0] + Bird.RADIAN,
                               self.pos[1] + Bird.RADIAN)
        drawer.create_line(self.pos[0],
                           self.pos[1],
                           self.pos[0] +
                           self.v[0] * 3,
                           self.pos[1] + self.v[1] * 3)



def myanimate():

    def animate():
        canvas.delete("all")
        canvas.create_rectangle(Bird.srcSquare, outline='red')
        canvas.create_rectangle(Bird.desSquare, outline='blue')
        for _,bird in enumerate(Bird.birds):
            bird.find_neighbors()
            bird.executation()
            bird.draw(canvas)
        Bird.measure()
        root.after(20, animate)


    Bird.birds = [Bird() for _ in range(Bird.NUM)]
    for i in range(Bird.smartCount):
        Bird.birds[i].smartFlag=1        # mark the intelligient birds
    root = Tk()
    canvas = Canvas(root, width=Field.WIDTH, height=Field.HEIGHT)
    canvas.pack()
    animate()
    root.mainloop()
def numEval():
    resoWeight = 4
    paraRange = np.linspace(0.1, 1, resoWeight)
    smartRange=np.linspace(0.025,0.5,resoWeight)
    r=[]
    repetion=5
    totaltimes = resoWeight ** 5 * repetion
    processedtimes=0
    fitness=np.zeros([repetion,3,resoWeight,
              resoWeight,resoWeight,
              resoWeight,resoWeight])
    data=[[[[[[[]for _ in range(resoWeight)]
              for _ in range(resoWeight)]
             for _ in range(resoWeight)]
            for _ in range(resoWeight)]
           for _ in range(resoWeight)]
          for _ in range(repetion)]
    for rep in range(repetion):
        for i0,r0 in enumerate(paraRange):
            r.append(r0)
            for i1,r1 in enumerate(paraRange):
                r.append(r1)
                for i2,r2 in enumerate(paraRange):
                    r.append(r2)
                    for i3,r3 in enumerate(paraRange):
                        r.append(r3)
                        r=r+[1]*(len(Bird.r)-len(r))
                        for i4,p in enumerate(smartRange):
                            time1=time.time()
                            Bird.smartCount=round(Bird.NUM*p)
                            Bird.birds = [Bird() for _ in range(Bird.NUM)]
                            for i in range(Bird.smartCount):
                                Bird.birds[i].smartFlag=1
                            for iter in range(Bird.maxiteration):
                                #Bird.neighbors()
                                for _, bird in enumerate(Bird.birds):
                                    bird.find_neighbors()
                                    bird.executation()
                                Bird.measure()
                                if Bird.measurement['allarrival']<Bird.maxiteration:
                                    break
                            data[rep][i0][i1][i2][i3][i4]=Bird.measurement
                            processedtimes +=1

                            # fitnessval=(
                            #         (Bird.maxiteration-Bird.measurement['allarrival'])/Bird.maxiteration+\
                            #         (150-max(Bird.measurement['deviation']))/150+\
                            #         max(Bird.measurement['avevelproj'])/Bird.SPEED+\
                            #         1-p
                            #      )*\
                            if Bird.measurement['allarrival'] < Bird.maxiteration:
                                firstthree=(Bird.maxiteration-Bird.measurement['allarrival'])/Bird.maxiteration+\
                                        (150-max(Bird.measurement['deviation']))/150+\
                                        max(Bird.measurement['avevelproj'])/Bird.SPEED
                                fitness[rep,0,i0,i1,i2,i3,i4]=(firstthree+(1-p))
                                fitness[rep, 1, i0, i1, i2, i3, i4] = (firstthree + (1 - 1.5*p))
                                fitness[rep, 2, i0, i1, i2, i3, i4] = (firstthree + (1 - 2*p))
                                print("fitness value:",fitness[rep,0,i0,i1,i2,i3,i4])

                            print(processedtimes,'/',totaltimes)
                            print(time.ctime())
                            # reset class variables
                            Bird.iteration = 0
                            Bird.measurement = {
                                'deviation': [],
                                'avevel': [],  # average velocity
                                'avevelproj': [],  # average velocity projected to the direction to the destination
                                'allarrival': Bird.maxiteration+1
                            }
                            print("This iteration costs: ", time.time()-time1,"s")

    with open('0512twilight.pkl', 'wb') as f:
        pickle.dump(data, f)
        pickle.dump(fitness, f)
    print(1)

def main():



    if 0:
        myanimate()
    else:
        numEval()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Boids Model parameters')
    parser.add_argument('--r0', type=float, default=2.0, help='cohesion coefficient') #원래는 1.0
    parser.add_argument('--r1', type=float, default=0.8, help='separation coefficient')
    parser.add_argument('--r2', type=float, default=0.3, help='alignment coefficient')
    parser.add_argument('--r3', type=float, default=2, help='intelligent coefficient')
    parser.add_argument('--center-pull', type=int, default=30, 
                        help='center pull coefficient for means of neighbors coordinante') #300
    parser.add_argument('--view', type=int, default=50, help='view of each birds') #150
    args = parser.parse_args()
    main()

    