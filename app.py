from flask import Flask, request, jsonify
import ast
import operator
import logging
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize Flask application and Limiter
app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Node class to represent the Abstract Syntax Tree (AST)
class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # 'operator' or 'operand'
        self.left = left       # Left child node (for operators)
        self.right = right     # Right child node (for operators)
        self.value = value     # Value for operand nodes (for conditions)

    def __repr__(self):
        return f"Node(type={self.type}, value={self.value}, left={self.left}, right={self.right})"

# Function to safely evaluate expressions
def safe_eval(expression, data):
    allowed_operators = {
        'AND': operator.and_,
        'OR': operator.or_,
        '<': operator.lt,
        '>': operator.gt,
        '==': operator.eq,
        '<=': operator.le,
        '>=': operator.ge,
        '!=': operator.ne
    }
    
    try:
        expr_ast = ast.parse(expression, mode='eval')
        for node in ast.walk(expr_ast):
            if isinstance(node, ast.Name) and node.id not in data:
                raise ValueError(f"Undefined variable: {node.id}")
            if isinstance(node, ast.Compare) and not all(isinstance(op, ast.Compare) for op in node.ops):
                raise ValueError("Invalid comparison operation.")
    except Exception as e:
        raise ValueError(f"Error parsing expression: {e}")

    return eval(compile(expr_ast, '', mode='eval'), {}, allowed_operators)

# Function to create an AST from a rule string
def create_rule(rule_string):
    operators = {
        'AND': 'operator',
        'OR': 'operator'
    }
    rule_parts = rule_string.split()
    if len(rule_parts) < 3:
        return None
    left_operand = Node('operand', value=' '.join(rule_parts[:-2]))
    right_operand = Node('operand', value=' '.join(rule_parts[-2:]))
    return Node('operator', left=left_operand, right=right_operand, value=rule_parts[-2])

# Function to combine multiple rules into one AST
def combine_rules(rules):
    if not rules:
        return None
    if len(rules) == 1:
        return rules[0]
    
    combined = rules[0]
    for rule in rules[1:]:
        combined = Node('operator', left=combined, right=rule, value='AND')
    return combined

# Function to evaluate the AST against given data
def evaluate_rule(ast, data):
    if ast.type == 'operand':
        return safe_eval(ast.value, data)
    elif ast.type == 'operator':
        left_eval = evaluate_rule(ast.left, data)
        right_eval = evaluate_rule(ast.right, data)
        return left_eval and right_eval if ast.value == 'AND' else left_eval or right_eval

# In-memory list to store rules
rules = []

# API route to create a rule
@app.route('/create_rule', methods=['POST'])
@limiter.limit("5 per minute")
def create_rule_api():
    """Create a new rule and store it as an AST."""
    rule_string = request.json.get('rule_string')
    if not rule_string:
        logger.error("Rule string is missing")
        return jsonify({"error": "Rule string is required"}), 400

    ast = create_rule(rule_string)
    if ast:
        rules.append(ast)
        logger.info(f"Rule created: {ast}")
        return jsonify({"message": "Rule created", "ast": str(ast)}), 200
    
    logger.error("Invalid rule format")
    return jsonify({"error": "Invalid rule format"}), 400

# API route to combine rules
@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    """Combine existing rules into a single AST."""
    combined_ast = combine_rules(rules)
    if combined_ast:
        return jsonify({"message": "Rules combined", "ast": str(combined_ast)}), 200
    return jsonify({"error": "No rules to combine"}), 400

# API route to evaluate the combined rule
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    """
    Evaluate the combined rule against provided data.
    Expected JSON format: {"data": {"age": 35, "department": "Sales"}}
    """
    data = request.json.get('data')
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    combined_ast = combine_rules(rules)
    if not combined_ast:
        return jsonify({"error": "No rules to evaluate"}), 400
    
    result = evaluate_rule(combined_ast, data)
    return jsonify({"eligible": result}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
