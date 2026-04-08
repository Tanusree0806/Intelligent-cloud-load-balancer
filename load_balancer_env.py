#!/usr/bin/env python3
"""
Intelligent Cloud Load Balancer Environment

This environment simulates a real-world cloud load balancing task where agents
must distribute incoming requests across multiple servers while optimizing for
performance, cost, and reliability.
"""

import random
import time
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from pydantic import BaseModel, Field
import asyncio


class TaskType(str, Enum):
    """Types of load balancing tasks"""
    BASIC_LOAD = "basic_load"  # Easy: distribute load evenly
    PRIORITY_ROUTING = "priority_routing"  # Medium: handle priority requests
    FAILOVER_MANAGEMENT = "failover_management"  # Hard: handle server failures


class ServerStatus(str, Enum):
    """Server status enumeration"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILED = "failed"
    MAINTENANCE = "maintenance"


class RequestPriority(str, Enum):
    """Request priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class Server(BaseModel):
    """Server model representing a backend server"""
    id: str
    host: str
    port: int
    max_capacity: int = 100
    current_load: int = 0
    status: ServerStatus = ServerStatus.HEALTHY
    response_time_ms: float = 50.0
    cost_per_request: float = 0.01
    failure_rate: float = 0.01
    last_health_check: float = 0.0
    
    def available_capacity(self) -> int:
        return max(0, self.max_capacity - self.current_load)
    
    def is_available(self) -> bool:
        return self.status in [ServerStatus.HEALTHY, ServerStatus.DEGRADED] and self.available_capacity() > 0
    
    def add_load(self, amount: int = 1) -> bool:
        if self.available_capacity() >= amount:
            self.current_load += amount
            return True
        return False
    
    def remove_load(self, amount: int = 1):
        self.current_load = max(0, self.current_load - amount)


class IncomingRequest(BaseModel):
    """Incoming request model"""
    id: str
    priority: RequestPriority = RequestPriority.NORMAL
    size_mb: float = 1.0
    expected_response_time_ms: float = 100.0
    timestamp: float = 0.0


class Action(BaseModel):
    """Agent action - assign request to server"""
    server_id: str = Field(..., description="ID of server to handle the request")
    request_id: Optional[str] = Field(None, description="Specific request ID to handle (for advanced tasks)")


class Observation(BaseModel):
    """Environment observation"""
    servers: List[Server] = Field(..., description="List of all servers")
    pending_requests: List[IncomingRequest] = Field(..., description="Queue of pending requests")
    current_step: int = Field(..., description="Current step number")
    total_requests_processed: int = Field(..., description="Total requests processed so far")
    average_response_time: float = Field(..., description="Average response time in ms")
    total_cost: float = Field(..., description="Total cost incurred")
    failed_requests: int = Field(..., description="Number of failed requests")
    task_type: TaskType = Field(..., description="Current task type")
    task_progress: float = Field(..., description="Task completion progress (0-1)")


