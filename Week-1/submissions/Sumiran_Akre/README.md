# Academic Advisor & Curriculum Assistant

An intelligent, LLM-powered academic advisor agent designed to assist Computer Science and Engineering students with curriculum navigation, course scheduling, and prerequisite checking. 

This agent uses **LangChain**, **Pydantic** for structured validation, and **Groq (`llama-3.1-8b-instant`)** to translate dry database facts into comprehensive, guidance-rich student advisor responses.

---

## 🌟 Key Features

1. **Course Code Translation**:
   - Automatically translates course codes (e.g., `CSL351`, `PHP102`) to full course names.
   - Robust normalization handles spaces (e.g., `CSL 301` vs `CSL301`) and composite slashes (e.g., `NCN 101` matching `"NCN101/NCN102"`).

2. **Detailed Course Profiles**:
   - Retrieves credits, L-T-P-C structure, category, overlap details, and the full official syllabus.
   - Augments structured database records with general academic context and recommended study materials.

3. **Prerequisite Analysis**:
   - Evaluates whether a course has prerequisite requirements (e.g., checks if a student must complete `MAL100` before taking `MAL403`).
   - Accurately identifies institute core or non-graded courses that require no prerequisites.

4. **Semester Planning**:
   - Provides full credit allocations, mandatory courses, and elective recommendations for any given semester (1 to 8).

---

## 🛠️ Tool Architecture

The agent operates as a tool-use (function-calling) loop with the following tools defined:

| Tool Name                 | Input Schema         | Description |
| :---                      | :---                 | :---                                                                  |
| `get_name_from_code`      | `course_code: str`   | Retrieves the course name matching the normalized course code. |
| `get_course_info`         | `course_name: str`   | Retrieves detailed information, syllabus, and metadata by name or code. |
| `know_about_prerequisites`| `course_name: str`   | Checks and lists all required prerequisites for a course. |
| `get_to_know_a_semester`  | `sem: int`           | Returns the entire course structure and credits for a specific semester. |

---

## 📂 Project Structure

---

## 🚀 Setup & Execution

### 1. Prerequisites
Ensure you have Python 3.10+ and a virtual environment set up. Install the required dependencies using the `requirements.txt` file:
```bash
pip install -r requirements.txt
```
Alternatively, install the required packages directly:
```bash
pip install pydantic python-dotenv langchain_groq langchain_core
```

### 2. Configure Environment Variables
Create a `.env` file in the root of the `Week-1/submissions/Sumiran_Akre` directory and add your Groq API key:
```env
groq=your_groq_api_key_here
```

### 3. Run the Agent
Start the interactive CLI loop:
```bash
python acad_advisor_agent.py
```

---

## 💬 Sample Interactions & Outputs

### 1. Querying Course Details using Course Code
When queried with a course code like `CSL351`, the agent automatically maps it to `Computer Networks` and fetches its details:

```text
You : Do you know about the Course CSL351

[TOOL]: get_name_from_code
[ARGS]: {'course_code': 'CSL351'}
[TOOL OUTPUT]: Computer Networks

[TOOL]: get_course_info
[ARGS]: {'course_name': 'Computer Networks'}
[TOOL OUTPUT]: {'semester': None, 'category': 'Program Core Course', 'details': {'code': 'CSL351', 'name': 'Computer Networks', ...}}

Agent : ### Computer Networks (CSL351)

#### Course Details
* **Course Code**: CSL351
* **Course Name**: Computer Networks
* **Credits**: 4
* **Category**: Program Core Course
* ...continued
```

### 2. Querying Prerequisites
Checking if any prerequisites are required:

```text
You : Tell me about the pre requisites of the course

[TOOL]: know_about_prerequisites
[ARGS]: {'course_name': 'Computer Networks'}
[TOOL OUTPUT]: No pre-requisite required for Computer Networks

Agent : ### Prerequisites for Computer Networks (CSL351)
There are no prerequisites required for the Computer Networks course. This means that students can take this course without having to complete any other courses first.
```

### 3. Semester Planning
Helping a student plan their upcoming semester:

```text
You : Currently I have completed my second sem can help me plan my 3rd sem

[TOOL]: get_to_know_a_semester
[ARGS]: {'sem': 3}
[TOOL OUTPUT]: {'semester': 3, 'courses': [{'code': 'MAL403', 'name': 'Probability & Statistics', ...}], 'total_credits': 19}

Agent : Based on the semester plan for the 3rd semester, it appears that you have a total of 19 credits to complete. Here's a breakdown of the courses you need to take:

### 3rd Semester Course Plan
#### Mandatory Courses
* **Probability & Statistics (MAL403)**: This course covers the fundamental concepts of probability...
* **Discrete Mathematics (CSL201)**: This course introduces you to the basics of discrete mathematics...
* ...continued
```
