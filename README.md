# TELESTO

## Scale-Adaptive Intelligence for Biological Manufacturing

> **Learning how biological processes change as they scale — and deciding what to do next.**

TELESTO is a research project investigating **adaptive decision-making in biological manufacturing under changing process dynamics**.

Instead of asking only:

> **What action should the system take?**

TELESTO asks:

> **Does the system understand the current process well enough to act, or should it measure, experiment, wait, adapt, or escalate?**

The first research domain is **fed-batch microbial fermentation**.

---

# Research Question

> **Can an uncertainty-aware decision system adapt a learned fermentation policy across scale and operating-regime shifts while learning when additional information is worth acquiring?**

---

# Research Architecture

```mermaid
flowchart TB

    A["Fed-Batch Fermentation<br/>Process / Digital Twin"]
    B["Observations"]
    C["State Estimation"]
    D["Regime Detection"]
    E["Uncertainty Estimation"]

    M["Experience Memory"]
    K["Process Knowledge"]
    L["LLM Knowledge Interface"]

    P["TELESTO Decision Engine"]
    V["Value of Information"]
    X["Counterfactual Evaluation"]

    Ctl["CONTROL"]
    Meas["MEASURE"]
    Exp["EXPERIMENT"]
    Wait["WAIT"]
    Esc["ESCALATE"]

    S["Constraints + Safety Gate"]
    O["Execute / Human Approval"]
    R["Observed Outcome"]
    E2["Expected vs Actual"]
    U["Learn + Update"]

    A --> B
    B --> C
    C --> D
    C --> E

    M --> P
    K --> P
    L --> K
    D --> P
    E --> P

    P --> V
    P --> X
    A --> X

    P --> Ctl
    P --> Meas
    P --> Exp
    P --> Wait
    P --> Esc

    Ctl --> S
    Meas --> S
    Exp --> S
    Wait --> S
    Esc --> S

    S --> O
    O --> A
    A --> R
    R --> E2

    E2 --> M
    E2 --> U

    U --> C
    U --> P
```

## Core Decision Loop

```mermaid
flowchart TD

    A["PROCESS"]
    B["OBSERVE"]
    C["STATE + REGIME + UNCERTAINTY"]
    D["MEMORY + PROCESS KNOWLEDGE"]
    E["TELESTO DECISION ENGINE"]

    F{"WHAT SHOULD HAPPEN NEXT?"}

    G["CONTROL"]
    H["MEASURE"]
    I["EXPERIMENT"]
    J["WAIT"]
    K["ESCALATE"]

    L["CONSTRAINTS + SAFETY"]
    M["EXECUTE / HUMAN APPROVAL"]
    N["OBSERVED OUTCOME"]
    O["EXPECTED vs ACTUAL"]
    P["LEARN + REMEMBER"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F

    F --> G
    F --> H
    F --> I
    F --> J
    F --> K

    G --> L
    H --> L
    I --> L
    J --> L
    K --> L

    L --> M
    M --> N
    N --> O
    O --> P

    P --> C
    P --> E
```

---

# Current Status

| Phase | Status |
|---|---|
| Research Definition | ✅ Complete |
| Fermentation Digital Twin | 🚧 **Current** |
| Control Baselines | Planned |
| Scale / Regime Shift | Planned |
| Uncertainty + Regime Detection | Planned |
| Adaptive Decision Policy | Planned |
| Information as an Action | Planned |
| Counterfactual Evaluation | Planned |
| Experience Memory | Planned |
| Process Knowledge + LLM | Planned |
| Full TELESTO | Planned |
| Ablation + Robustness Studies | Planned |

> **Current principle: environment before intelligence.**

We are **not** starting with RL or an LLM.  
The first task is to build and validate the fermentation environment.

---

# Phase 1 — Fermentation Digital Twin

The initial process domain is **fed-batch microbial fermentation**.

The first implementation will use **IndPenSim / PenSimPy** as the fermentation research testbed behind a TELESTO-owned process interface.

```mermaid
flowchart LR

    A["IndPenSim / PenSimPy"]
    B["Process Adapter"]
    C["TELESTO Fermentation Environment"]

    D["State"]
    E["Observation"]
    F["Action"]
    G["Process Transition"]
    H["Outcome"]

    A --> B
    B --> C

    C --> D
    C --> E
    C --> F

    F --> G
    G --> H
    H --> C
```

