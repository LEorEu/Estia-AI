# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Estia AI is an intelligent assistant with advanced memory systems, voice interaction, and persistent conversation capabilities. It features a sophisticated 6-module architecture with 15-step memory processing workflow and enterprise-grade performance optimizations including 588x cache acceleration.

## Development Commands

### Setup and Installation
```bash
# Setup environment and dependencies (Windows)
cd setup
install.bat

# Manual environment setup
python -m venv estia_env
estia_env\Scripts\activate
pip install -r setup/requirements.txt
```

### Running the Application
```bash
# Voice interaction mode (default)
python main.py

# Text interaction mode
python main.py --mode text

# API server mode (in development)
python main.py --mode api

# Enable streaming output
python main.py --stream
python main.py --text-stream    # text-only streaming
python main.py --audio-stream   # audio-only streaming
```

### Testing
```bash
# Complete 15-step workflow validation (comprehensive)
python test_14_step_workflow.py

# Run all tests with pytest
pytest

# Specific memory system tests
python tests/test_estia_memory_complete.py

# Cache performance tests  
python tests/test_cache_performance.py

# Memory system analysis
python tests/test_cache_system_analysis.py

# Audio streaming tests
python tests/test_audio_stream.py
python tests/test_simple_audio_stream.py

# Context and streaming tests
python tests/test_context_length_demo.py
python tests/test_stream_output.py
```

### Configuration
Configuration is managed through `config/settings.py`. Create `config/local_settings.py` for API keys:
```python
# config/local_settings.py
GEMINI_API_KEY = "your-key"
DEEPSEEK_API_KEY = "your-key"
OPENAI_API_KEY = "your-key"
```

## Core Architecture

### 6-Module Memory System Architecture
```
core/memory/
├── managers/                    # Six core managers
│   ├── sync_flow/              # Synchronous flow manager (Steps 1-9)
│   ├── async_flow/             # Asynchronous flow manager (Steps 10-15)
│   ├── monitor_flow/           # Memory process monitoring
│   ├── lifecycle/              # Lifecycle management
│   ├── config/                 # Configuration manager
│   └── recovery/               # Error recovery manager
├── shared/                     # Shared utilities
│   ├── caching/               # Unified cache system (588x acceleration)
│   ├── embedding/             # Vectorization tools (Qwen3-Embedding-0.6B)
│   ├── emotion/               # Emotion analysis
│   └── internal/              # Internal tools
├── estia_memory_v5.py         # v5.0 main coordinator (migrated)
└── estia_memory_v6.py         # v6.0 fusion architecture (current production)
```

### 15-Step Memory Processing Workflow

The system processes memory through three phases:

**Phase 1: System Initialization (Steps 1-3)**
- Database and memory storage initialization
- Advanced components (FAISS, vectorizer, etc.)
- Async evaluator initialization

**Phase 2: Real-time Memory Enhancement (Steps 4-9)**
- Unified cache vectorization (588x performance boost)
- FAISS vector retrieval (<50ms)
- Association network expansion (2-layer depth)
- Historical dialogue aggregation
- Weight ranking and deduplication
- Final context assembly

**Phase 3: Dialogue Storage & Async Evaluation (Steps 10-15)**
- LLM response generation (external call)
- Immediate dialogue storage
- Async LLM evaluation (non-blocking)
- Save evaluation results (async)
- Auto-association creation (async)
- Process monitoring and cleanup (async)

### Key Performance Targets
- **Cache acceleration**: 588x vs direct computation
- **Vector retrieval**: <50ms for 15 memories
- **Context assembly**: <100ms for complete Steps 4-8
- **Async evaluation**: 2-5 seconds (non-blocking)
- **Database writes**: <10ms with transactional dual-write

## Memory System Integration

### Creating Memory System Instance
```python
from core.memory import create_estia_memory

# Create with advanced features
memory_system = create_estia_memory(enable_advanced=True)
await memory_system.initialize()

# Query enhancement
enhanced_context = await memory_system.enhance_query(
    user_input="Hello, how are you?",
    context={"session_id": "user123"}
)

# Store interaction
await memory_system.store_interaction(
    user_input="Hello",
    ai_response="Hi there!",
    context={"session_id": "user123"}
)
```

