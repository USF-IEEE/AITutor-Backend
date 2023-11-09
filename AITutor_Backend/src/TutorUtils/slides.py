from typing import List, Tuple, Union
import re
from enum import IntEnum
from AITutor_Backend.src.BackendUtils.json_serialize import *
from AITutor_Backend.src.TutorUtils.concepts import *
import yaml

class SlidePlanner(JSONSerializable):
    """
    Map {Slides -> List[Concept]}
    Planner [i] returns a slide
    resettable, indexable, interactable
    """
    class Slide(JSONSerializable):
        def __init__(self, title:str, content:str, latex_render:List[str]):
            super().__init__()
            self.__title, self.__content, self.__latex_render = title, content, latex_render
            
    