from flask import Flask, request, jsonify

# Node class to represent the Abstract Syntax Tree (AST)
class Node:
    def __init__(self, node_type, left=None, right=None, value=None):
        self.type = node_type  # 'operator' or 'operand'
        self.left = left       # Left child node (for operators)
        self.right = right     # Right child node (for operators)
        self.value = value     # Value for operand nodes (for conditions)

    def __repr__(self):
        return f"Node(type={self.type}, value={self.value}, left={self.left}, right={self.right})"

# Function to create an AST from a rule string
def create_rule(rule_string):
    # Simplified rule string parsing to AST (hardcoded example)
    if rule_string == "age > 30 AND department = 'Sales'":
        return Node('operator', left=Node('operand', value='age > 30'),
                              right=Node('operand', value="department = 'Sales'"))
    elif rule_string == "age < 25 AND department = 'Marketing'":
        return Node('operator', left=Node('operand', value='age < 25'),
                              right=Node('operand', value="department = 'Marketing'"))
    elif rule_string == "salary > 50000 OR experience > 5":
        return Node('operator', left=Node('operand', value='salary > 50000'),
                              right=Node('operand', value="experience > 5"), value='OR')
    return None

# Function to combine multiple rules into one AST
def combine_rules(rules):
    if len(rules) == 1:
        return rules[0]
    
    combined = rules[0]
    for rule in rules[1:]:
        combined = Node('operator', left=combined, right=rule, value='AND')
    return combined

# Function to evaluate the AST against given data
def evaluate_rule(ast, data):
    if ast.type == 'operand':
        # Evaluate the operand condition dynamically based on provided data
        return eval(ast.value, {}, data)  # Warning: Use `eval` with caution in production
    elif ast.type == 'operator':
        left_eval = evaluate_rule(ast.left, data)
        right_eval = evaluate_rule(ast.right, data)
        return left_eval and right_eval if ast.value == 'AND' else left_eval or right_eval

# Initialize Flask application
app = Flask(__name__)
rules = []  # In-memory list to store rules

# API route to create a rule
@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    rule_string = request.json.get('rule_string')
    ast = create_rule(rule_string)
    if ast:
        rules.append(ast)
        return jsonify({"message": "Rule created", "ast": str(ast)}), 200
    return jsonify({"error": "Invalid rule format"}), 400

# API route to combine rules
@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    combined_ast = combine_rules(rules)
    return jsonify({"message": "Rules combined", "ast": str(combined_ast)}), 200

# API route to evaluate the combined rule
@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    data = request.json.get('data')
    combined_ast = combine_rules(rules)
    result = evaluate_rule(combined_ast, data)
    return jsonify({"eligible": result}), 200

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
