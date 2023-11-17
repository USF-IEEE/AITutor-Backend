import os
import replicate
# from langchain.llms import Replicate


B_INST, E_INST = "[INST]", "[/INST]"
B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"

class ReplicateAPI:
    def __init__(self,):
        pass
    def get_output(self, system_prompt, instruction):
        output = replicate.run("meta/codellama-34b:efbd2ef6feefb242f359030fa6fe08ce32bfced18f3868b2915db41d41251b46",
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
        return "".join(output)

