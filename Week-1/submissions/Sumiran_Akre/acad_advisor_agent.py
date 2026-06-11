from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError, field_validator
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage, BaseMessage
import os
import json
from typing import List, Union, Optional, Dict, Any, Tuple, Callable

MAX_STEPS = 10
load_dotenv()
if not os.getenv("groq"):
    raise RuntimeError("GROQ_API_KEY is not set")
os.environ["GROQ_API_KEY"] = os.getenv("groq")

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, "btech_cse_courses.json"), "r") as f:
    data = json.load(f)

categories = [
    ("common_courses", "Institute Common Course"),
    ("non_graded_core_courses", "Non-Graded Core Course"),
    ("program_core_courses", "Program Core Course"),
    ("program_linked_courses", "Program Linked Course")
]

def normalize_code(code:str) -> str:
    """ Normalize the course code by removing spaces and hyphens and converting to lowercase. """
    return code.replace(" ", "").replace("-", "").lower()

class GetNameInput(BaseModel):
    course_code: str = Field(description="The course code")

    @field_validator("course_code")
    @classmethod
    def valid_course_code(cls, v):
        for type_of_course, labels in categories:
            for key in data.get(f"{type_of_course}", {}).get("courses", []):
                allowed_codes = [normalize_code(c) for c in key.get("code", "").split("/")]
                if normalize_code(v) in allowed_codes:
                    return v
        raise ValueError("Course code must be in the following: " + str([key.get("code","" ) for type_of_course, labels in categories for key in data.get(f"{type_of_course}", {}).get("courses", [])]))

class GetCourseInfoInput(BaseModel):
    course_name: str = Field(description="The course name or course code")

class KnowAboutPrerequisitesInput(BaseModel):
    course_name: str = Field(description="The course name or course code")

class GetToKnowASemesterInput(BaseModel):
    sem: int = Field(description="The semester number")

    @field_validator("sem")
    @classmethod
    def sem_must_be_valid(cls, v):
        if v not in [1,2,3,4,5,6,7,8]:
            raise ValueError("Semester number must be between 1 and 8")
        return v

def get_name_from_code(course_code:str) -> Optional[str]:
    """ Get the course name from the course code. """
    for type_of_course, labels in categories:
        for key in data.get(f"{type_of_course}", {}).get("courses", []):
            allowed_codes = [normalize_code(c) for c in key.get("code", "").split("/")]
            if normalize_code(course_code) in allowed_codes:
                return key.get("name","")
    return None
    
def find_course_details(course_name:str, cat:List[Tuple[str,str]] = categories) -> Union[Optional[str], Dict[str,str], Optional[str]]:
    """ Helper to locate a course in the dataset by its name or code. 
    Returns: (semester_info, course_metadata, category_name) """
    
    sem_info = None
    for sem_plan in data.get("semester_plan",[]):
        for course in sem_plan.get("courses",[]):
            allowed_codes = [normalize_code(c) for c in course.get("code", "").split("/")]
            if (normalize_code(course_name) in allowed_codes) or (course_name.lower() in course.get("name","",).lower()):
                sem_info = f"Course is in Semester {sem_plan['semester']}"
                break
        if sem_info:
            break
    
    course_info = {}
    category = None
    for type_of_course, labels in cat:
        for key in data.get(f"{type_of_course}", {}).get("courses", []):
            allowed_codes = [normalize_code(c) for c in key.get("code", "").split("/")]
            if (normalize_code(course_name) in allowed_codes) or (course_name.lower() in key.get("name","").lower()):
                course_info = key.copy()
                category = labels
                break
        if category:
            break
    return sem_info, course_info, category


def get_course_info(course_name: str) -> Optional[Dict[str, Any]]:
    """ Get full details for a course using a helper function. """
    semester_info, course_data, category = find_course_details(course_name)
    if not course_data:
        return {"error": "Course not found"}
    
    return {
        "semester": semester_info,
        "category": category,
        "details": course_data
    }

def know_about_prerequisites(course_name:str) -> str:
    """ Returns the course name, semester, and its prerequisites. """
    sem,course,category = find_course_details(course_name)
    if not course:
        return "Course not found"
    prerequisites = course.get("prerequisites",[])

    if category in ["Non-Graded Core Course", "Institute Common Course"]:
        return f"No pre-requisite required for {course.get('name')}, as it is a common course to all."
    if prerequisites:
        return f"You have to complete {', '.join(prerequisites)} before taking {course.get('name')}"
    return f"No pre-requisite required for {course.get('name')}"

def get_to_know_a_semester(sem: int) -> Optional[Dict[str, Any]]:
    """ Returns the entire course plan for a given semester number. """
    for sem_plan in data.get("semester_plan", []):
        if sem_plan.get("semester") == sem:
            return sem_plan
    return "Course not found"

# TOOL WRAPPER
class Tool:

    def __init__(self, name: str, description: str, input_model: type[BaseModel],func: Callable[..., str]):
        self.name = name
        self.description = description
        self.input_model = input_model
        self.func = func

    def run(self, raw_input: dict[str, Any]) -> str:

        try:
            validated = self.input_model(**raw_input)
            return self.func(**validated.model_dump())
        except ValidationError as e:
            return f"Validation Error:\n{e}"
        except Exception as e:
            return f"Tool Error: {e}"

    def to_groq_tool(self):

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": (
                    self.input_model
                    .model_json_schema()
                ),
            },
        }

