import random
import numpy as np


def sigmoid(x):
    # sigmoid function: f(x) = 1 / (1 + e^(-x))
    return 1 / (1 + np.exp(-x))


def tanh(x):
    # tanh function: f(x) = (e^(x) - e^(-x)) / (e^(x) + e^(-x))
    return (np.exp(x) - np.exp(-x)) / (np.exp(x) + np.exp(-x))


def deriv_sigmoid(x):
    # derivative of sigmoid function: f'(x) = f(x) * (1 - f(x))
    fx = sigmoid(x)
    return fx * (1 - fx)


def mse_loss(y_true, y_predict):
    # loss function
    return ((y_true - y_predict) ** 2).mean()


def get_random_weights(size, range_=(-1, 1)) -> list:
    ret = []
    for i in range(size):
        ret.append(random.uniform(*range_))
    return ret


def get_random_bias(range_=(-1, 1)):
    return random.uniform(*range_)


class Neuron:
    """
    single neuron class
    """

    def __init__(self, weights, bias):
        self.weights = weights
        self.bias = bias

    def feedforward(self, inputs, activation=None):
        """
        output=0
        for i in range(len(inputs)):
            output+=inputs[i]*weights[i]
        """
        output = np.dot(self.weights, inputs) + self.bias
        if activation == 'sigmoid':
            return sigmoid(output)
        elif activation == 'tanh':
            return tanh(output)
        elif activation == None:
            return output


class NeuralNetwork:
    """
    this network consist of three layers including 1 input layer, 1 hidden layer, and 1 output layer
    input layer has 3 neurons, hidden layer has 5 neurons, and output layer has 2 neurons
    ┌─────────────┬──────────────┬──────────────┐
     input layer  hidden layer  output layer 
    ├─────────────┼──────────────┼──────────────┤
           3             5              2            
    └─────────────┴──────────────┴──────────────┘
    """

    def __init__(self):
        # # hidden layer neurons's initial weights
        # hidden_weights = [0, 1, 0]
        # # output layer neurons's initial weights
        # output_weights = [0, 1, 0, 1, 0]
        # # all neurons's initial bias: 0
        # bias = 1

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
        output_h1 = self.hs[0].feedforward(inputs)
        output_h2 = self.hs[1].feedforward(inputs)
        output_h3 = self.hs[2].feedforward(inputs)
        output_h4 = self.hs[3].feedforward(inputs)
        output_h5 = self.hs[4].feedforward(inputs)

        # hidden layer output
        output_h = [output_h1, output_h2, output_h3, output_h4, output_h5]

        output_o1 = self.os[0].feedforward(output_h, 'tanh')
        output_o2 = self.os[1].feedforward(output_h)

        return [output_o1, output_o2]


def sort_score(nets) -> list:
    """
    sort networks list by their score (fitness), big-->small
    """
    for i in range(len(nets) - 1):
        for j in range(i + 1, len(nets)):
            if nets[i].score < nets[j].score:
                # swap
                temp = nets[i]
                nets[i] = nets[j]
                nets[j] = temp
    return nets


def update_score(nets) -> list:
    """
    update every network's score (fitness) per loop
    fitness is determined by every networks's behaves in current round
    """
    for i in range(len(nets)):
        nets[i].score = i
    return nets


def roulette_selection(nets, ratio) -> NeuralNetwork:
    """
    select one network from networks' mating pool by using 'roullette wheel selection' algorithm
    'roulette' algorithm tend to select one network that has higher score
    """
    nets = [nets[i] for i in range(int(len(nets) * ratio))]
    # calculate all networks' total score
    total_score = 0
    for net in nets:
        total_score += net.score

    # calculate every network's accum_rate
    accum_rate = 0
    for i in range(len(nets)):
        rate = nets[i].score / total_score  # one's probability
        accum_rate += rate
        nets[i].accum_rate = accum_rate

    # select one network randomly by each probability
    n = random.random()
    for net in nets:
        if n < net.accum_rate:
            return net


def get_elites(nets, ratio) -> list:
    """
    get top 1/4 elites networks from this generation
    """
    elites = [nets[i] for i in range(int(len(nets) * ratio))]
    return elites


def crossover(nets, ratio) -> NeuralNetwork:
    """
    select two networks through 'roullette wheel selection' algorithm,
    then cross their genes (weights) randomly to get a new child (network)
    """
    father = roulette_selection(nets, ratio)
    mother = roulette_selection(nets, ratio)
    child = NeuralNetwork()

    # crossover hidden layer
    for i in range(len(child.hs)):
        if random.random() < 0.5:
            child.hs[i] = father.hs[i]
        else:
            child.hs[i] = mother.hs[i]

    # crossover output layer
    for i in range(len(child.os)):
        if random.random() < 0.5:
            child.os[i] = father.os[i]
        else:
            child.os[i] = mother.os[i]

    return child


def mutate(nets, pm, range_) -> list:
    """
    mutate next generation networks by 'Pm'
    'Pm' is the probability of mutation
    """
    for i in range(len(nets)):
        # every hidden layer's neuron
        for j in range(len(nets[i].hs)):
            if random.random() < pm:
                # mutate weights and bias
                for k in range(len(nets[i].hs[j].weights)):
                    nets[i].hs[j].weights[k] += random.uniform(-range_,
                                                               range_) * nets[i].hs[j].weights[k]
                nets[i].hs[j].bias += random.uniform(-range_,
                                                     range_) * nets[i].hs[j].bias
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

    # networks list, every item is a NeuralNetwork
    nets = []

    # initialize networks list, size: 100
    for i in range(100):
        nets.append(NeuralNetwork())

    # update fitness according to behaves
    nets = update_score(nets)

    # sort networks by their fitness
    nets = sort_score(nets)

    # top 1/4 elite networks
    elites = get_elites(nets, 0.25)

    # next generation's networks list
    next_gen_nets = []

    # add this generation's elites directly to next generation
    next_gen_nets.extend(elites)

    # create hybrid children and add them to next generation until enough
    for i in range(int(len(nets) / 4 * 3)):
        child = crossover(nets, 0.3)
        next_gen_nets.append(child)

    # mutate next generation's every network including elites
    next_gen_nets = mutate(next_gen_nets, 0.1, 0.1)

    print([net.hs[1].bias for net in next_gen_nets])


if __name__ == "__main__":
    main()
