import structlog

logger = structlog.get_logger()

class PromptComposer:
    def __init__(self, system_prompt: str = "You are HYPER, a production-grade AI assistant. Use the following context to answer the query."):
        self.system_prompt = system_prompt

    def compose(self, query: str, context: str) -> str:
        """
        Builds a structured prompt for LLM consumption.
        """
        logger.info("composing_prompt", query_length=len(query), context_length=len(context))
        
        prompt = f"""<|system|>
{self.system_prompt}
<|context|>
{context}
<|user|>
{query}
<|assistant|>
"""
        return prompt

if __name__ == "__main__":
    composer = PromptComposer()
    print(composer.compose("How is HYPER built?", "HYPER uses CPU-first principles."))