TOOLS = [
    Tool(
        "get_name_from_code",
        "Get the course name from the course code. ",
        GetNameInput,
        get_name_from_code
        ),
    Tool(
        "get_course_info",
        "Get the course information from the course name or course code. ",
        GetCourseInfoInput,
        get_course_info
    ),
    Tool(
        "know_about_prerequisites",
        "Know about the prerequisites of a course using the course name or course code. ",
        KnowAboutPrerequisitesInput,
        know_about_prerequisites
    ),
    Tool(
        "get_to_know_a_semester",
        "Get to know about a semester. ",
        GetToKnowASemesterInput,
        get_to_know_a_semester
    )
]

TOOLS_MAP = {tool.name : tool for tool in TOOLS}

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0,
)

model_with_tools = llm.bind_tools([tool.to_groq_tool() for tool in TOOLS])

class AcadAgent:

    def __init__(self, messages:List[BaseMessage]):
        self.messages = messages
    
    def run( self, query: str) -> str:
        self.messages.append(HumanMessage(content=query))

        for _ in range(MAX_STEPS):
            response = model_with_tools.invoke(self.messages)
            self.messages.append(response)

            if not response.tool_calls:
                return str(response.content), self.messages

            for tool_called in response.tool_calls:
                tool_name = tool_called["name"]
                tool_args = tool_called["args"]
                print(f"\n[TOOL]: {tool_name}")
                print(f"[ARGS]: {tool_args}")
                tool = TOOLS_MAP.get(tool_name)
                if not tool:
                    result = (f"Unknown Tool: " f"{tool_name}")
                else:
                    result = tool.run(tool_args)
                print(f"[TOOL OUTPUT]: {result}")
                self.messages.append(ToolMessage(content=result,tool_call_id=tool_called["id"]))

        return (
            "Stopped after reaching "
            "MAX_STEPS."
        ), self.messages

# Test code examples
if __name__ == "__main__":
    # print(get_course_info("Biology for Engineers"))
    # print(know_about_prerequisites("Probability & Statistics"))
    # print(get_to_know_a_semester(1))
    # print(get_name_from_code("PHP102"))
    chat_history = [
        SystemMessage(content="""
        You are an expert Academic Advisor and Curriculum Assistant for the Computer Science and Engineering department.
        Your goal is to provide rich, comprehensive, and highly detailed guidance to student queries.

        CRITICAL GUIDELINES FOR RESPONSES:
        1. **Leverage Tools First**: When a query pertains to courses, codes, plans, or prerequisites, ALWAYS use the relevant tool(s) first to fetch the official curriculum facts.
        2. **Go Beyond Dry Database Facts**: Do not just copy-paste tool outputs. Instead, augment the official syllabus/details with your general academic knowledge. Explain the *significance* of the course, what core concepts mean, what technologies or practical applications are relevant, and how it fits into a student's learning journey.
        3. **Support and General Knowledge**: If the user asks for concepts, advice, or details beyond what is literally in the JSON database, use your general knowledge to explain it clearly (e.g., explain what compilers do, what books are recommended, or the career prospects of learning operating systems).
        4. **Handling Missing Data/Errors**: If a tool returns an error or indicates a course is "not found", do not just report the error. Explain that the course is not part of the department's standard curriculum plan, but then provide general information about what that course typically covers in standard Computer Science programs.
        5. **Code Conversion Rule**: If the user provides a course code, first convert it to a course name using the 'get_name_from_code' tool, then retrieve its info or prerequisites.
        6. **Formatting**: Present your answers in a professional, beautifully styled Markdown format. Use headers, bold text, lists, and spacing to make it extremely easy to read.

        PREPARATIONS BEFORE USING SOME TOOLS:
        - A Course Code contains of 6 letters, first three of it are Alphabets and rest three are the numbers.
        - Few Examples of COURSE CODE are : CSL351, PHP102, CSL203, MAL403, etc.
        - If you get a query like "What are the prerequisites for [course_code]", first check if it is a course code. If yes, use 'get_name_from_code' tool to get the course name. Then, use 'know_about_prerequisites' tool with [course_name] as argument.
        - if you get a query like "tell me more about [course_code]", first check if it is a course code. If yes, use 'get_name_from_code' tool to get the course name. Then, use 'get_course_info' tool with [course_name] as argument.

        RULES FOR TOOL USAGE:
        - Prerequisites query: Use 'know_about_prerequisites'.
        - Course code to name: Use 'get_name_from_code'.
        - Course name to info: Use 'get_course_info'.
        - Semester plan query: Use 'get_to_know_a_semester'.
        - Course info by code: First run 'get_name_from_code', then use 'get_course_info' on the name where name is the output from 'get_name_from_code'.
        """)
    ]

    while True:
        query = input("You : ")
        if query.lower() == "exit":
            break
        agent = AcadAgent(chat_history)
        response, chat_history = agent.run(query)
        print("\n Agent : ",response)
        print("\n\n"+ "="*80 + "\n\n")
