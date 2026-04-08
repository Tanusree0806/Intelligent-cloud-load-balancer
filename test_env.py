#!/usr/bin/env python3
"""
Quick test script to verify the load balancer environment works correctly
"""

from load_balancer_env import LoadBalancerEnv, Action, TaskType
from tasks import get_all_task_info, evaluate_task

def test_basic_functionality():
    """Test basic environment functionality"""
    print("Testing Load Balancer Environment...")
    
    # Test all task types
    for task_type in [TaskType.BASIC_LOAD, TaskType.PRIORITY_ROUTING, TaskType.FAILOVER_MANAGEMENT]:
        print(f"\n--- Testing {task_type.value} ---")
        
        env = LoadBalancerEnv(task_type)
        obs = env.reset()
        
        print(f"Task: {obs.task_type}")
        print(f"Servers: {len(obs.servers)}")
        print(f"Pending requests: {len(obs.pending_requests)}")
        print(f"Step: {obs.current_step}")
        
        # Run a few steps
        actions = []
        observations = [obs]
        rewards = []
        
        for step in range(5):
            if obs.pending_requests and env.servers:
                # Choose first available server
                available_servers = [s for s in env.servers if s.is_available()]
                if available_servers:
                    action = Action(server_id=available_servers[0].id)
                    actions.append(action)
                    
                    obs, reward, done, info = env.step(action)
                    observations.append(obs)
                    rewards.append(reward)
                    
                    print(f"Step {step+1}: Action={action.server_id}, Reward={reward:.2f}, Done={done}")
                    
                    if done:
                        break
        
        # Calculate score
        score = env.get_score()
        print(f"Final Score: {score:.3f}")
        
        # Test task evaluation
        task_score = evaluate_task(task_type, actions, observations, rewards)
        print(f"Task Score: {task_score:.3f}")
    
    # Test task info
    print("\n--- Available Tasks ---")
    tasks = get_all_task_info()
    for task_name, info in tasks.items():
        print(f"{task_name}: {info['difficulty']} - {info['description'][:50]}...")
    
    print("\nAll tests completed successfully!")

if __name__ == "__main__":
    test_basic_functionality()
