# State Machine & DAG Engine
SARA V1.5 replaces linear task orchestration with the `DAGEngine`. Nodes explicitly track `dependencies`. 
The overall objective runs via `StateMachine` tracking explicit persistent bounds: `RECEIVED -> PLANNING -> READY -> DEPLOYING -> COMPLETED`.
