from .schema import PreProcessorOutput

def override_intent_if_low_confidence(output: PreProcessorOutput) -> PreProcessorOutput:
    if output.confidence < 0.55 and output.intent != "chit_chat":
        output.intent = "chit_chat"
    return output