The simulator is the **process world**.  
TELESTO will provide the abstraction used by future control, learning, and decision-making components.

---

# Fermentation Environment

The initial environment will expose four fundamental concepts:

### State

Potential internal process variables include:

- biomass
- substrate
- product
- dissolved oxygen
- temperature
- pH
- volume
- relevant kinetic/process variables
- equipment-dependent parameters

### Observations

The decision system receives defined process measurements rather than unrestricted access to the complete hidden state.

Potential measurements include:

- temperature
- pH
- dissolved oxygen
- volume
- feed
- aeration
- agitation

Observation noise, sampling frequency, and measurement delay can later be introduced as controlled experimental variables.

### Actions

The initial action space will remain deliberately small and focus on meaningful controllable process inputs such as:

- feed
- aeration
- agitation

### Outcome

Each environment step produces the resulting process trajectory, objective metrics, and constraint information.

---

# Fermentation Environment Architecture

```mermaid
flowchart TB

    A["FERMENTATION PROCESS"]

    B["HIDDEN PROCESS STATE"]
    C["OBSERVATION MODEL"]
    D["ACTION INTERFACE"]
    E["PROCESS DYNAMICS"]
    F["OUTCOME"]

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    E --> B

    B --> S
    C --> O
    D --> AC

    subgraph S["STATE"]
        S1["Biomass"]
        S2["Substrate"]
        S3["Product"]
        S4["Dissolved Oxygen"]
        S5["Temperature"]
        S6["pH"]
        S7["Volume"]
        S8["Kinetic / Process Variables"]
        S9["Equipment Parameters"]
    end

    subgraph O["OBSERVATIONS"]
        O1["Measured Variables"]
        O2["Sensor Noise"]
        O3["Measurement Delay"]
        O4["Sampling Frequency"]
    end

    subgraph AC["ACTIONS"]
        A1["Feed"]
        A2["Aeration"]
        A3["Agitation"]
    end
```

---

# Phase 1 Deliverables

The first milestone is complete only when the environment can reliably support controlled experiments.

```mermaid
flowchart TB

    A["Simulator Running"]
    B["Process Adapter"]
    C["Fermentation Environment"]
    D["State Interface"]
    E["Observation Interface"]
    F["Action Interface"]
    G["Defined Process Timestep"]
    H["Complete Batch Simulation"]
    I["Trajectory Visualization"]
    J["Reproducibility Checks"]
    K["Validation Tests"]
    L["Initial Process Constraints"]

    A --> B
    B --> C
    C --> D
    C --> E
    C --> F
    C --> G
    G --> H
    H --> I
    I --> J
    J --> K
    K --> L
```

---

# Research Roadmap

```mermaid
flowchart LR

    A["01<br/>FERMENTATION DIGITAL TWIN"]
    B["02<br/>CONTROL BASELINES"]
    C["03<br/>SCALE / REGIME SHIFT"]
    D["04<br/>UNCERTAINTY + REGIME DETECTION"]
    E["05<br/>ADAPTIVE DECISION POLICY"]
    F["06<br/>INFORMATION AS AN ACTION"]
    G["07<br/>COUNTERFACTUAL EVALUATION"]
    H["08<br/>EXPERIENCE MEMORY"]
    I["09<br/>PROCESS KNOWLEDGE + LLM"]
    J["10<br/>FULL TELESTO"]
    K["11<br/>ABLATION + ROBUSTNESS"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J --> K
```

---

# Scale and Operating-Regime Shift

Once the baseline process and controllers are established, TELESTO will deliberately introduce changes to the process dynamics.

Potential shifts include:

- scale
- equipment characteristics
- mixing behaviour
- oxygen-transfer behaviour
- process delays
- sensor characteristics
- kinetic parameters
- disturbance distributions

