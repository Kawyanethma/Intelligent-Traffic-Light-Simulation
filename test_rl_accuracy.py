import numpy as np
from traffic_rl import TrafficRLAgent
import matplotlib.pyplot as plt

def test_rl_accuracy():
    # Initialize the agent
    agent = TrafficRLAgent(state_size=5, action_size=4)
    
    # Test parameters
    n_episodes = 1000
    accuracy_list = []
    rewards_list = []
    
    # Generate synthetic traffic scenarios
    def generate_traffic_scenario():
        return {
            'right': np.random.randint(0, 20),
            'down': np.random.randint(0, 20),
            'left': np.random.randint(0, 20),
            'up': np.random.randint(0, 20)
        }
    
    print("Starting accuracy test...")
    
    for episode in range(n_episodes):
        # Generate random traffic scenario
        stopped_vehicles = generate_traffic_scenario()
        current_signal = np.random.randint(0, 4)
        
        # Get agent's decision
        state = agent.get_state(stopped_vehicles, current_signal)
        action = agent.act(state)
        
        # Get optimal action
        optimal_action = agent.get_optimal_action(stopped_vehicles)
        
        # Calculate accuracy
        accuracy = 1.0 if action == optimal_action else 0.0
        accuracy_list.append(accuracy)
        
        # Calculate reward
        reward = agent.calculate_reward(stopped_vehicles, {})
        rewards_list.append(reward)
        
        # Train the agent
        next_state = agent.get_state(generate_traffic_scenario(), action)
        agent.train_model(state, action, reward, next_state, False)
        
        # Print progress
        if (episode + 1) % 100 == 0:
            avg_accuracy = np.mean(accuracy_list[-100:])
            avg_reward = np.mean(rewards_list[-100:])
            print(f"Episode {episode + 1}")
            print(f"Average Accuracy (last 100): {avg_accuracy:.2%}")
            print(f"Average Reward (last 100): {avg_reward:.2f}")
            print(f"Epsilon: {agent.epsilon:.3f}")
            print("------------------------")
    
    # Plot results
    plt.figure(figsize=(15, 5))
    
    # Plot accuracy
    plt.subplot(1, 2, 1)
    plt.plot(np.convolve(accuracy_list, np.ones(100)/100, mode='valid'))
    plt.title('Moving Average Accuracy (window=100)')
    plt.xlabel('Episode')
    plt.ylabel('Accuracy')
    
    # Plot rewards
    plt.subplot(1, 2, 2)
    plt.plot(np.convolve(rewards_list, np.ones(100)/100, mode='valid'))
    plt.title('Moving Average Reward (window=100)')
    plt.xlabel('Episode')
    plt.ylabel('Reward')
    
    plt.tight_layout()
    plt.show()
    
    # Final statistics
    print("\nFinal Statistics:")
    print(f"Overall Accuracy: {np.mean(accuracy_list):.2%}")
    print(f"Final Epsilon: {agent.epsilon:.3f}")
    print(f"Average Reward: {np.mean(rewards_list):.2f}")
    
    # Detailed analysis
    def analyze_performance(stopped_vehicles):
        state = agent.get_state(stopped_vehicles, 0)
        action = agent.act(state)
        optimal = agent.get_optimal_action(stopped_vehicles)
        return action, optimal
    
    print("\nTesting specific scenarios:")
    
    # Test balanced traffic
    balanced = {'right': 10, 'down': 10, 'left': 10, 'up': 10}
    action, optimal = analyze_performance(balanced)
    print("\nBalanced traffic:")
    print(f"Vehicles: {balanced}")
    print(f"Agent action: {action}, Optimal action: {optimal}")
    
    # Test heavy traffic in one direction
    heavy_right = {'right': 18, 'down': 5, 'left': 5, 'up': 5}
    action, optimal = analyze_performance(heavy_right)
    print("\nHeavy right traffic:")
    print(f"Vehicles: {heavy_right}")
    print(f"Agent action: {action}, Optimal action: {optimal}")
    
    # Test light traffic
    light = {'right': 2, 'down': 3, 'left': 1, 'up': 2}
    action, optimal = analyze_performance(light)
    print("\nLight traffic:")
    print(f"Vehicles: {light}")
    print(f"Agent action: {action}, Optimal action: {optimal}")

if __name__ == "__main__":
    test_rl_accuracy() 