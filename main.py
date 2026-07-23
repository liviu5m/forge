from agent.loop import run
import litellm
import os

litellm.suppress_debug_info = True

os.environ["LITELLM_LOG"] = "ERROR"
run()
