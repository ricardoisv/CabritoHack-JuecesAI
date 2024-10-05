import nest_asyncio
nest_asyncio.apply()

from getpass import getpass
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Access environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")
# https://developers.google.com/custom-search/v1/overview
google_api_key=os.getenv("GOOGLE_API_KEY")
# https://cse.google.com/cse/all
search_engine_id = os.getenv("SEARCH_ENGINE_ID")


import textwrap
from camel.agents import ChatAgent
from camel.configs import ChatGPTConfig
from camel.messages import BaseMessage
from camel.models import ModelFactory
from camel.tasks import Task
from camel.toolkits import OpenAIFunction, SearchToolkit
from camel.types import ModelPlatformType, ModelType
from camel.workforce import Workforce

def make_judge(
    persona: str,
    example_feedback: str,
    criteria: str,
) -> ChatAgent:
    msg_content = textwrap.dedent(
        f"""\
        You are a judge in a hackathon.
        This is your persona that you MUST act with: {persona}
        Here is an example feedback that you might give with your persona, you MUST try your best to align with this:
        {example_feedback}
        When evaluating projects, you must use the following criteria:
        {criteria}
        You also need to give scores based on these criteria, from 1-4. The score given should be like 3/4, 2/4, etc.
        """
    )

    sys_msg = BaseMessage.make_assistant_message(
        role_name="Hackathon Judge",
        content=msg_content,
    )

    model = ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=ModelType.GPT_4O_MINI,
        model_config_dict=ChatGPTConfig().as_dict(),
    )

    agent = ChatAgent(
        system_message=sys_msg,
        model=model,
    )

    return agent

# Create helper agent
search_toolkit = SearchToolkit()
search_tools = [
    OpenAIFunction(search_toolkit.search_google),
]

researcher_model = ModelFactory.create(
    model_platform=ModelPlatformType.OPENAI,
    model_type=ModelType.GPT_4O_MINI,
    model_config_dict=ChatGPTConfig().as_dict(),
)

researcher_agent = ChatAgent(
    system_message=BaseMessage.make_assistant_message(
        role_name="Researcher",
        content="You are a researcher who does research on AI and Open"
                "Sourced projects. You use web search to stay updated on the "
                "latest innovations and trends.",
    ),
    model=researcher_model,
    tools=search_tools,
)

# 1. Venture Capitalist - El-VC
vc_persona = """
You are El-VC, a venture capitalist who is obsessed with how projects can 
be scaled into "unicorn" companies. You pepper your speech with 
buzzwords like "disruptive," "synergistic," and "market penetration."
You are primarily concerned with the business potential and scalability of projects.
"""

vc_example_feedback = """
Wow, this project is absolutely disruptive in the AgriTech marketplace! I can definitely 
see synergistic applications across various sectors. The scalability potential is 
through the roof--this could be the next unicorn in sustainable technology!
"""

vc_criteria = textwrap.dedent(
    """\
    ### **Business Potential and Scalability (1-4 points)**
    - **4**: The project has clear potential to become a unicorn with a highly scalable business model.
    - **3**: Good business potential with some scalability, but may face challenges in rapid growth.
    - **2**: Limited scalability or unclear business model that needs significant refinement.
    - **1**: Poor business potential with major obstacles to scalability.
    """
)

vc_agent = make_judge(vc_persona, vc_example_feedback, vc_criteria)

# 2. Programmer - TopFounder
programmer_persona = """
You are TopFounder, an experienced programmer and tech entrepreneur. You have a keen eye 
for technical implementation and innovation. You value clean code, scalable architecture, 
and cutting-edge technologies. Your feedback focuses on the technical aspects and 
feasibility of projects.
"""

programmer_example_feedback = """
The integration of machine learning algorithms with IoT sensors shows promising 
technical innovation. However, I have concerns about the scalability of the data 
processing pipeline. The use of containerization is a plus, but I'd like to see more 
details on how they're handling real-time data streams at scale.
"""

programmer_criteria = textwrap.dedent(
    """\
    ### **Technical Innovation and Implementation (1-4 points)**
    - **4**: Cutting-edge technology with flawless implementation and clear scalability.
    - **3**: Solid technical foundation with some innovative elements, minor improvements needed.
    - **2**: Basic implementation with limited innovation, significant optimizations required.
    - **1**: Poor technical implementation or lack of innovation.
    """
)

programmer_agent = make_judge(programmer_persona, programmer_example_feedback, programmer_criteria)

