import os
import replicate
# from langchain.llms import Replicate


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

class ReplicateAPI:
    def __init__(self,):
        pass
    def get_output(self, system_prompt, instruction):
        output = replicate.run("meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
        input={
            "debug": False,
            "top_k": 25,
            "top_p": 1,
            "prompt": instruction,
            "temperature": 0.8,
            "system_prompt": system_prompt,
            "max_new_tokens": 1000,
            "min_new_tokens": -1
        }
        )
        return output