```mermaid
flowchart LR

    A["SOURCE ENVIRONMENT"]
    B["LEARNED POLICY"]

    C["SCALE SHIFT"]
    D["EQUIPMENT SHIFT"]
    E["OPERATING-REGIME SHIFT"]
    F["DISTURBANCE SHIFT"]
    G["OBSERVATION SHIFT"]

    H["TARGET ENVIRONMENT"]
    I["PERFORMANCE DEGRADATION"]
    J["ADAPTIVE RECOVERY"]

    A --> B
    B --> H

    H --> C
    H --> D
    H --> E
    H --> F
    H --> G

    C --> I
    D --> I
    E --> I
    F --> I
    G --> I

    I --> J
```

The project will distinguish between **virtual experimental scale changes** and physically validated industrial scale-up.

---

# Uncertainty and Regime Detection

The system must eventually recognize when it is operating outside familiar conditions.

```mermaid
flowchart TD

    A["CURRENT OBSERVATIONS"]
    B["STATE REPRESENTATION"]

    C["REGIME DETECTION"]
    D["UNCERTAINTY ESTIMATION"]

    E{"CURRENT CONDITION"}

    F["FAMILIAR"]
    G["UNCERTAIN"]
    H["SHIFTED"]
    I["INSUFFICIENTLY UNDERSTOOD"]

    J["NORMAL CONTROL"]
    K["MEASURE / CONSERVATIVE DECISION"]
    L["ESCALATE / ACQUIRE INFORMATION"]

    A --> B
    B --> C
    B --> D

    C --> E
    D --> E

    E --> F
    E --> G
    E --> H
    E --> I

    F --> J
    G --> K
    H --> K
    I --> L
```

The objective is not merely to calculate uncertainty.

> **Uncertainty must change behaviour.**

---

# Information as an Action

One of TELESTO's central ideas is that **information acquisition can itself be a decision**.

The system may eventually choose between:

- acting immediately
- measuring first
- running an experiment

```mermaid
flowchart TD

    A["UNCERTAIN PROCESS STATE"]

    B["ACT NOW"]
    C["MEASURE FIRST"]
    D["RUN EXPERIMENT"]

    E["IMMEDIATE UTILITY"]
    F["REDUCED UNCERTAINTY"]
    G["FUTURE DECISION IMPROVEMENT"]

    H["INFORMATION COST"]
    I["RISK"]

    J["DECISION VALUE"]
    K["SELECTED DECISION"]

    A --> B
    A --> C
    A --> D

    B --> E
    C --> F
    D --> F

    F --> G

    E --> J
    G --> J
    H --> J
    I --> J

    J --> K
```

The research goal is to study the trade-off between **decision utility, information value, information cost, and risk**.

---

# Experience Memory

Important decisions should produce reusable experience.

```mermaid
flowchart TD

    A["PROCESS CONTEXT"]
    B["OBSERVED STATE"]
    C["DETECTED REGIME"]
    D["UNCERTAINTY"]
    E["CANDIDATE DECISIONS"]
    F["SELECTED DECISION"]
    G["EXPECTED OUTCOME"]
    H["ACTUAL OUTCOME"]
    I["PREDICTION ERROR"]
    J["LESSON"]

    K["EXPERIENCE MEMORY"]

    L["NEW SITUATION"]
    M["RETRIEVE RELATED EXPERIENCE"]
    N["ASSESS APPLICABILITY"]
    O["INFLUENCE CURRENT DECISION"]

    A --> B --> C --> D --> E --> F --> G --> H --> I --> J
    J --> K

    L --> M
    K --> M
    M --> N --> O
```

The research question is:

> **Does retrieving previous experience measurably improve later decisions?**

---

# Counterfactual Decision-Making

The digital twin will eventually be used to evaluate possible futures before important decisions are executed.

```mermaid
flowchart TD

    A["CURRENT PROCESS STATE"]

    B["CANDIDATE ACTION A"]
    C["CANDIDATE ACTION B"]
    D["CANDIDATE ACTION C"]

    E["DIGITAL TWIN"]
    F["COUNTERFACTUAL SIMULATION"]

    G["EXPECTED OUTCOME"]
    H["UNCERTAINTY"]
    I["COST"]
    J["RISK"]

    K["DECISION ENGINE"]
    L["SELECTED ACTION"]

    A --> B
    A --> C
    A --> D

    B --> F
    C --> F
    D --> F
    E --> F

    F --> G
    F --> H

    G --> K
    H --> K
    I --> K
    J --> K

    K --> L
```

---

# Process Knowledge and LLM

