import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import random

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
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._build_model().to(self.device)
        self.target_model = self._build_model().to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.update_target_counter = 0
        self.target_update_frequency = 10
    
    def _build_model(self):
        model = nn.Sequential(
            nn.Linear(self.state_size, 24),
            nn.ReLU(),
            nn.Linear(24, 24),
            nn.ReLU(),
            nn.Linear(24, self.action_size)
        )
        return model
    
    def update_target_model(self):
        self.target_model.load_state_dict(self.model.state_dict())
    
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
        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)
        with torch.no_grad():
            act_values = self.model(state)
        return np.argmax(act_values.cpu().numpy())
    
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
        
        targets = self.model(torch.FloatTensor(states).to(self.device))
        next_target = self.target_model(torch.FloatTensor(next_states).to(self.device))
        
        for i in range(self.batch_size):
            if dones[i]:
                targets[i][actions[i]] = rewards[i]
            else:
                targets[i][actions[i]] = rewards[i] + self.gamma * targets[i].max().item()
        
        self.optimizer.zero_grad()
        targets = targets.detach().numpy()
        targets = torch.FloatTensor(targets).to(self.device)
        loss = nn.MSELoss()(targets, self.model(torch.FloatTensor(states).to(self.device)))
        loss.backward()
        self.optimizer.step()
        
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
    
    def train_model(self, state, action, reward, next_state, done):
        self.remember(state, action, reward, next_state, done)
        self.replay()

if __name__ == "__main__":
    # Create an agent instance
    agent = TrafficRLAgent()
    
    # Example usage
    stopped_vehicles = {'right': 5, 'down': 3, 'left': 4, 'up': 2}
    current_signal = 0
    
    # Get green time and state
    green_time, state = agent.get_green_time(stopped_vehicles, current_signal)
    print(f"Recommended green time: {green_time}")