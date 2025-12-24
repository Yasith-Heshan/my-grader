# Architecture Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend Application                         │
│                  (React + TypeScript)                           │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP/REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Backend Server (FastAPI)                     │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │            Grading Service (grader_service.py)           │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │         ExecutorFactory                             │ │  │
│  │  │  - Selects appropriate executor                     │ │  │
│  │  │  - Handles configuration                            │ │  │
│  │  │  - Manages fallback logic                           │ │  │
│  │  └──────────────┬────────────────────────┬─────────────┘ │  │
│  │                 │                        │                │  │
│  │    ┌────────────▼──────────┐  ┌──────────▼────────────┐ │  │
│  │    │   DockerExecutor      │  │   LocalExecutor       │ │  │
│  │    │   (Production)        │  │   (Development)       │ │  │
│  │    │                       │  │                        │ │  │
│  │    │ ✅ Secure isolation  │  │ ⚠️  Fast iteration    │ │  │
│  │    │ ✅ Resource limits   │  │ ⚠️  No isolation      │ │  │
│  │    │ ✅ Network disabled  │  │ ⚠️  Dev only          │ │  │
│  │    └───────────┬───────────┘  └────────────────────────┘ │  │
│  └────────────────┼────────────────────────────────────────┘  │
└───────────────────┼───────────────────────────────────────────┘
                    │
                    │ Docker API
                    │
┌───────────────────▼───────────────────────────────────────────┐
│                    Docker Engine                              │
│                                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Container 1  │  │ Container 2  │  │ Container 3  │  ...  │
│  │ Python 3.11  │  │ Python 3.11  │  │ Python 3.11  │       │
│  │              │  │              │  │              │       │
│  │ Student Code │  │ Student Code │  │ Student Code │       │
│  │ + Test Code  │  │ + Test Code  │  │ + Test Code  │       │
│  │              │  │              │  │              │       │
│  │ Isolated     │  │ Isolated     │  │ Isolated     │       │
│  │ Non-root     │  │ Non-root     │  │ Non-root     │       │
│  │ No network   │  │ No network   │  │ No network   │       │
│  │ Read-only FS │  │ Read-only FS │  │ Read-only FS │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
└────────────────────────────────────────────────────────────────┘
```

## Execution Flow

```
Student Submission
        │
        ▼
┌───────────────────┐
│ Grader Service    │
│ receives code     │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│ ExecutorFactory   │
│ creates executor  │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐     Yes    ┌──────────────────┐
│ Docker available? │────────────>│ DockerExecutor   │
└─────────┬─────────┘             └────────┬─────────┘
          │ No                             │
          ▼                                │
┌───────────────────┐                      │
│ Fallback allowed? │                      │
└─────────┬─────────┘                      │
          │ Yes                            │
          ▼                                │
┌───────────────────┐                      │
│ LocalExecutor     │                      │
└─────────┬─────────┘                      │
          │                                │
          └────────────┬───────────────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │ Execute Code Securely  │
          └────────────┬───────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │ Return ExecutionResult │
          │ - success              │
          │ - score                │
          │ - feedback             │
          │ - test_results         │
          └────────────┬───────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │ Cleanup Resources      │
          └────────────┬───────────┘
                       │
                       ▼
          ┌────────────────────────┐
          │ Return to Grader       │
          └────────────────────────┘
```

## Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Host System                             │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Docker Engine                            │  │
│  │                                                        │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │         Container Namespace                    │  │  │
│  │  │                                                 │  │  │
│  │  │  ┌──────────────────────────────────────────┐  │  │  │
│  │  │  │     Resource Limits (cgroups)           │  │  │  │
│  │  │  │  - CPU: 50% max                         │  │  │  │
│  │  │  │  - Memory: 256MB max                    │  │  │  │
│  │  │  │  - PIDs: 50 max                         │  │  │  │
│  │  │  │                                          │  │  │  │
│  │  │  │  ┌───────────────────────────────────┐  │  │  │  │
│  │  │  │  │  Network Namespace                │  │  │  │  │
│  │  │  │  │  🚫 Network Disabled              │  │  │  │  │
│  │  │  │  │                                    │  │  │  │  │
│  │  │  │  │  ┌────────────────────────────┐   │  │  │  │  │
│  │  │  │  │  │  Filesystem (Mount NS)    │   │  │  │  │  │
│  │  │  │  │  │  🔒 Root: Read-only       │   │  │  │  │  │
│  │  │  │  │  │  📝 /tmp: 10MB writable   │   │  │  │  │  │
│  │  │  │  │  │                            │   │  │  │  │  │
│  │  │  │  │  │  ┌─────────────────────┐  │   │  │  │  │  │
│  │  │  │  │  │  │  User Namespace    │  │   │  │  │  │  │
│  │  │  │  │  │  │  👤 UID 1000       │  │   │  │  │  │  │
│  │  │  │  │  │  │  🚫 No privileges  │  │   │  │  │  │  │
│  │  │  │  │  │  │                     │  │   │  │  │  │  │
│  │  │  │  │  │  │  ┌──────────────┐  │  │   │  │  │  │  │
│  │  │  │  │  │  │  │ Student Code │  │  │   │  │  │  │  │
│  │  │  │  │  │  │  │ + Test Code  │  │  │   │  │  │  │  │
│  │  │  │  │  │  │  └──────────────┘  │  │   │  │  │  │  │
│  │  │  │  │  │  └─────────────────────┘  │   │  │  │  │  │
│  │  │  │  │  └────────────────────────────┘   │  │  │  │  │
│  │  │  │  └───────────────────────────────────┘  │  │  │  │
│  │  │  └──────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘

Security Layers (Outside → Inside):
1. Host System
2. Docker Engine
3. Container Namespace Isolation
4. Resource Limits (CPU, Memory, PIDs)
5. Network Namespace (Disabled)
6. Filesystem Restrictions (Read-only)
7. User Namespace (Non-root)
8. Student Code Execution
```

