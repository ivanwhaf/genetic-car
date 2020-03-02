import random
import numpy as np


def sigmoid(x):
    # sigmoid function: f(x) = 1 / (1 + e^(-x))
    return 1/(1+np.exp(-x))


def deriv_sigmoid(x):
    # derivative of simgoid function: f'(x) = f(x) * (1 - f(x))
    fx = sigmoid(x)
    return fx*(1-fx)


def mse_loss(y_true, y_predict):
    # loss function
    return ((y_true-y_predict)**2).mean()


def get_random_weights(size)->list:
    ret=[]
    for i in range(size):
        ret.append(random.uniform(-1,1))
    return ret


def get_random_bias():
    return random.uniform(-1,1)


class Neuron:
    """
    single neuron class
    """
    def __init__(self, weights, bias):
        self.weights = weights
        self.bias = bias


    def feedforward(self, inputs,activation='sigmoid'):
        '''
        output=0
        for i in range(len(inputs)):
            output+=inputs[i]*weights[i]
        '''
        output = np.dot(self.weights, inputs)+self.bias
        if activation=='sigmoid':
            return sigmoid(output)
        elif activation=='softmax':
            return output
        elif activation=='no':
            return output



class NeuralNetwork:
    """
    this network consist of three layers including 1 input layer, 1 hidden layer, and 1 output layer
    input layer has 3 neurons, hidden layer has 5 neurons, and output layer has 2 neurons
    ┌─────────────┬──────────────┬──────────────┐
     input layer  hidden layer  output layer 
    ├─────────────┼──────────────┼──────────────┤
          3             5            2            
    └─────────────┴──────────────┴──────────────┘
    """

    def __init__(self):
        # hidden layer neurons's initial weights
        hidden_weights = [0, 1, 0]
        # output layer neurons's initial weights
        output_weights = [0, 1, 0, 1, 0]
        # all neurons's initial bias: 0
        bias = 1

        # hidden layer neurons
        self.h1 = Neuron(get_random_weights(3), get_random_bias())
        self.h2 = Neuron(get_random_weights(3), get_random_bias())
        self.h3 = Neuron(get_random_weights(3), get_random_bias())
        self.h4 = Neuron(get_random_weights(3), get_random_bias())
        self.h5 = Neuron(get_random_weights(3), get_random_bias())
        self.hs = [self.h1, self.h2, self.h3, self.h4, self.h5]

        # output layer neurons
        self.o1 = Neuron(get_random_weights(5), get_random_bias())
        self.o2 = Neuron(get_random_weights(5), get_random_bias())
        self.os = [self.o1, self.o2]

        # network's fitness score
        self.score = 0

        # network's accum_rate calculated by all networks' score
        self.accum_rate = 0

    def feedforward(self, inputs):
        '''
        output_h1 = self.h1.feedforward(inputs)
        output_h2 = self.h2.feedforward(inputs)
        output_h3 = self.h3.feedforward(inputs)
        output_h4 = self.h4.feedforward(inputs)
        output_h5 = self.h5.feedforward(inputs)
        '''
        output_h1 = self.hs[0].feedforward(inputs)
        output_h2 = self.hs[1].feedforward(inputs)
        output_h3 = self.hs[2].feedforward(inputs)
        output_h4 = self.hs[3].feedforward(inputs)
        output_h5 = self.hs[4].feedforward(inputs)

        output_h = [output_h1, output_h2, output_h3, output_h4, output_h5]

        output_o1 = self.os[0].feedforward(output_h)
        output_o2 = self.os[1].feedforward(output_h)

        return [output_o1, output_o2]

    def train(self, x_train, y_train):
        '''
        epochs=1000  # train loop times
        lr=0.1  # learning rate
        for epoch in range(epochs):
            for x, y_true in zip(x_train,y_train):
                w1=self.h1.weights[0]
                w2=self.h1.weights[1]
                w3=self.h1.weights[2]
                w4=self.h2.weights[0]
                w5=self.h2.weights[1]
                w6=self.h2.weights[2]
                w7=self.h3.weights[0]
                w8=self.h3.weights[1]
                w9=self.h3.weights[2]
                w10=self.h4.weights[0]
                w11=self.h4.weights[1]
                w12=self.h4.weights[2]
                w13=self.h5.weights[0]
                w14=self.h5.weights[1]
                w15=self.h5.weights[2]
                b1=self.h1.bias
                b2=self.h2.bias
                b3=self.h3.bias
                b4=self.h4.bias
                b5=self.h5.bias

                w16=self.o1.weights[0]
                w17=self.o1.weights[1]
                w18=self.o1.weights[2]
                w19=self.o1.weights[3]
                w20=self.o1.weights[4]
                w21=self.o2.weights[0]
                w22=self.o2.weights[1]
                w23=self.o2.weights[2]
                w24=self.o2.weights[3]
                w25=self.o2.weights[4]
                b6=self.o1.bias
                b7=self.o2.bias

                sum_h1=w1*x[0] + w2*x[1] + w3*x[2] + b1
                h1=sigmoid(sum_h1)

                sum_h2=w4*x[0] + w5*x[1] + w6*x[2] + b2
                h2=sigmoid(sum_h2)

                sum_h3=w7*x[0] + w8*x[1] + w9*x[2] + b3
                h3=sigmoid(sum_h3)

                sum_h4=w10*x[0] + w11*x[1] + w12*x[2] + b4
                h4=sigmoid(sum_h4)

                sum_h5=w13*x[0] + w14*x[1] + w15*x[2] + b5
                h5=sigmoid(sum_h5)
        '''


