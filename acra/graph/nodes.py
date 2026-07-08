from acra.agents.planner.planner_agent import (
    planner_agent
)

from acra.agents.researcher.researcher_agent import (
    researcher_agent
)

from acra.agents.coder.coder_agent import (
    coder_agent
)

from acra.agents.executor.executor_agent import (
    executor_agent
)

from acra.agents.critic.critic_agent import (
    critic_agent
)

from acra.agents.memory.memory_agent import (
    memory_agent
)

from acra.agents.human.human_node import (
    human_node
)


# node registry

NODE_REGISTRY = {

    "planner": planner_agent,

    "researcher": researcher_agent,

    "coder": coder_agent,

    "executor": executor_agent,

    "critic": critic_agent,

    "memory": memory_agent,

    "human": human_node,
}


# get nodes 

def get_node(node_name: str):
    """
    Returns node function.
    """

    return NODE_REGISTRY.get(node_name)

# list nodes

def list_nodes():
    """
    Returns all available nodes.
    """

    return list(
        NODE_REGISTRY.keys()
    )