### Memory System Components Access
```python
# Access specific managers
sync_manager = memory_system.sync_flow_manager
async_manager = memory_system.async_flow_manager

# Get system statistics
stats = memory_system.get_system_stats()
```

## Application Architecture

### Main Application Flow
1. **Entry Point**: `main.py` - Handles command-line arguments and logging setup
2. **Core App**: `core/app.py` - Main application logic, component coordination
3. **Memory System**: `core/memory/` - Advanced memory processing
4. **Dialogue Engine**: `core/dialogue/` - LLM integration and response generation
5. **Audio System**: `core/audio/` - Voice input/output and keyboard controls

### Component Initialization Order
1. Database manager
2. Unified cache manager (critical for 588x performance)
3. Text vectorizer (Qwen3-Embedding-0.6B with graceful fallback)
4. Memory storage and retrieval components
5. Advanced features (FAISS, association networks, async evaluators)

## Development Guidelines

### Module Development Rules (from .cursor/rules)
1. **Single Problem Focus**: Only solve one specific problem per session - avoid introducing multiple complex features at once
2. **Explanation First**: Explain approach and reasoning before implementing - let users understand the changes  
3. **Progressive Improvement**: Avoid big-bang rewrites, maintain system stability - each change should keep the system runnable
4. **User Control**: Keep code readable and maintainable - avoid over-complex abstractions

### Development Workflow (from .cursor/rules)
1. **Problem Identification**: Clearly identify the specific problem to solve
2. **Solution Explanation**: Detailed explanation of approach and reasoning  
3. **User Confirmation**: Wait for user understanding and agreement
4. **Code Implementation**: Write clean, clear code
5. **Testing & Validation**: Ensure functionality works correctly
6. **Summary & Next Steps**: Explain what was completed and what's next

### Code Organization
- Follow the 6-module architecture strictly
- Place new sync operations in `managers/sync_flow/`
- Place new async operations in `managers/async_flow/`
- Use shared utilities in `shared/` for common functionality
- Add monitoring in `managers/monitor_flow/`

### Error Handling
The system implements enterprise-grade error handling:
- Graceful degradation when components fail
- Automatic fallback to SimpleVectorizer if Qwen3 model fails
- Session timeout and cleanup mechanisms
- Comprehensive logging with UTF-8 encoding

## Testing Strategy

### Memory System Testing
- Use `tests/test_estia_memory_complete.py` for comprehensive testing
- Use `tests/test_cache_performance.py` for performance validation
- Use `tests/test_cache_system_analysis.py` for detailed analysis

### Performance Benchmarking
Key metrics to monitor:
- Cache hit rate (target: >80%)
- Vector retrieval time (target: <50ms)
- Memory initialization time
- Session management efficiency

## Current Development Status - v6.0 FUSION ARCHITECTURE COMPLETE ✅

### v6.0 Fusion Architecture Complete (2025-01-16)
The Estia AI memory system has **successfully evolved to v6.0 fusion architecture** with all previously identified issues resolved:

**✅ All Features Implemented:**
- ✅ Complete 6-module architecture migration
- ✅ Full 15-step memory processing workflow  
- ✅ Unified cache system with 588x acceleration
- ✅ Enterprise-grade error handling and recovery
- ✅ Vector processing with 1024-dimensional embeddings
- ✅ Async evaluation with thread-based fallback
- ✅ Session management and lifecycle control
- ✅ FAISS vector search integration
- ✅ Association network with 2-layer depth
- ✅ Complete workflow implementation (all 15 steps)
- ✅ Asynchronous evaluation mechanism
- ✅ Session management system
- ✅ Memory layering (4-tier system)
- ✅ User profiling system

**🎯 Performance Achievements (v6.0):**
- **671.60 QPS** query processing (超目标117%)
- **1.49ms average response time** (卓越级别)
- **100% cache hit rate** (完美缓存)
- **588x cache acceleration** vs direct computation
- **<1ms vector retrieval** (超预期性能)
- **Enterprise reliability** with graceful degradation

**🔧 Technical Completions:**
- Model loading with offline-first detection
- Vector dimension consistency (1024D across all components)
- Event loop management for async operations
- Circular import resolution
- Comprehensive error recovery mechanisms