## Component Interaction

```
┌─────────────────┐
│ grader_service  │
│     .py         │
└────────┬────────┘
         │
         │ import ExecutorFactory
         │
         ▼
┌──────────────────────────────────────┐
│ executor_factory.py                  │
│                                      │
│  create_executor()                   │
│    ├─ Check config                   │
│    ├─ Try Docker                     │
│    └─ Fallback to Local if allowed   │
└────────┬─────────────────────────────┘
         │
         ├──────────────────┬────────────────────┐
         │                  │                    │
         ▼                  ▼                    ▼
┌─────────────────┐  ┌──────────────┐  ┌─────────────────┐
│docker_executor  │  │local_executor│  │executor_config  │
│     .py         │  │     .py      │  │     .py         │
│                 │  │              │  │                 │
│ DockerExecutor  │  │LocalExecutor │  │ ExecutorConfig  │
│   class         │  │   class      │  │   class         │
└────────┬────────┘  └──────┬───────┘  └─────────────────┘
         │                  │
         │                  │
         │    implements    │
         └──────────┬───────┘
                    │
                    ▼
         ┌────────────────────┐
         │executor_interface  │
         │     .py            │
         │                    │
         │ CodeExecutor       │
         │   (Abstract)       │
         │                    │
         │ ExecutionConfig    │
         │ ExecutionResult    │
         └────────────────────┘
```

## Data Flow

```
Input: Student Code + Test Code
           │
           ▼
┌──────────────────────────┐
│ ExecutionConfig          │
│ - language: python       │
│ - timeout: 10s           │
│ - memory: 256m           │
│ - cpu_quota: 50%         │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ DockerExecutor           │
│ 1. Create temp dir       │
│ 2. Write code files      │
│ 3. Create container      │
│ 4. Execute code          │
│ 5. Collect results       │
│ 6. Parse output          │
│ 7. Cleanup               │
└──────────┬───────────────┘
           │
           ▼
┌──────────────────────────┐
│ ExecutionResult          │
│ - success: true          │
│ - passed: true           │
│ - score: 8.5             │
│ - max_score: 10.0        │
│ - stdout: "..."          │
│ - stderr: ""             │
│ - feedback: "Correct!"   │
│ - execution_time: 0.5s   │
│ - test_results: [...]    │
└──────────┬───────────────┘
           │
           ▼
Output: Grading Results
```

## File Organization

```
backend/
├── config/
│   ├── __init__.py
│   └── executor_config.py          ← Configuration
│
├── utils/
│   ├── __init__.py
│   ├── executor_interface.py       ← Abstract base
│   ├── docker_executor.py          ← Docker implementation
│   ├── local_executor.py           ← Local implementation
│   ├── executor_factory.py         ← Factory pattern
│   └── executor_examples.py        ← Usage examples
│
├── docker/
│   ├── python/
│   │   ├── Dockerfile              ← Container definition
│   │   └── requirements.txt        ← Python packages
│   ├── build.ps1                   ← Windows build
│   ├── build.sh                    ← Linux/Mac build
│   └── README.md                   ← Docker docs
│
├── services/
│   └── grader_service.py           ← Uses executor
│
├── .env.example                    ← Config template
├── EXECUTOR_README.md              ← Main docs
├── DOCKER_EXECUTOR_QUICKSTART.md   ← Quick start
├── MIGRATION_GUIDE.md              ← Integration guide
├── IMPLEMENTATION_SUMMARY.md       ← Summary
└── IMPLEMENTATION_COMPLETE.txt     ← Status
```

## Deployment Architecture

```
Development Environment:
┌─────────────────────────────┐
│ Developer Machine           │
│                             │
│ Backend Server              │
│   ├─ Local Executor         │ ← Fast iteration
│   └─ Docker (optional)      │ ← Testing
│                             │
│ DOCKER_ENABLED=false        │
│ FALLBACK_TO_LOCAL=true      │
└─────────────────────────────┘


Production Environment:
┌─────────────────────────────┐
│ Production Server           │
│                             │
│ Backend Server              │
│   └─ Docker Executor        │ ← Secure only
│                             │
│ Docker Engine               │
│   ├─ Container Pool         │
│   ├─ Resource Limits        │
│   └─ Network Isolation      │
│                             │
│ DOCKER_ENABLED=true         │
│ FALLBACK_TO_LOCAL=false     │
│ REQUIRE_DOCKER=true         │
└─────────────────────────────┘
```

## Future Enhancements

```
Current (v1.0):
┌─────────────┐
│ Python Only │
└──────┬──────┘
       │
       ▼
┌──────────────┐
│ Single Host  │
└──────────────┘

Future (v2.0):
┌─────────────┬──────────┬────────┐
│ Python      │JavaScript│ Java   │
└──────┬──────┴──────────┴────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Distributed Execution            │
│  ┌────────┬────────┬────────┐   │
│  │ Host 1 │ Host 2 │ Host 3 │   │
│  └────────┴────────┴────────┘   │
└──────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────┐
│ Container Pool                   │
│ - Pre-warmed containers          │
│ - Faster execution               │
│ - Auto-scaling                   │
└──────────────────────────────────┘
```