def sort_score(nets) -> list:
    """
    sort networks by their score(fitness), big-->small
    """
    for i in range(len(nets)-1):
        for j in range(i+1, len(nets)):
            if nets[i].score < nets[j].score:
                # swap
                temp = nets[i]
                nets[i] = nets[j]
                nets[j] = temp
    return nets


def update_score(nets) -> list:
    """
    update every network's score(fitness) per loop
    fitness is determined by every networks's behaves in current round
    """
    for i in range(len(nets)):
        nets[i].score = i
    return nets


def roulette_selection(nets) -> NeuralNetwork:
    """
    select one network from all networks by using 'roullette wheel selection' algorithm
    'roulette' algorithm tend to select one network that has higher score
    """
    # calculate all networks' toatal score
    total_score = 0
    for net in nets:
        total_score += net.score

    # calculate every network's accum_rate
    accum_rate = 0
    for i in range(len(nets)):
        rate = nets[i].score/total_score  # one's probability
        accum_rate += rate
        nets[i].accum_rate = accum_rate

    # select one network randomly by each probability
    n = random.random()
    for net in nets:
        if n < net.accum_rate:
            return net


def get_elites(nets,rate) ->list:
    """
    get top 1/4 elites networks from this generation
    """
    elites = [nets[i] for i in range(int(len(nets)*rate))]
    return elites


def crossover(nets) -> NeuralNetwork:
    """
    select two networks through 'roullette wheel selection' algorithm,
    then cross their genes(weights) randomly to get a new child(network)
    """
    father = roulette_selection(nets)
    mother = roulette_selection(nets)
    child = NeuralNetwork()
    # cross hidden layer
    for i in range(len(child.hs)):
        if random.random() < 0.5:
            child.hs[i] = father.hs[i]
        else:
            child.hs[i] = mother.hs[i]

    # cross output layer
    for i in range(len(child.os)):
        if random.random() < 0.5:
            child.os[i] = father.os[i]
        else:
            child.os[i] = mother.os[i]
    
    return child


def mutation(nets,pm,ratio) -> list:
    """
    mutate next generation networks by 'Pm'
    'Pm' is the probability of mutation
    """
    for i in range(len(nets)):
        # every hidden layer neuron
        for j in range(len(nets[i].hs)):
            if random.random() < pm:
                # mutate weights and bias
                for k in range(len(nets[i].hs[j].weights)):
                    nets[i].hs[j].weights[k] += random.uniform(-ratio, ratio)*nets[i].hs[j].weights[k]
                nets[i].hs[j].bias += random.uniform(-ratio, ratio)*nets[i].hs[j].bias
    return nets


def main():
    weights = [1, 2]  # w1=1, w2=2
    bias = 5
    neuron = Neuron(weights, bias)
    inputs = [2, 3]  # x1=2, x2=3
    print(neuron.feedforward(inputs))

    network = NeuralNetwork()
    inputs = [2, 3, 4]
    print(network.feedforward(inputs))

    # networks list, every item is a NuralNetwork
    nets = []

    # initialize networks list, size: 100
    for i in range(100):
        nets.append(NeuralNetwork())

    # update fitness according to behaves
    nets = update_score(nets)

    # sort networks by their fitness
    nets = sort_score(nets)

    # top 1/4 elite networks
    elites=get_elites(nets,0.25)

    # next generation's networks list
    next_gen_nets=[]

    # add this generation's elites directly to next generation
    next_gen_nets.extend(elites)

    # create hybrid children and add them to next geration until enough
    for i in range(int(len(nets)/4*3)):
        child = crossover(nets)
        next_gen_nets.append(child)

    # mutate next generation's every network including elites
    next_gen_nets=mutation(next_gen_nets,0.1)

    print([net.hs[1].bias for net in next_gen_nets])


if __name__ == "__main__":
    main()

