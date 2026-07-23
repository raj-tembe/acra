from langgraph.graph import (
    StateGraph,
    START,
    END
)
import time

from langchain_core.callbacks import BaseCallbackHandler

from acra.graph.state import AgentState

from acra.graph.nodes import (
    NODE_REGISTRY
)

from acra.graph.conditional_edges import (
    register_conditional_edges
)

from acra.graph.checkpoint import GraphCheckpointManager
from acra.observability.metrics import metrics_tracker
from acra.observability.monitoring import system_monitor


class OmniAgentCallbacks(BaseCallbackHandler):
    """LangGraph callbacks for metrics and monitoring.

    Subclasses BaseCallbackHandler (rather than duck-typing a plain class)
    so every callback method LangChain might call -- including
    on_llm_new_token, which only fires once real token streaming is in use
    (see acra.ui.spinner.run_workflow_with_thoughts) -- has a safe no-op
    default unless explicitly overridden below. Without this base class,
    an unhandled callback raises AttributeError inside LangChain's
    callback manager for every single token, which it catches per-handler
    and logs rather than raising, but the run continues underneath a wall
    of "Error in OmniAgentCallbacks.on_llm_new_token callback" spam.
    """

    raise_error = False
    ignore_chain = False
    ignore_agent = False
    ignore_llm = False
    ignore_chat_model = False

    def on_chain_start(self, serialized, inputs, **kwargs):
        try:
            self._start = time.time()
            agent = (serialized or {}).get("name", "unknown") if isinstance(serialized, dict) else "unknown"
            system_monitor.info(agent, f"Agent started: {agent}")
            metrics_tracker.record_agent_execution(agent)
        except Exception:
            return None

    def on_chain_end(self, outputs, **kwargs):
        try:
            elapsed = time.time() - getattr(self, "_start", time.time())
            system_monitor.info("workflow", f"Step completed in {elapsed:.2f}s")
        except Exception:
            return None

    def on_chain_error(self, error, **kwargs):
        try:
            system_monitor.error("workflow", str(error))
        except Exception:
            return None

    def on_chat_model_start(self, serialized, messages, **kwargs):
        return None

    def on_llm_end(self, response, **kwargs):
        return None

    def on_llm_error(self, error, **kwargs):
        return None


# Initialize checkpoint manager
graph_checkpoint = GraphCheckpointManager()


# create workflow graph

def create_workflow():
    """
    Build OMNIAGENT workflow graph.
    """

    workflow = StateGraph(
        AgentState
    )

    # register nodes

    for (
        node_name,
        node_function
    ) in NODE_REGISTRY.items():

        workflow.add_node(
            node_name,
            node_function
        )

    # entry point

    workflow.add_edge(
        START,
        "planner"
    )

    # conditional routing 

    workflow = (
        register_conditional_edges(
            workflow
        )
    )

    # compile graph with checkpointer

    graph = workflow.compile(
        checkpointer=graph_checkpoint.checkpointer
    )

    return graph


# singleton workflow instance

omniagent_graph = create_workflow()