class LoadBalancerEnv:
    """Intelligent Cloud Load Balancer Environment"""
    
    def __init__(self, task_type: TaskType = TaskType.BASIC_LOAD):
        self.task_type = task_type
        self.servers: List[Server] = []
        self.pending_requests: List[IncomingRequest] = []
        self.processed_requests: List[IncomingRequest] = []
        self.current_step = 0
        self.max_steps = 50
        self.request_counter = 0
        self.total_cost = 0.0
        self.failed_requests = 0
        self.start_time = time.time()
        
        # Task-specific parameters
        self.task_params = self._get_task_params()
        
        # Initialize servers
        self._initialize_servers()
    
    def _get_task_params(self) -> Dict[str, Any]:
        """Get parameters for the current task type"""
        if self.task_type == TaskType.BASIC_LOAD:
            return {
                "num_servers": 5,
                "request_rate": 2,
                "failure_probability": 0.01,
                "target_efficiency": 0.8
            }
        elif self.task_type == TaskType.PRIORITY_ROUTING:
            return {
                "num_servers": 5,
                "request_rate": 3,
                "failure_probability": 0.02,
                "priority_ratio": 0.3,
                "target_efficiency": 0.85
            }
        else:  # FAILOVER_MANAGEMENT
            return {
                "num_servers": 5,
                "request_rate": 4,
                "failure_probability": 0.05,
                "server_failure_rate": 0.1,
                "target_efficiency": 0.9
            }
    
    def _initialize_servers(self):
        """Initialize server pool"""
        self.servers = []
        for i in range(self.task_params["num_servers"]):
            server = Server(
                id=f"server_{i}",
                host=f"192.168.1.{10 + i}",
                port=8080 + i,
                max_capacity=random.randint(80, 120),
                response_time_ms=random.uniform(30, 100),
                cost_per_request=random.uniform(0.005, 0.02),
                failure_rate=random.uniform(0.005, 0.02)
            )
            self.servers.append(server)
    
    def _generate_request(self) -> IncomingRequest:
        """Generate a new incoming request"""
        self.request_counter += 1
        
        # Priority routing task has more priority requests
        if self.task_type == TaskType.PRIORITY_ROUTING and random.random() < self.task_params["priority_ratio"]:
            priority = random.choice([RequestPriority.HIGH, RequestPriority.CRITICAL])
        else:
            priority = random.choice([RequestPriority.LOW, RequestPriority.NORMAL, RequestPriority.HIGH])
        
        return IncomingRequest(
            id=f"req_{self.request_counter}",
            priority=priority,
            size_mb=random.uniform(0.5, 5.0),
            expected_response_time_ms=random.uniform(50, 200),
            timestamp=time.time()
        )
    
    def _update_server_health(self):
        """Update server health status (for failover task)"""
        if self.task_type == TaskType.FAILOVER_MANAGEMENT:
            for server in self.servers:
                if server.status == ServerStatus.HEALTHY and random.random() < self.task_params["server_failure_rate"]:
                    server.status = ServerStatus.FAILED
                elif server.status == ServerStatus.FAILED and random.random() < 0.1:  # Recovery chance
                    server.status = ServerStatus.DEGRADED
    
    def _process_request(self, request: IncomingRequest, server: Server) -> Tuple[bool, float]:
        """Process a request on a server and return (success, response_time)"""
        # Simulate processing time
        base_time = server.response_time_ms
        priority_multiplier = {
            RequestPriority.LOW: 1.5,
            RequestPriority.NORMAL: 1.0,
            RequestPriority.HIGH: 0.8,
            RequestPriority.CRITICAL: 0.5
        }
        
        processing_time = base_time * priority_multiplier[request.priority] * (1 + request.size_mb / 10)
        
        # Check for failure
        failure_chance = server.failure_rate
        if server.status == ServerStatus.DEGRADED:
            failure_chance *= 2
        elif server.status == ServerStatus.FAILED:
            failure_chance = 1.0
        
        success = random.random() > failure_chance
        return success, processing_time
    
    def reset(self) -> Observation:
        """Reset the environment to initial state"""
        self.current_step = 0
        self.request_counter = 0
        self.total_cost = 0.0
        self.failed_requests = 0
        self.start_time = time.time()
        self.pending_requests = []
        self.processed_requests = []
        
        # Reinitialize servers
        self._initialize_servers()
        
        # Generate initial requests
        for _ in range(random.randint(3, 7)):
            self.pending_requests.append(self._generate_request())
        
        return self._get_observation()
    
    def step(self, action: Action) -> Tuple[Observation, float, bool, Dict[str, Any]]:
        """Execute one step in the environment"""
        self.current_step += 1
        
        # Update server health for failover scenarios
        self._update_server_health()
        
        # Generate new requests
        new_requests = random.randint(1, self.task_params["request_rate"])
        for _ in range(new_requests):
            self.pending_requests.append(self._generate_request())
        
        # Process action
        reward = 0.0
        info = {"action_result": "no_action"}
        
        if self.pending_requests and action.server_id:
            # Find target server
            target_server = next((s for s in self.servers if s.id == action.server_id), None)
            
            if target_server and target_server.is_available():
                # Get highest priority request (or specific request if specified)
                if action.request_id:
                    request = next((r for r in self.pending_requests if r.id == action.request_id), None)
                else:
                    # Sort by priority (critical first)
                    self.pending_requests.sort(key=lambda r: (
                        r.priority.value != "critical",
                        r.priority.value != "high", 
                        r.priority.value != "normal",
                        r.timestamp
                    ))
                    request = self.pending_requests[0]
                
                if request:
                    # Process the request
                    success, response_time = self._process_request(request, target_server)
                    
                    if success:
                        target_server.add_load(1)
                        self.processed_requests.append(request)
                        self.pending_requests.remove(request)
                        self.total_cost += target_server.cost_per_request
                        
                        # Calculate reward based on efficiency
                        efficiency_reward = 1.0 - (response_time / 1000)  # Lower response time = higher reward
                        priority_bonus = {
                            RequestPriority.LOW: 0.0,
                            RequestPriority.NORMAL: 0.1,
                            RequestPriority.HIGH: 0.2,
                            RequestPriority.CRITICAL: 0.3
                        }
                        reward = efficiency_reward + priority_bonus[request.priority]
                        info["action_result"] = "success"
                    else:
                        self.failed_requests += 1
                        reward = -0.5  # Penalty for failed request
                        info["action_result"] = "failed"
            else:
                reward = -0.2  # Penalty for invalid action
                info["action_result"] = "invalid_server"
        
        # Simulate request processing (reduce load over time)
        for server in self.servers:
            if server.current_load > 0:
                server.remove_load(random.randint(0, min(2, server.current_load)))
        
        # Check if episode should end
        done = self.current_step >= self.max_steps or len(self.pending_requests) > 20
        
        # Calculate task-specific reward
        task_reward = self._calculate_task_reward()
        reward += task_reward
        
        observation = self._get_observation()
        
        return observation, reward, done, info
    
    def _calculate_task_reward(self) -> float:
        """Calculate task-specific reward component"""
        if self.task_type == TaskType.BASIC_LOAD:
            # Reward for balanced load distribution
            if self.servers:
                loads = [s.current_load / s.max_capacity for s in self.servers if s.is_available()]
                if loads:
                    load_variance = max(loads) - min(loads)
                    return max(0, 1.0 - load_variance) * 0.5
            return 0.0
        
        elif self.task_type == TaskType.PRIORITY_ROUTING:
            # Reward for handling priority requests well
            priority_processed = sum(1 for r in self.processed_requests 
                                   if r.priority in [RequestPriority.HIGH, RequestPriority.CRITICAL])
            total_priority = sum(1 for r in self.processed_requests + self.pending_requests 
                               if r.priority in [RequestPriority.HIGH, RequestPriority.CRITICAL])
            if total_priority > 0:
                return (priority_processed / total_priority) * 0.5
            return 0.0
        
        else:  # FAILOVER_MANAGEMENT
            # Reward for maintaining availability during failures
            healthy_servers = sum(1 for s in self.servers if s.is_available())
            total_servers = len(self.servers)
            availability_ratio = healthy_servers / total_servers
            return availability_ratio * 0.5
    
    def _get_observation(self) -> Observation:
        """Get current environment state"""
        avg_response_time = 0.0
        if self.processed_requests:
            # Simulate average response time based on server loads
            avg_response_time = sum(s.response_time_ms * (1 + s.current_load / s.max_capacity) 
                                  for s in self.servers) / len(self.servers)
        
        # Calculate task progress
        task_progress = min(1.0, self.current_step / self.max_steps)
        
        return Observation(
            servers=self.servers.copy(),
            pending_requests=self.pending_requests.copy(),
            current_step=self.current_step,
            total_requests_processed=len(self.processed_requests),
            average_response_time=avg_response_time,
            total_cost=self.total_cost,
            failed_requests=self.failed_requests,
            task_type=self.task_type,
            task_progress=task_progress
        )
    
    def state(self) -> Dict[str, Any]:
        """Get full environment state for debugging"""
        return {
            "task_type": self.task_type,
            "current_step": self.current_step,
            "max_steps": self.max_steps,
            "servers": [s.dict() for s in self.servers],
            "pending_requests": [r.dict() for r in self.pending_requests],
            "processed_requests": len(self.processed_requests),
            "total_cost": self.total_cost,
            "failed_requests": self.failed_requests,
            "task_params": self.task_params
        }
    
    def get_score(self) -> float:
        """Calculate overall performance score (0.0 to 1.0)"""
        if not self.processed_requests:
            return 0.0
        
        # Base score from processed requests
        processed_score = min(1.0, len(self.processed_requests) / 20)
        
        # Penalty for failed requests
        failure_penalty = self.failed_requests / max(1, len(self.processed_requests) + self.failed_requests)
        
        # Cost efficiency (lower cost is better)
        cost_score = max(0, 1.0 - (self.total_cost / 10.0))
        
        # Task-specific scoring
        task_score = 0.0
        if self.task_type == TaskType.BASIC_LOAD:
            # Load balance score
            loads = [s.current_load / s.max_capacity for s in self.servers if s.is_available()]
            if loads:
                task_score = max(0, 1.0 - (max(loads) - min(loads)))
        
        elif self.task_type == TaskType.PRIORITY_ROUTING:
            # Priority handling score
            high_priority_processed = sum(1 for r in self.processed_requests 
                                        if r.priority in [RequestPriority.HIGH, RequestPriority.CRITICAL])
            total_high_priority = sum(1 for r in self.processed_requests + self.pending_requests 
                                    if r.priority in [RequestPriority.HIGH, RequestPriority.CRITICAL])
            if total_high_priority > 0:
                task_score = high_priority_processed / total_high_priority
        
        else:  # FAILOVER_MANAGEMENT
            # Availability score
            healthy_servers = sum(1 for s in self.servers if s.is_available())
            task_score = healthy_servers / len(self.servers)
        
        # Combine scores
        final_score = (processed_score * 0.3 + 
                      (1 - failure_penalty) * 0.3 + 
                      cost_score * 0.2 + 
                      task_score * 0.2)
        
        return max(0.0, min(1.0, final_score))
