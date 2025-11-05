# ABM Policy Simulation

Agent-Based Model (ABM) for simulating the effects of social policy interventions on youth employment outcomes.

## Overview

This simulation models interactions between **NEETs** (Not in Education, Employment, or Training) and **Businesses**, testing the effectiveness of two primary policy interventions:

1. **Counseling Services** - Reduce barriers and increase motivation
2. **Wage Subsidies** - Incentivize business hiring

The model implements **Level 1 LLM Integration**: LLM-powered profile generation for realistic agent diversity, with rule-based decision-making during simulation.

## 🌐 Web Interface

**Try the live interactive demo**: [Youth Employment Policy Simulator](https://[your-app-name].streamlit.app) *(coming soon)*

The Streamlit web interface provides:
- 🎛️ **Interactive controls** - Adjust policies with sliders and dropdowns
- 📊 **Real-time visualization** - See results with charts and metrics
- 💡 **Plain language explanations** - No technical jargon
- 📥 **Download results** - Export data and reports
- 🚀 **No installation needed** - Runs in your browser

Perfect for policy makers, practitioners, and anyone interested in exploring policy interventions!

## Features

- ✅ **Expandable Architecture** - Easy to add new agent types (unemployment services, training providers, etc.)
- ✅ **LLM Integration** - Optional LLM-powered profile generation (OpenAI, Anthropic, or mock)
- ✅ **Policy Scenarios** - Pre-configured 2×2 matrix of counseling × subsidy levels
- ✅ **Batch Execution** - Run 30-100 simulations per scenario for statistical analysis
- ✅ **Configuration-Driven** - YAML-based configuration for easy experimentation
- ✅ **Metrics & Reporting** - Comprehensive tracking of employment outcomes

## Installation

### Option 1: GitHub Codespaces (Recommended for Quick Start)

The easiest way to try the simulation without any local setup:

1. **Create Codespace**
   - On the GitHub repository page, click the green **"Code"** button
   - Select the **"Codespaces"** tab
   - Click **"Create codespace on [branch-name]"**

2. **Install Dependencies** (in Codespace terminal)
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Your First Simulation**
   ```bash
   # Quick test (takes ~10 seconds)
   python scripts/run_single_simulation.py --random-seed 42
   ```

✅ **No API keys needed** - Mock LLM works out of the box
✅ **Pre-configured** - All paths and configs work as-is
✅ **Fast** - Simulations run in seconds

### Option 2: Local Installation

```bash
# Clone or navigate to the repository
cd ABM_policy_simulation

# Install dependencies
pip install -r requirements.txt

# Optional: Install LLM packages if using real APIs
pip install openai anthropic
```

## Quick Start

### Run the Web Interface (Recommended)

```bash
# Install dependencies
pip install -r requirements.txt

# Start the Streamlit app
streamlit run streamlit_app.py
```

The app will open in your browser at `http://localhost:8501`

**Features:**
- Interactive sliders for all policy parameters
- Real-time results with charts
- Download data and reports
- No coding required!

### Run Command-Line Simulations

```bash
# Basic run with mock LLM (no API costs)
python scripts/run_single_simulation.py

# Run a specific scenario
python scripts/run_single_simulation.py --scenario low_counseling_low_subsidy

# Use real LLM (requires API key)
export OPENAI_API_KEY="your-key-here"
python scripts/run_single_simulation.py --llm-provider openai
```

### Run Multiple Simulations (Batch)

```bash
# Run 30 simulations for statistical analysis
python scripts/run_scenario_batch.py --scenario high_counseling_high_subsidy --num-runs 30

# Compare all scenarios
python scripts/run_scenario_batch.py --scenario low_counseling_low_subsidy --num-runs 30
python scripts/run_scenario_batch.py --scenario high_counseling_high_subsidy --num-runs 30
python scripts/run_scenario_batch.py --scenario low_counseling_high_subsidy --num-runs 30
python scripts/run_scenario_batch.py --scenario high_counseling_low_subsidy --num-runs 30
```

## Project Structure

```
ABM_policy_simulation/
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── base_agent.py    # Abstract base class
│   │   ├── neet_agent.py    # NEET agent
│   │   ├── business_agent.py # Business agent
│   │   └── agent_factory.py # Factory pattern for extensibility
│   │
│   ├── llm/                 # LLM integration (Level 1)
│   │   ├── llm_client.py    # Multi-provider LLM client
│   │   └── profile_generator.py # Profile generation
│   │
│   ├── matching/            # Job matching logic
│   │   ├── constraints.py   # Hard floor rules
│   │   └── hiring_decision.py # Probability calculations
│   │
│   ├── simulation/          # Core simulation engine
│   │   └── simulation_engine.py # Monthly loop implementation
│   │
│   ├── metrics/             # Metrics collection
│   │   └── metric_collector.py # Reporting and aggregation
│   │
│   └── utils/               # Utilities
│       └── config_loader.py # YAML configuration
│
├── config/                  # Configuration files
│   ├── base_config.yaml     # Default parameters
│   └── scenarios/           # Pre-defined scenarios
│       ├── low_counseling_low_subsidy.yaml
│       ├── high_counseling_high_subsidy.yaml
│       ├── low_counseling_high_subsidy.yaml
│       └── high_counseling_low_subsidy.yaml
│
├── scripts/                 # Executable scripts
│   ├── run_single_simulation.py
│   └── run_scenario_batch.py
│
├── data/
│   └── output/              # Simulation results (CSV, JSON)
│
├── docs/                    # Documentation
│   └── ABM_Intervention_Model_Guide.md # Full specification
│
└── requirements.txt
```

## Configuration

Edit `config/base_config.yaml` to change simulation parameters:

```yaml
simulation:
  duration_months: 12

agents:
  neets:
    count: 10
  businesses:
    count: 5

policies:
  counseling:
    budget_monthly: 50000
    intensity: 0.12

  subsidy:
    available: true
    effectiveness: 0.5

llm:
  enabled: true
  provider: "mock"  # or "openai", "anthropic"
```

## LLM Integration

### Level 1: Initialization Only (Recommended)

Agents are initialized with LLM-generated profiles for realism, then run with rule-based decisions:

```python
# Using mock LLM (no API costs, fast)
llm_client = LLMClient(provider='mock')

# Using real LLM (realistic diversity)
llm_client = LLMClient(provider='openai', api_key='...')
```

**Cost estimate**: ~$1-5 for 100 agents with GPT-4

### Adding New Agent Types

The architecture is designed for easy expansion:

```python
# 1. Create new agent class
class UnemploymentServiceAgent(BaseAgent):
    def __init__(self, agent_id, budget, staff_capacity):
        super().__init__(agent_id, 'unemployment_service')
        self.budget = budget
        self.staff_capacity = staff_capacity

    def step(self, month, context):
        # Implement behavior
        pass

# 2. Register with factory
AgentFactory.register_agent_type('unemployment_service', UnemploymentServiceAgent)

# 3. Add to config
# agents:
#   unemployment_services:
#     count: 2
```

## Key Metrics

The simulation tracks:

- **Employment Rate**: % of NEETs employed
- **Placements**: New hires per month
- **Attribute Changes**: How NEETs' skills, motivation, and barriers evolve
- **Cost Effectiveness**: Outcomes per euro spent
- **Outcome Distribution**: Very Poor / Poor / Base / Good / Very Good

## Results

Results are saved to `data/output/`:

- `{scenario}_run{N}_monthly.csv` - Month-by-month metrics
- `{scenario}_run{N}_report.json` - Final summary
- `{scenario}_aggregated.json` - Statistics across all runs

### Viewing Results in Codespaces

```bash
# List output files
ls data/output/

# View monthly metrics
cat data/output/base_run42_monthly.csv

# View final report (formatted JSON)
cat data/output/base_run42_report.json | python -m json.tool

# Quick comparison of multiple runs
grep "employment_rate" data/output/*.csv
```

### Experimenting with Scenarios in Codespaces

```bash
# Edit existing scenario
nano config/scenarios/low_counseling_low_subsidy.yaml

# Or create your own
cp config/scenarios/low_counseling_low_subsidy.yaml config/scenarios/my_custom_scenario.yaml
nano config/scenarios/my_custom_scenario.yaml

# Run your custom scenario
python scripts/run_single_simulation.py --scenario my_custom_scenario

# Run batch for statistical analysis (5 runs is good for testing)
python scripts/run_scenario_batch.py --scenario my_custom_scenario --num-runs 5
```

### Using Real LLMs in Codespaces

```bash
# Set API key as environment variable
export OPENAI_API_KEY="your-key-here"

# Run with OpenAI
python scripts/run_single_simulation.py --llm-provider openai

# Or with Anthropic
export ANTHROPIC_API_KEY="your-key-here"
python scripts/run_single_simulation.py --llm-provider anthropic
```

**Note**: Mock LLM is recommended for testing - it's free, fast, and produces realistic results!

## Extending the Model

### Add New Policy Interventions

1. Create policy module in `src/policies/`
2. Add configuration in YAML
3. Integrate into simulation engine

### Add New Matching Algorithms

1. Implement in `src/matching/`
2. Use factory pattern to swap algorithms

### Add Agent Interactions

1. Define interaction rules in config
2. Use interaction manager pattern

## Testing

```bash
# Run tests (if implemented)
pytest tests/

# Quick validation
python scripts/run_single_simulation.py --random-seed 42
```

## References

- Full specification: `docs/ABM_Intervention_Model_Guide.md`
- Based on agent-based modeling best practices
- Implements Mesa-compatible agent structure

## License

MIT

## Contributing

To add new features:

1. Follow the existing architecture patterns
2. Use factory patterns for extensibility
3. Add configuration options to YAML
4. Document in docstrings

## Contact

For questions about this simulation, refer to the specification document or open an issue.
