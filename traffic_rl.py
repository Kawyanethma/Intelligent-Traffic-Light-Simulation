import numpy as np
from collections import deque
import random

class TrafficRLAgent:
    def __init__(self, state_size=5, action_size=4):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        self.min_green_time = 10
        self.max_green_time = 30
        self.model = self._build_model()
    
    def _build_model(self):
        # Initialize Q-table with small random values instead of zeros
        return np.random.uniform(low=0, high=1, size=(100, self.action_size))
    
    def get_state(self, stopped_vehicles, current_signal):
        # Create a more compact state representation
        state = []
        for direction in ['right', 'down', 'left', 'up']:
            state.append(min(stopped_vehicles[direction], 10))  # Cap at 10 vehicles
        state.append(current_signal)
        return np.array(state)
    
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        
        # Use a better state index for Q-table lookup
        state_index = int(sum(state[:-1]) * state[-1] % 100)
        q_values = self.model[state_index]
        return np.argmax(q_values)
    
    def train(self, state, action, reward, next_state):
        # Better state indexing for Q-learning
        state_index = int(sum(state[:-1]) * state[-1] % 100)
        next_state_index = int(sum(next_state[:-1]) * next_state[-1] % 100)
        
        current_q = self.model[state_index, action]
        next_max_q = np.max(self.model[next_state_index])
        new_q = current_q + self.learning_rate * (reward + self.gamma * next_max_q - current_q)
        self.model[state_index, action] = new_q
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def get_green_time(self, stopped_vehicles, current_signal):
        state = self.get_state(stopped_vehicles, current_signal)
        action = self.act(state)
        
        # Scale action to green time more evenly
        green_time = self.min_green_time + int(action * (self.max_green_time - self.min_green_time) / (self.action_size - 1))
        return max(min(green_time, self.max_green_time), self.min_green_time), state