The LLM enters as a **knowledge interface**, not an unrestricted controller.

It can eventually interpret:

- SOPs
- batch documentation
- operator notes
- engineering guidance
- experimental records

```mermaid
flowchart TB

    A["SOPs"]
    B["BATCH DOCUMENTATION"]
    C["OPERATOR NOTES"]
    D["ENGINEERING GUIDANCE"]
    E["EXPERIMENTAL RECORDS"]

    F["LLM KNOWLEDGE INTERFACE"]
    G["STRUCTURED PROCESS KNOWLEDGE"]
    H["TELESTO DECISION SYSTEM"]
    I["CONSTRAINTS + SAFETY"]
    J["APPROVED ACTION"]

    A --> F
    B --> F
    C --> F
    D --> F
    E --> F

    F --> G
    G --> H
    H --> I
    I --> J
```

The LLM does **not** receive unrestricted actuator authority.

---

# Constraints and Safety

Every eventual autonomous decision must pass through a dedicated safety layer.

```mermaid
flowchart TD

    A["CANDIDATE DECISION"]
    B["FEASIBILITY CHECK"]
    C["HARD PROCESS CONSTRAINTS"]
    D["RISK ASSESSMENT"]

    E{"ALLOWED?"}

    F["REJECT"]
    G["EXECUTE"]
    H["HUMAN APPROVAL"]

    A --> B --> C --> D --> E

    E -->|"NO"| F
    E -->|"YES"| G
    E -->|"REVIEW REQUIRED"| H
```

---

# Evaluation

The final system will be evaluated against strong baselines.

Key evaluation dimensions:

- **Decision quality**
- **Robustness under distribution shift**
- **Adaptation speed**
- **Sample efficiency**
- **Information efficiency**
- **Uncertainty calibration**
- **Constraint adherence**
- **Transfer to unseen conditions**

Each major component will be subjected to controlled ablations.

The goal is not to demonstrate architectural complexity.

> **Every component must produce measurable research value.**

---

# Final TELESTO Workflow

```mermaid
flowchart TB

    A["BIOLOGICAL PROCESS / DIGITAL TWIN"]

    B["OBSERVE"]
    C["STATE ESTIMATION"]
    D["REGIME DETECTION"]
    E["UNCERTAINTY ESTIMATION"]

    F["EXPERIENCE MEMORY"]
    G["PROCESS KNOWLEDGE"]

    H["TELESTO DECISION ENGINE"]

    I["VALUE OF INFORMATION"]
    J["COUNTERFACTUAL EVALUATION"]

    K["CONTROL"]
    L["MEASURE"]
    M["EXPERIMENT"]
    N["WAIT"]
    O["ESCALATE"]

    P["CONSTRAINTS + SAFETY GATE"]
    Q["EXECUTE / HUMAN APPROVAL"]

    R["OBSERVED OUTCOME"]
    S["EXPECTED vs ACTUAL"]
    T["LEARN + UPDATE"]

    A --> B
    B --> C
    C --> D
    C --> E

    D --> H
    E --> H
    F --> H
    G --> H

    H --> I
    H --> J
    A --> J

    H --> K
    H --> L
    H --> M
    H --> N
    H --> O

    K --> P
    L --> P
    M --> P
    N --> P
    O --> P

    P --> Q
    Q --> A

    A --> R
    R --> S
    S --> T

    T --> F
    T --> C
    T --> E
    T --> H
```

---

# Repository Structure

```text
TELESTO/
├── apps/
├── biocontrolos/
│   └── environment/
│       ├── process_adapter.py
│       └── fermentation_env.py
├── configs/
├── data/
├── docs/
├── experiments/
├── scripts/
├── tests/
├── pyproject.toml
└── README.md
```

`biocontrolos/` is retained as the implementation namespace while the research project evolves under the **TELESTO** identity.

---

# Design Principles

- **Environment before intelligence**
- **Evidence before complexity**
- **Uncertainty must influence decisions**
- **Information can be an action**
- **Memory must change future behaviour**
- **LLMs remain bounded by process knowledge and safety**
- **Every major claim must be experimentally reproducible**

---

## TELESTO

**Scale-Adaptive Intelligence for Biological Manufacturing**

> **Don't just optimize the process. Learn the process.**