from google.adk.agents import LlmAgent, SequentialAgent
from google.genai.types import GenerateContentConfig

# Instructions
OUTLINER_INSTRUCTION = """
You are an expert curriculum designer.
Your goal is to create a detailed outline for a course topic.
You will be provided with the Topic, Chapter, Subject, and Course Name.
Your output should be a structured outline that covers core concepts, key terms, principles, theories, historical context, and real-world relevance.
Do not write the full content, just the outline and structure that the writer should follow.
"""

WRITER_INSTRUCTION = """
You are an expert educational content writer.
Your goal is to write detailed, in-depth content based on the provided outline and topic details.
You must follow these requirements:
1. Delve deeply into core concepts, defining key terms, principles, and theories.
2. Include historical context and real-world relevance.
3. Provide diverse examples, including numerical examples with step-by-step explanations using equations, tables, or graphs.
4. **DIAGRAMS WITH MERMAID JS**: Include relevant diagrams using Mermaid JS syntax (flowchart, sequence, class, state, etc.) if they clarify the content. Wrap them in `<pre class="mermaid">` tags.
   Example:
   <pre class="mermaid">
   graph LR
   A --- B
   </pre>
5. **INTERACTIVE CHARTS WITH CHART.JS**: For statistical data or comparisons, use Chart.js JSON format wrapped in ````chart-json` blocks.
   Example:
   ```chart-json
   {
     "type": "bar",
     "data": { ... },
     "options": { ... }
   }
   ```
6. **Mathematical Formulas**: Use LaTeX format `$$...$$` for multiline equations and `$...$` for inline.
7. **Assignments**: Include at least 10 assignments or problems if applicable, with varying difficulty.
8. **Tables**: Use Markdown tables for comparisons or data summaries.
9. **Resources**: specific references to research papers, books, or reliable URLs for further reading.

Generate everything in Markdown.
"""

REVIEWER_INSTRUCTION = """
You are an expert editor and reviewer.
Review the provided content for clarity, accuracy, formatting, and adherence to the requirements.
Ensure Mermaid diagrams and Chart.js JSON blocks are correctly formatted.
Ensure LaTeX formulas are correct.
If the content is good, return it as is. If there are minor issues, fix them.
If there are major missing parts (like missing assignments or diagrams where needed), add them.
Your output should be the final polished Markdown content.
"""

def get_content_pipeline(model_name: str = "gemini-2.5-flash-lite"):
    """
    Creates and returns a SequentialAgent pipeline for content generation.
    """

    outliner = LlmAgent(
        name="Outliner",
        model=model_name,
        instruction=OUTLINER_INSTRUCTION
    )

    writer = LlmAgent(
        name="Writer",
        model=model_name,
        instruction=WRITER_INSTRUCTION
    )

    reviewer = LlmAgent(
        name="Reviewer",
        model=model_name,
        instruction=REVIEWER_INSTRUCTION
    )

    pipeline = SequentialAgent(
        name="ContentGenerationPipeline",
        description="A pipeline to outline, write, and review course content.",
        sub_agents=[outliner, writer, reviewer]
    )

    return pipeline