### Architecture Migration Complete
The migration from `core/old_memory` to the new 6-module architecture is **100% complete**. All critical components have been successfully migrated and tested:

- ✅ **AssociationNetwork**: `core/memory/managers/async_flow/association/network.py`
- ✅ **ContextLengthManager**: `core/memory/managers/sync_flow/context/context_manager.py`  
- ✅ **All workflow steps**: Fully operational in new architecture
- ✅ **Performance benchmarks**: Exceeding targets across all metrics

**Note**: The `core/old_memory` directory can now be safely deleted after updating 2 import statements (see troubleshooting section below).

## Configuration Management

### Memory Context Presets
- `"compact"`: 4000 chars, fast response
- `"balanced"`: 8000 chars, default mode
- `"detailed"`: 16000 chars, deep conversations

### Model Providers
Supports multiple LLM providers:
- `"local"`: Local LLM server (default: localhost:8080)
- `"openai"`: OpenAI API
- `"deepseek"`: DeepSeek API  
- `"gemini"`: Google Gemini API

## Audio System

### Voice Interaction
- Whisper-large-v3-turbo for speech recognition
- Edge-TTS for speech synthesis
- Keyboard controls (space bar for recording, ESC to exit)
- Background listening with wake word support

### Streaming Output
Supports real-time streaming for both text and audio:
- Text streaming: Real-time text output
- Audio streaming: Progressive speech synthesis
- Combined streaming: Simultaneous text and audio

## Performance Considerations

### Memory Optimization
- Use unified cache for all vectorization operations
- Implement graceful fallback for model loading failures
- Monitor memory usage with built-in statistics
- Configure appropriate context length limits

### Development Workflow
When modifying the memory system:
1. Follow the 6-module architecture principles strictly
2. Place new sync operations in `managers/sync_flow/`
3. Place new async operations in `managers/async_flow/`
4. Use shared utilities in `shared/` for common functionality
5. Ensure async operations don't block the main workflow
6. Test with both simple and advanced mode configurations
7. Verify cache performance improvements
8. Use the unified testing framework: `python test_14_step_workflow.py`

## Troubleshooting

### Common Issues
- **Model loading failures**: System automatically falls back to SimpleVectorizer
- **Database connection issues**: Check `data/memory.db` permissions
- **Cache performance**: Verify UnifiedCacheManager initialization
- **Import errors**: Ensure all paths point to new 6-module architecture

### Safe Removal of old_memory Directory
The `core/old_memory` directory can be safely deleted after making these 2 import updates:

**File: `core/memory/estia_memory_v5.py` (Line 173)**
```python
# Change from:
from ..old_memory.association.network import AssociationNetwork
# To:
from .managers.async_flow.association.network import AssociationNetwork
```

**File: `core/memory/estia_memory_v6.py` (Lines 205, 220)**
```python
# Change from:
from ..old_memory.association.network import AssociationNetwork
from ..old_memory.context.context_manager import ContextLengthManager
# To:
from .managers.async_flow.association.network import AssociationNetwork
from .managers.sync_flow.context.context_manager import ContextLengthManager
```

After making these changes, test the system with `python test_14_step_workflow.py` to ensure everything works correctly, then safely delete the `core/old_memory` directory.

### Debug Commands
```bash
# Complete system validation (recommended)
python test_14_step_workflow.py

# Check system status (simple)
python -c "
from core.memory import create_estia_memory
memory_system = create_estia_memory(enable_advanced=True)
if memory_system.initialized:
    print('✅ System operational')
    print(f'Performance: {memory_system.get_system_stats()}')
else:
    print('❌ System initialization failed')
"

# Performance benchmarking
python tests/test_cache_performance.py

# Cache system analysis
python tests/test_cache_system_analysis.py

# Environment validation
python setup/check_env.py
```

## Development Scripts and Utilities

### Maintenance Scripts
```bash
# Clean project cache and temporary files
cd setup && clean_project.bat

# Migration and fix scripts (in scripts/ directory)
python scripts/migrate_old_system.py          # Migrate from old memory system
python scripts/monitor_data_consistency.py    # Check data consistency
python scripts/fix_cache_final_issues.py      # Fix cache-related issues
```