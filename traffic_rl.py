import numpy as np
from collections import deque
import random
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.optimizers import Adam

class TrafficRLAgent:
    def __init__(self, state_size=5, action_size=4):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0   # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.min_green_time = 10
        self.max_green_time = 30
        self.batch_size = 32
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_counter = 0
        self.target_update_frequency = 10
    
    def _build_model(self):
        model = Sequential([
            Dense(24, input_dim=self.state_size, activation='relu'),
            Dense(24, activation='relu'),
            Dense(self.action_size, activation='linear')
        ])
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())
    
    def get_state(self, stopped_vehicles, current_signal):
        state = []
        # Normalize vehicle counts
        for direction in ['right', 'down', 'left', 'up']:
            state.append(min(stopped_vehicles[direction], 20) / 20.0)  # Normalize between 0 and 1
        state.append(current_signal / (self.action_size - 1))  # Normalize signal
        return np.array(state)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        state = np.reshape(state, [1, self.state_size])
        act_values = self.model.predict(state, verbose=0)
        return np.argmax(act_values[0])
    
    def replay(self):
        if len(self.memory) < self.batch_size:
            return
        
        minibatch = random.sample(self.memory, self.batch_size)
        states = np.array([i[0] for i in minibatch])
        actions = np.array([i[1] for i in minibatch])
        rewards = np.array([i[2] for i in minibatch])
        next_states = np.array([i[3] for i in minibatch])
        dones = np.array([i[4] for i in minibatch])
        
        states = np.squeeze(states)
        next_states = np.squeeze(next_states)
        
        targets = self.model.predict(states, verbose=0)
        next_target = self.target_model.predict(next_states, verbose=0)
        
        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * np.amax(next_target[i])
        
        self.model.fit(states, targets, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.update_target_counter += 1
        if self.update_target_counter >= self.target_update_frequency:
            self.update_target_model()
            self.update_target_counter = 0
    
    def get_green_time(self, stopped_vehicles, current_signal):
        state = self.get_state(stopped_vehicles, current_signal)
        action = self.act(state)
        
        # Convert action to green time using a more granular approach
        green_time = self.min_green_time + (action * (self.max_green_time - self.min_green_time) // (self.action_size - 1))
        return max(min(green_time, self.max_green_time), self.min_green_time), state
    
    def calculate_reward(self, stopped_vehicles, waiting_times):
        # Calculate reward based on both number of stopped vehicles and waiting times
        total_stopped = sum(stopped_vehicles.values())
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
        
        # Negative reward proportional to stopped vehicles and waiting time
        reward = -(total_stopped * 0.5 + avg_waiting_time * 0.5)
        return max(-100, min(reward, 0))  # Clip reward between -100 and 0