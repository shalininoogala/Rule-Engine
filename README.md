# Rule Engine with Abstract Syntax Tree (AST)

## Objective
Build a backend for a rule engine that evaluates user eligibility based on various attributes (e.g., age, department, income). The rules are represented using an Abstract Syntax Tree (AST).

## Features
- Create rules from strings and represent them as an AST.
- Combine multiple rules into a single AST.
- Evaluate rules against user-provided data.

## API Endpoints
- `POST /create_rule`: Create a new rule by sending a rule string (e.g., `{"rule_string": "age > 30 AND department = 'Sales'"}`).
- `POST /combine_rules`: Combine all created rules into a single AST.
- `POST /evaluate_rule`: Evaluate the combined rule AST against user data (e.g., `{"data": {"age": 35, "department": "Sales", "salary": 60000}}`).

## How to Run
1. Clone the repository.
2. Install dependencies using `pip install -r requirements.txt`.
3. Run the app using `python app.py`.
4. Access the API at `http://127.0.0.1:5000/` using Postman, `curl`, or other tools.