# 3. Business Writer - Startupera
writer_persona = """
You are Startupera, an accomplished business writer with a knack for identifying compelling 
narratives in startup projects. You focus on how well the project is communicated, its 
potential impact on the market, and how it addresses real-world problems. Your feedback 
often includes suggestions for refining the project's story and pitch.
"""

writer_example_feedback = """
The project presents a compelling narrative in the sustainable agriculture space. 
The team articulates the problem and solution clearly, but I believe they could 
strengthen their impact story by providing more concrete examples of how their 
technology affects individual farmers. The market positioning is strong, but the 
competitive analysis could be more comprehensive.
"""

writer_criteria = textwrap.dedent(
    """\
    ### **Communication and Market Positioning (1-4 points)**
    - **4**: Exceptional communication of the project with a clear, compelling narrative and strong market positioning.
    - **3**: Well-communicated idea with good market positioning, but some aspects could be refined.
    - **2**: Basic communication of the concept with unclear market positioning.
    - **1**: Poor communication of the project idea and lack of clear market positioning.
    """
)

writer_agent = make_judge(writer_persona, writer_example_feedback, writer_criteria)

# 4. Growth Expert - El GrowthGuy
growth_persona = """
You are El GrowthGuy, a growth hacking expert with a track record of scaling startups. 
You focus on user acquisition strategies, viral potential, and long-term growth 
opportunities. Your feedback often includes suggestions for growth strategies and 
potential pivots to maximize market penetration.
"""

growth_example_feedback = """
This project has solid viral potential within the agricultural community. The 
real-time data sharing feature could be leveraged for rapid user acquisition. 
However, I see opportunities to enhance user retention through gamification of 
sustainable practices. Consider implementing a referral program to accelerate 
growth among farming communities.
"""

growth_criteria = textwrap.dedent(
    """\
    ### **Growth Potential and Strategy (1-4 points)**
    - **4**: Clear path to rapid growth with multiple viable user acquisition channels.
    - **3**: Good growth potential with some clear strategies, but may face scaling challenges.
    - **2**: Limited growth strategies with unclear user acquisition plans.
    - **1**: Poor growth potential with major obstacles to user acquisition and retention.
    """
)

growth_agent = make_judge(growth_persona, growth_example_feedback, growth_criteria)

# Create Workforce
workforce = Workforce('Hackathon Judges')

workforce.add_single_agent_worker(
    'El-VC (Judge), a venture capitalist focused on unicorn potential',
    worker=vc_agent,
).add_single_agent_worker(
    'TopFounder (Judge), an experienced programmer and tech entrepreneur',
    worker=programmer_agent,
).add_single_agent_worker(
    'Startupera (Judge), an accomplished business writer focused on market narratives',
    worker=writer_agent,
).add_single_agent_worker(
    'El GrowthGuy (Judge), a growth hacking expert specializing in scaling startups',
    worker=growth_agent,
).add_single_agent_worker(
    'Researcher Practicante (Helper), a researcher who does online searches to'
    'find the latest innovations and trends on AI and Open Sourced projects.',
    worker=researcher_agent,
)

def create_task(project_description: str) -> Task:
    return Task(
        content="Evaluate the hackathon project. First, do some research on "
                "the information related to the project, then each judge should give a"
                " score accordingly. Finally, list the opinions from each judge while"
                " preserving the judge's unique identity, along with the score and"
                " judge name, and also give a final summary of the opinions.",
        additional_info=project_description,
        id="0",
    )

def evaluate_project(project_description: str) -> str:
    task = create_task(project_description)
    result = workforce.process_task(task)
    
    full_conversation = "Project Evaluation Conversation:\n\n"
    
    if hasattr(result, 'task_steps'):
        for step in result.task_steps:
            full_conversation += f"Step: {step.step_id}\n"
            full_conversation += f"Worker: {step.worker_name}\n"
            full_conversation += f"Input: {step.input_msg.content}\n"
            full_conversation += f"Output: {step.output_msg.content}\n\n"
    else:
        full_conversation += "Detailed task steps are not available.\n\n"
    
    full_conversation += "Final Result:\n"
    full_conversation += result.result
    
    return full_conversation


def create_task(project_description: str) -> Task:
    return Task(
        content="Evaluate the hackathon project. First, do some research on "
                "the information related to the project, then each judge should give a"
                " score accordingly. Finally, list the opinions from each judge while"
                " preserving the judge's unique identity, along with the score and"
                " judge name, and also give a final summary of the opinions.",
        additional_info=project_description,
        id="0",
    )