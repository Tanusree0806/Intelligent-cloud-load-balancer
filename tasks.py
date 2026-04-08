#!/usr/bin/env python3
"""
Task definitions and graders for the Intelligent Cloud Load Balancer environment
"""

from typing import Dict, Any, List, Tuple
from load_balancer_env import LoadBalancerEnv, TaskType, Action, Observation


class TaskGrader:
    """Base class for task grading"""
    
    def __init__(self, task_type: TaskType):
        self.task_type = task_type
        self.env = LoadBalancerEnv(task_type)
    
    def evaluate_episode(self, actions: List[Action], observations: List[Observation], 
                        rewards: List[float]) -> float:
        """Evaluate a complete episode and return score (0.0 to 1.0)"""
        raise NotImplementedError
    
    def get_task_description(self) -> str:
        """Get task description"""
        raise NotImplementedError
    
    def get_difficulty(self) -> str:
        """Get task difficulty level"""
        raise NotImplementedError


class BasicLoadGrader(TaskGrader):
    """Grader for Basic Load Balancing task (Easy)"""
    
    def __init__(self):
        super().__init__(TaskType.BASIC_LOAD)
    
    def get_task_description(self) -> str:
        return """Basic Load Balancing (Easy):
Distribute incoming requests evenly across available servers. Focus on:
- Maintaining balanced server loads
- Minimizing failed requests
- Keeping costs reasonable
- Processing requests efficiently

Success criteria: Load variance < 0.3, failure rate < 10%, cost efficiency > 70%"""
    
    def get_difficulty(self) -> str:
        return "Easy"
    
    def evaluate_episode(self, actions: List[Action], observations: List[Observation], 
                        rewards: List[float]) -> float:
        if not observations:
            return 0.0
        
        final_obs = observations[-1]
        
        # Load balance score (40%)
        if self.env.servers:
            loads = [s.current_load / s.max_capacity for s in self.env.servers if s.is_available()]
            if loads:
                load_variance = max(loads) - min(loads)
                load_balance_score = max(0, 1.0 - (load_variance / 1.0))  # Normalize to 0-1
            else:
                load_balance_score = 0.0
        else:
            load_balance_score = 0.0
        
        # Success rate score (30%)
        total_requests = final_obs.total_requests_processed + final_obs.failed_requests
        success_rate = final_obs.total_requests_processed / max(1, total_requests)
        success_score = success_rate
        
        # Cost efficiency score (20%)
        cost_per_request = final_obs.total_cost / max(1, final_obs.total_requests_processed)
        cost_score = max(0, 1.0 - (cost_per_request / 0.05))  # Normalize assuming 0.05 is high cost
        
        # Response time score (10%)
        response_time_score = max(0, 1.0 - (final_obs.average_response_time / 500))  # Normalize to 500ms
        
        # Combine scores
        final_score = (load_balance_score * 0.4 + 
                      success_score * 0.3 + 
                      cost_score * 0.2 + 
                      response_time_score * 0.1)
        
        return max(0.0, min(1.0, final_score))


class PriorityRoutingGrader(TaskGrader):
    """Grader for Priority Routing task (Medium)"""
    
    def __init__(self):
        super().__init__(TaskType.PRIORITY_ROUTING)
    
    def get_task_description(self) -> str:
        return """Priority Routing (Medium):
Handle requests with different priority levels effectively. Focus on:
- Processing high/critical priority requests first
- Maintaining reasonable load balance
- Minimizing priority request failures
- Adapting to varying request patterns

Success criteria: Priority request processing > 85%, overall efficiency > 75%"""
    
    def get_difficulty(self) -> str:
        return "Medium"
    
    def evaluate_episode(self, actions: List[Action], observations: List[Observation], 
                        rewards: List[float]) -> float:
        if not observations:
            return 0.0
        
        final_obs = observations[-1]
        
        # Priority handling score (50%)
        # This requires analyzing the request history
        priority_requests = 0
        priority_processed = 0
        
        # Reconstruct request processing from environment state
        all_requests = []  # This would be tracked in a real implementation
        # For now, use the processed requests count as a proxy
        priority_score = min(1.0, final_obs.total_requests_processed / 15)  # Assume 15 is good
        
        # Load balance score (20%)
        if self.env.servers:
            loads = [s.current_load / s.max_capacity for s in self.env.servers if s.is_available()]
            if loads:
                load_variance = max(loads) - min(loads)
                load_balance_score = max(0, 1.0 - (load_variance / 1.0))
            else:
                load_balance_score = 0.0
        else:
            load_balance_score = 0.0
        
        # Success rate score (20%)
        total_requests = final_obs.total_requests_processed + final_obs.failed_requests
        success_rate = final_obs.total_requests_processed / max(1, total_requests)
        success_score = success_rate
        
        # Adaptability score (10%) - based on reward variance
        if len(rewards) > 5:
            reward_improvement = (rewards[-1] - rewards[0]) / max(0.001, abs(rewards[0]))
            adaptability_score = max(0, min(1, (reward_improvement + 1) / 2))
        else:
            adaptability_score = 0.5
        
        # Combine scores
        final_score = (priority_score * 0.5 + 
                      load_balance_score * 0.2 + 
                      success_score * 0.2 + 
                      adaptability_score * 0.1)
        
        return max(0.0, min(1.0, final_score))


