# Neural Network architecture.

from keras.models import Sequential
from keras.layers import Conv2D, Flatten, Dense
import gym
import numpy as np


class DQN_net:
    def __init__(self, input_size, action_size,
                 batch_size = 32,
                 discount_factor = 0.95,
                 learning_rate = 0.00025):
        # Hyper Parameters
        self.actions = action_size
        self.input_size = input_size
        self.discount_factor = discount_factor
        self.learning_rate = learning_rate
        self.batch_size = batch_size

        # Sequential() creates the foundation of the layers.
        self.model = Sequential()
        self.model.add(Conv2D(16, (8, 8), strides=4,
                              activation='relu',
                              input_shape= input_size))

        # The second hidden layer convolves 32 4×4 filters
        self.model.add(Conv2D(32, (4, 4), strides=2,
                              activation='relu'))
        self.model.add(Flatten())
        self.model.add(Dense(256, activation='relu'))
        self.model.add(Dense(self.actions))
        self.model.compile(loss='mean_squared_error',
                           optimizer='rmsprop',
                           metrics=['accuracy'])

    def train(self, experience_batch, target_network):
        ''' Experience_batch is a list of size "batch_size" with elements
        randomly drawn from the Replay-memory.
        elements = (state, action, reward, next_state, done)
        -target_network is a DQN_net instance to generate target according
        to the DQN algorithm.
        '''
        assert type(target_network) == DQN_net
        state_train = np.zeros((self.batch_size,) + self.input_size)
        target_train = np.zeros((self.batch_size,) + (self.actions,))
        for i, experience in enumerate(experience_batch):

            state_train[i] = experience[0]
            action_train = experience[1]
            reward_train = experience[2]
            next_state_train = experience[3]
            is_done = experience[4]

            output_target_pred = target_network.model.predict(next_state_train)
            output_current_state = self.model.predict(state_train)

            # output_target_pred_shape = [[q_action_1, ... ,q_action_n]]
            for k, elem in enumerate(output_current_state[0]):
                target_train[i][k] = elem

            max_q_value_pred = np.max(output_target_pred[0])
            # max_q_action = np.argmax(output_target_pred[0])

            if is_done is True:
                target_train[i][action_train] = reward_train
            else:
                target_train[i][action_train] = reward_train + \
                                        self.discount_factor * max_q_value_pred  # output_target_pred[0][max_q_action]

        self.model.fit(state_train,
                       target_train,
                       batch_size=self.batch_size,
                       epochs=1,
                       verbose=0)


# TEST CODE
if __name__ == "__main__":
    env = gym.make('MsPacman-v0')
    frame = env.reset()
    state_size = env.observation_space.shape
    print("state size:",state_size)
    action_size = env.action_space.n #Gives a size of 9?!? change to 4!!
    print("action size:",action_size)
    test_net = DQN_net(state_size, action_size)

    # Formatting input shape for first conv2D layer
    frame, reward, is_done, _ = env.step(env.action_space.sample())
    # y = np.reshape(x, (10, 15, 1))
    # print(frame[1][1][1])
    obs = np.expand_dims(frame, axis=0)     # (Formatting issues) Making the observation the first element of a batch of inputs
    # input_tensor = np.stack((frame, frame), axis=1)
    # print(obs)
    target_f = test_net.model.predict(obs)
