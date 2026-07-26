from agent.loop import initiate_session, run
import litellm
import os

litellm.suppress_debug_info = True

os.environ["LITELLM_LOG"] = "ERROR"

if __name__ == "__main__":
    run(initiate_session())