class FailoverManagementGrader(TaskGrader):
    """Grader for Failover Management task (Hard)"""
    
    def __init__(self):
        super().__init__(TaskType.FAILOVER_MANAGEMENT)
    
    def get_task_description(self) -> str:
        return """Failover Management (Hard):
Maintain service availability during server failures. Focus on:
- Detecting and avoiding failed servers
- Redistributing load when servers fail
- Maintaining high availability
- Handling cascading failures

Success criteria: Availability > 90%, graceful degradation, minimal service disruption"""
    
    def get_difficulty(self) -> str:
        return "Hard"
    
    def evaluate_episode(self, actions: List[Action], observations: List[Observation], 
                        rewards: List[float]) -> float:
        if not observations:
            return 0.0
        
        final_obs = observations[-1]
        
        # Availability score (40%)
        healthy_servers = sum(1 for s in self.env.servers if s.is_available())
        availability_score = healthy_servers / len(self.env.servers)
        
        # Resilience score (30%) - based on handling failures
        # Check if agent avoided failed servers
        failed_servers = sum(1 for s in self.env.servers if s.status.value == "failed")
        if failed_servers > 0:
            # Bonus for maintaining performance despite failures
            resilience_score = availability_score * (1 - (final_obs.failed_requests / max(1, final_obs.total_requests_processed)))
        else:
            resilience_score = availability_score
        
        # Recovery score (20%) - based on reward recovery after failures
        if len(rewards) > 10:
            # Look for recovery patterns
            mid_point = len(rewards) // 2
            early_avg = sum(rewards[:mid_point]) / mid_point
            late_avg = sum(rewards[mid_point:]) / (len(rewards) - mid_point)
            recovery_score = max(0, min(1, (late_avg - early_avg + 1) / 2))
        else:
            recovery_score = 0.5
        
        # Efficiency score (10%)
        efficiency_score = max(0, 1.0 - (final_obs.total_cost / max(1, final_obs.total_requests_processed) / 0.05))
        
        # Combine scores
        final_score = (availability_score * 0.4 + 
                      resilience_score * 0.3 + 
                      recovery_score * 0.2 + 
                      efficiency_score * 0.1)
        
        return max(0.0, min(1.0, final_score))


def get_task_grader(task_type: TaskType) -> TaskGrader:
    """Get the appropriate grader for a task type"""
    if task_type == TaskType.BASIC_LOAD:
        return BasicLoadGrader()
    elif task_type == TaskType.PRIORITY_ROUTING:
        return PriorityRoutingGrader()
    elif task_type == TaskType.FAILOVER_MANAGEMENT:
        return FailoverManagementGrader()
    else:
        raise ValueError(f"Unknown task type: {task_type}")


def evaluate_task(task_type: TaskType, actions: List[Action], 
                 observations: List[Observation], rewards: List[float]) -> float:
    """Evaluate a task and return score"""
    grader = get_task_grader(task_type)
    return grader.evaluate_episode(actions, observations, rewards)


def get_all_task_info() -> Dict[str, Dict[str, str]]:
    """Get information about all available tasks"""
    tasks = {
        TaskType.BASIC_LOAD: BasicLoadGrader(),
        TaskType.PRIORITY_ROUTING: PriorityRoutingGrader(),
        TaskType.FAILOVER_MANAGEMENT: FailoverManagementGrader()
    }
    
    return {
        task_type.value: {
            "description": grader.get_task_description(),
            "difficulty": grader.get_difficulty()
        }
        for task_type, grader in tasks.items()
    }
