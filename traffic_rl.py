import numpy as np
from collections import deque
import torch
import torch.nn as nn
import torch.optim as optim
import random

class TrafficRLAgent:
    def __init__(self, state_size=5, action_size=2):
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
        
        # Add metrics tracking
        self.metrics = {
            'rewards': [],
            'waiting_times': [],
            'stopped_vehicles': [],
            'decisions': [],
            'accuracy': [],
            'loss_history': []
        }
    
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
        # Get vehicle counts for all 4 directions
        for direction in ['right', 'down', 'left', 'up']:
            state.append(min(stopped_vehicles[direction], 20) / 20.0)
        # Add current signal state
        state.append(current_signal / 3.0)  # Normalize signal state (0-3)
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
    
    def evaluate_performance(self):
        """Calculate and print performance metrics"""
        if len(self.metrics['rewards']) == 0:
            return
        
        print("\n=== Performance Metrics ===")
        # Calculate average metrics over last 100 episodes
        window = min(100, len(self.metrics['rewards']))
        recent_rewards = self.metrics['rewards'][-window:]
        recent_waiting = self.metrics['waiting_times'][-window:]
        recent_stopped = self.metrics['stopped_vehicles'][-window:]
        recent_accuracy = self.metrics['accuracy'][-window:]
        
        print(f"Last {window} episodes:")
        print(f"Average Reward: {sum(recent_rewards) / window:.2f}")
        print(f"Average Waiting Time: {sum(recent_waiting) / window:.2f} seconds")
        print(f"Average Stopped Vehicles: {sum(recent_stopped) / window:.2f}")
        print(f"Decision Accuracy: {sum(recent_accuracy) / window:.2%}")
        
        # Plot metrics if matplotlib is available
        try:
            self.plot_metrics()
        except ImportError:
            print("Matplotlib not available for plotting")
    
    def plot_metrics(self):
        """Plot performance metrics"""
        import matplotlib.pyplot as plt
        
        plt.figure(figsize=(15, 10))
        
        # Plot rewards
        plt.subplot(2, 2, 1)
        plt.plot(self.metrics['rewards'])
        plt.title('Rewards over Time')
        plt.xlabel('Episode')
        plt.ylabel('Reward')
        
        # Plot waiting times
        plt.subplot(2, 2, 2)
        plt.plot(self.metrics['waiting_times'])
        plt.title('Average Waiting Time')
        plt.xlabel('Episode')
        plt.ylabel('Time (s)')
        
        # Plot stopped vehicles
        plt.subplot(2, 2, 3)
        plt.plot(self.metrics['stopped_vehicles'])
        plt.title('Total Stopped Vehicles')
        plt.xlabel('Episode')
        plt.ylabel('Count')
        
        # Plot accuracy
        plt.subplot(2, 2, 4)
        plt.plot(self.metrics['accuracy'])
        plt.title('Decision Accuracy')
        plt.xlabel('Episode')
        plt.ylabel('Accuracy')
        
        plt.tight_layout()
        plt.show()
    
    def update_metrics(self, state, action, reward, stopped_vehicles, waiting_times):
        """Update performance metrics"""
        # Store metrics
        self.metrics['rewards'].append(reward)
        self.metrics['waiting_times'].append(sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0)
        self.metrics['stopped_vehicles'].append(sum(stopped_vehicles.values()))
        
        # Calculate decision accuracy
        optimal_action = self.get_optimal_action(stopped_vehicles)
        accuracy = 1.0 if action == optimal_action else 0.0
        self.metrics['accuracy'].append(accuracy)
        
        # Print current metrics every 100 episodes
        if len(self.metrics['rewards']) % 100 == 0:
            self.evaluate_performance()
    
    def get_optimal_action(self, stopped_vehicles):
        """Calculate the optimal action based on traffic state"""
        # Simple heuristic: choose direction with most waiting vehicles
        max_waiting = -1
        optimal_direction = 0
        
        for i, direction in enumerate(['right', 'down', 'left', 'up']):
            if stopped_vehicles[direction] > max_waiting:
                max_waiting = stopped_vehicles[direction]
                optimal_direction = i
        
        return optimal_direction
    
    def get_green_time(self, stopped_vehicles, current_signal):
        state = self.get_state(stopped_vehicles, current_signal)
        action = self.act(state)
        
        # Debug print and metrics update
        print("\n=== RL Agent Decision ===")
        print(f"Current Signal: {current_signal}")
        print(f"State: {state}")
        print(f"Action chosen: {action}")
        print(f"Optimal action: {self.get_optimal_action(stopped_vehicles)}")
        print(f"Stopped vehicles: {stopped_vehicles}")
        
        # Calculate green time and update metrics
        green_time = self.calculate_green_time(action, stopped_vehicles)
        reward = self.calculate_reward(stopped_vehicles, {})  # Empty waiting times for now
        self.update_metrics(state, action, reward, stopped_vehicles, {})
        
        return action, green_time, state
    
    def calculate_green_time(self, action, stopped_vehicles):
        """Calculate appropriate green time based on traffic state"""
        direction_map = {0: 'right', 1: 'down', 2: 'left', 3: 'up'}
        vehicles_waiting = stopped_vehicles[direction_map[action]]
        
        if vehicles_waiting > 15:
            return self.max_green_time
        elif vehicles_waiting > 8:
            return (self.min_green_time + self.max_green_time) // 2
        else:
            return self.min_green_time
    
    def calculate_reward(self, stopped_vehicles, waiting_times):
        # Penalize heavily for vehicles stuck in left direction
        left_penalty = -50 if stopped_vehicles['left'] > 5 else 0
        
        # Calculate base reward
        total_stopped = sum(stopped_vehicles.values())
        avg_waiting_time = sum(waiting_times.values()) / len(waiting_times) if waiting_times else 0
        
        # Combine rewards with extra weight on left direction
        base_reward = -(total_stopped * 0.5 + avg_waiting_time * 0.5)
        total_reward = base_reward + left_penalty
        
        # Add reward tracking
        print(f"Reward received: {total_reward}")
        return max(-100, min(total_reward, 0))  # Clip between -100 and 0
    
    def train_model(self, state, action, reward, next_state, done):
        self.remember(state, action, reward, next_state, done)
        self.replay()

if __name__ == "__main__":
    # Create an agent instance
    agent = TrafficRLAgent()
    
    def get_stopped_vehicles_from_simulation(simulation):
        """Get number of stopped vehicles from the simulation for each direction"""
        stopped_vehicles = {
            'right': len(simulation.right_vehicles_stopped),
            'down': len(simulation.down_vehicles_stopped),
            'left': len(simulation.left_vehicles_stopped),
            'up': len(simulation.up_vehicles_stopped)
        }
        
        # Print the stopped vehicles count
        print("\nStopped Vehicles Count:")
        print("----------------------")
        print(f"Right: {stopped_vehicles['right']} vehicles")
        print(f"Down:  {stopped_vehicles['down']} vehicles")
        print(f"Left:  {stopped_vehicles['left']} vehicles")
        print(f"Up:    {stopped_vehicles['up']} vehicles")
        print(f"Total: {sum(stopped_vehicles.values())} vehicles")
        print("----------------------\n")
        
        return stopped_vehicles
    
    # In your main simulation loop:
    def update(simulation, current_signal):
        # Get and print real-time stopped vehicles data
        stopped_vehicles = get_stopped_vehicles_from_simulation(simulation)
        
        # Get green time and state from agent
        green_time, state = agent.get_green_time(stopped_vehicles, current_signal)
        
        return green_time