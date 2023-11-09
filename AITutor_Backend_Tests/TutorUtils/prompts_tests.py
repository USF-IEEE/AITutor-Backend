from AITutor_Backend.src.TutorUtils.notebank import *

def test_notebank_creation_and_modification():
    llm_output1 = """
    adksdfbjhafds adskj akjdnkasdj gibberihs
    ```TextPrompt
    Please detail further what piece of this subject is troubling you the most.
    ```
    qnd ajksbdsmfb askjbd lorem epsiu
    """
    
    llm_output2 = """
    adksdfbjhafds adskj akjdnkasdj gibberihs:
    [TERM]
    mfb askjbd lorem epsiu
    """
    
    llm_output3 = """
    adksdfbjhafds adskj akjdnkasdj gibberihs
    ```FilePrompt
    Please detail further what piece of this subject is troubling you the most.
    ```
    qnd ajksbdsmfb askjbd lorem epsiu
    """
    
    llm_output4 = """
    adksdfbjhafds adskj akjdnkasdj gibberihs
    ```RatingPrompt
    Please detail further what piece of this subject is troubling you the most.
    ```
    qnd ajksbdsmfb askjbd lorem epsiu
    """

    p1 = PromptAction.parse_llm_action(llm_output1)

    assert p1.format_json()["type"] == 1, "Error in parsing Text prompt."

    p2 = PromptAction.parse_llm_action(llm_output2)

    assert p2.format_json()["type"] == -1, "Error in parsing Termination prompt."
    
    p3 = PromptAction.parse_llm_action(llm_output3)

    assert p3.format_json()["type"] == 0, "Error in parsing File prompt."
    
    p4 = PromptAction.parse_llm_action(llm_output4)

    assert p4.format_json()["type"] == 2, "Error in parsing Rating prompt."

    # p3 = PromptAction.parse_llm_action("this is bad action.") # Assert.fail