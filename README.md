# Intelligent Cloud Load Balancer Environment

A realistic cloud load balancing simulation environment for training and evaluating AI agents in distributed systems management. This environment simulates real-world challenges faced by cloud load balancers including server failures, priority routing, and dynamic load distribution.

## Overview

The Intelligent Cloud Load Balancer Environment provides a comprehensive simulation where agents must distribute incoming requests across multiple servers while optimizing for:
- **Performance**: Minimizing response times and maximizing throughput
- **Cost**: Reducing operational expenses while maintaining quality
- **Reliability**: Ensuring high availability and graceful failure handling

This environment models genuine cloud infrastructure challenges that DevOps and SRE teams face daily, making it valuable for training autonomous systems for cloud management.

## Environment Description

### Real-World Motivation

Load balancing is a critical component in modern cloud infrastructure. Real load balancers must:
- Distribute traffic across multiple servers to prevent overload
- Handle server failures and route around degraded infrastructure
- Prioritize critical requests while maintaining fairness
- Balance cost efficiency with performance requirements
- Adapt to changing traffic patterns and system conditions

This environment captures these challenges in a controlled, reproducible setting suitable for AI agent training and evaluation.

### Action Space

The agent selects which server should handle the next incoming request:

```python
Action(
    server_id: str,           # Target server (e.g., "server_0", "server_1")
    request_id: Optional[str] # Specific request ID (for advanced tasks)
)
```

### Observation Space

Each step provides complete system visibility:

```python
Observation(
    servers: List[Server],              # All server states
    pending_requests: List[Request],    # Queue of waiting requests
    current_step: int,                  # Current episode step
    total_requests_processed: int,      # Total successful requests
    average_response_time: float,       # Current avg response time (ms)
    total_cost: float,                  # Accumulated cost ($)
    failed_requests: int,               # Failed request count
    task_type: TaskType,               # Current task
    task_progress: float               # Completion progress (0-1)
)
```

#### Server Properties
- `id`: Unique server identifier
- `current_load`/`max_capacity`: Current and maximum load
- `status`: Health state (healthy, degraded, failed, maintenance)
- `response_time_ms`: Typical response time
- `cost_per_request`: Operational cost per request
- `failure_rate`: Probability of request failure

#### Request Properties
- `priority`: Low, Normal, High, or Critical
- `size_mb`: Request size in megabytes
- `expected_response_time_ms`: SLA requirement

## Tasks and Difficulty Levels

### 1. Basic Load Balancing (Easy)
**Objective**: Distribute requests evenly across healthy servers

**Success Criteria**:
- Load variance < 30%
- Failure rate < 10%
- Cost efficiency > 70%

**Challenges**:
- Basic load distribution
- Simple capacity management
- Cost awareness

### 2. Priority Routing (Medium)
**Objective**: Handle requests with different priority levels effectively

**Success Criteria**:
- Priority request processing > 85%
- Overall efficiency > 75%
- Balanced load maintenance

**Challenges**:
- Request prioritization
- Mixed workload handling
- Performance trade-offs

### 3. Failover Management (Hard)
**Objective**: Maintain service availability during server failures

**Success Criteria**:
- Availability > 90%
- Graceful degradation
- Minimal service disruption

**Challenges**:
- Dynamic server failures
- Cascading failure prevention
- Rapid adaptation to infrastructure changes

## Reward Function

The reward function provides dense, informative feedback combining multiple objectives:

```
Reward = 0.3 × LoadBalance + 0.3 × SuccessRate + 0.2 × CostEfficiency + 0.2 × TaskSpecific
```

- **Load Balance**: Rewards balanced server utilization
- **Success Rate**: Rewards successful request processing
- **Cost Efficiency**: Rewards cost-effective decisions
- **Task Specific**: Additional rewards based on current task objectives

## Setup and Usage

### Local Development

1. **Clone and Install Dependencies**:
```bash
git clone <repository-url>
cd intelligent-cloud-load-balancer
pip install -r requirements.txt
```

2. **Start the Server**:
```bash
python server.py
```
The server will start on `http://localhost:7860`

3. **Run Inference**:
```bash
# Set environment variables
export API_BASE_URL="https://router.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="your-api-key"

# Run inference
python inference.py
```

### Docker Deployment

```bash
# Build image
docker build -t load-balancer-env .

# Run container
docker run -p 7860:7860 load-balancer-env
```

### Hugging Face Spaces Deployment

1. Create a new Space on Hugging Face
2. Upload all files to the Space
3. The Space will automatically build and deploy using the provided Dockerfile

## API Endpoints

### Core OpenEnv Endpoints

- `POST /reset` - Reset environment with task type
- `POST /step` - Execute one environment step
- `GET /state` - Get current environment state
- `GET /health` - Health check endpoint

### Additional Endpoints

- `GET /tasks` - Get available task information
- `POST /evaluate` - Evaluate completed episode

### Example Usage

```python
import aiohttp

async def run_episode():
    # Reset environment
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:7860/reset", 
                               json={"task_type": "basic_load"}) as resp:
            obs = await resp.json()
        
        # Run steps
        for step in range(20):
            action = {"server_id": "server_0"}
            async with session.post("http://localhost:7860/step", 
                                   json={"action": action}) as resp:
                result = await resp.json()
                if result["done"]:
                    break
```

## Baseline Performance

Expected baseline scores for a well-tuned agent:

| Task | Difficulty | Baseline Score | Target Score |
|------|------------|----------------|--------------|
| Basic Load Balancing | Easy | 0.65 | 0.80 |
| Priority Routing | Medium | 0.55 | 0.75 |
| Failover Management | Hard | 0.45 | 0.70 |

## Environment Configuration

### Environment Variables

- `API_BASE_URL`: OpenAI API endpoint (default: `https://router.huggingface.co/v1`)
- `MODEL_NAME`: Model identifier (default: `Qwen/Qwen2.5-72B-Instruct`)
- `HF_TOKEN`/`API_KEY`: API authentication token
- `LOAD_BALANCER_TASK`: Task type for inference (default: `basic_load`)
- `SERVER_URL`: Environment server URL (default: `http://localhost:7860`)

### Customization

The environment can be customized by modifying parameters in `load_balancer_env.py`:

- Server count and properties
- Request generation patterns
- Failure rates and recovery times
- Reward function weights
- Task-specific parameters

## Validation

This environment is fully OpenEnv compliant and passes all validation checks:

```bash
# Install openenv-core
pip install openenv-core

# Validate environment
openenv validate
```

The validation checks:
- OpenEnv interface compliance
- Docker build compatibility
- API endpoint functionality
- Baseline inference execution

## Architecture

### Components

1. **LoadBalancerEnv**: Core environment logic
2. **TaskGraders**: Task-specific evaluation logic
3. **FastAPI Server**: HTTP API interface
4. **Inference Script**: Baseline agent implementation

### Design Principles

- **Realism**: Models actual cloud infrastructure challenges
- **Transparency**: Clear action and observation spaces
- **Reproducibility**: Deterministic behavior with fixed seeds
- **Extensibility**: Easy to add new tasks and metrics
- **Performance**: Efficient for large-scale training

## Contributing

To contribute to this environment:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `openenv validate` passes
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

This environment is designed to meet the OpenEnv specification and provides a realistic simulation of cloud load balancing challenges. It demonstrates how complex real-world systems can be modeled for AI agent training and evaluation.
