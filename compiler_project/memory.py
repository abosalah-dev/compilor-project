"""Simple interpreter that executes assignments and stores variable memory."""

from scanner import IDENTIFIER_TYPES, tokenize

OPERATORS = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}


def execute(code):
    """Execute code line by line and return memory snapshots."""
    result = {"steps": [], "final_memory": {}, "errors": []}
    if not code or not code.strip():
        result["errors"].append("Line 1: Empty input")
        return result

    tokens = tokenize(code)
    if not tokens:
        result["errors"].append("Line 1: No valid tokens found")
        return result

    memory = {}
    line_tokens = {}
    for token in tokens:
        line_tokens.setdefault(token["line"], []).append(token)

    for line_no in sorted(line_tokens):
        tokens_on_line = [t for t in line_tokens[line_no] if t["value"] not in {"{", "}"}]
        if not tokens_on_line:
            continue

        if tokens_on_line[-1]["value"] != ";":
            result["errors"].append(f"Line {line_no}: Statement must end with ';'")
            continue

        core = tokens_on_line[:-1]
        if not core:
            continue

        try:
            if core[0]["value"] in IDENTIFIER_TYPES:
                _exec_declaration(core, memory, line_no)
            else:
                _exec_assignment(core, memory, line_no)
            result["steps"].append({"line": _line_text(code, line_no), "memory": dict(memory)})
        except ValueError as exc:
            result["errors"].append(str(exc))

    result["final_memory"] = dict(memory)
    return result


def _exec_declaration(core, memory, line_no):
    """Handle declaration with required assignment."""
    if len(core) < 4:
        raise ValueError(f"Line {line_no}: Declaration must include assignment")

    var_token = core[1]
    if var_token["type"] != "Variable":
        raise ValueError(f"Line {line_no}: Invalid variable name in declaration")

    var_name = var_token["value"]
    if core[2]["value"] != "=":
        raise ValueError(f"Line {line_no}: Expected '=' in declaration of '{var_name}'")

    expr = core[3:]
    value = _eval_expression(expr, memory, line_no)
    memory[var_name] = value


def _exec_assignment(core, memory, line_no):
    """Handle reassignment statement."""
    if len(core) < 3:
        raise ValueError(f"Line {line_no}: Invalid assignment")
    if core[0]["type"] != "Variable":
        raise ValueError(f"Line {line_no}: Assignment must start with a variable")

    var_name = core[0]["value"]
    if var_name not in memory:
        raise ValueError(f"Line {line_no}: Variable '{var_name}' is not defined")
    if core[1]["value"] != "=":
        raise ValueError(f"Line {line_no}: Expected '=' in assignment")

    expr = core[2:]
    value = _eval_expression(expr, memory, line_no)
    memory[var_name] = value


def _eval_expression(expr_tokens, memory, line_no):
    """Evaluate arithmetic expression with a shunting-yard based evaluator."""
    if not expr_tokens:
        raise ValueError(f"Line {line_no}: Empty expression")

    rpn = _to_rpn(expr_tokens, line_no)
    stack = []
    for token in rpn:
        if isinstance(token, (int, float)):
            stack.append(token)
            continue

        if isinstance(token, str) and token in OPERATORS:
            if len(stack) < 2:
                raise ValueError(f"Line {line_no}: Invalid expression")
            right = stack.pop()
            left = stack.pop()
            stack.append(_apply_operator(left, right, token, line_no))
            continue

        # Token is variable name in RPN.
        if token not in memory:
            raise ValueError(f"Line {line_no}: Variable '{token}' is not defined")
        stack.append(memory[token])

    if len(stack) != 1:
        raise ValueError(f"Line {line_no}: Invalid expression")
    return stack[0]


def _to_rpn(expr_tokens, line_no):
    """Convert infix expression to Reverse Polish Notation."""
    output = []
    ops = []
    expect_operand = True

    for token in expr_tokens:
        value = token["value"]
        token_type = token["type"]

        if expect_operand:
            if token_type == "Number":
                number = float(value) if "." in value else int(value)
                output.append(number)
            elif token_type == "Variable":
                output.append(value)
            else:
                raise ValueError(f"Line {line_no}: Expected operand, found '{value}'")
            expect_operand = False
        else:
            if value not in OPERATORS:
                raise ValueError(f"Line {line_no}: Expected operator, found '{value}'")
            while ops and OPERATORS[ops[-1]] >= OPERATORS[value]:
                output.append(ops.pop())
            ops.append(value)
            expect_operand = True

    if expect_operand:
        raise ValueError(f"Line {line_no}: Expression cannot end with an operator")

    while ops:
        output.append(ops.pop())
    return output


def _apply_operator(left, right, op, line_no):
    """Apply a binary arithmetic operator."""
    if op == "+":
        return left + right
    if op == "-":
        return left - right
    if op == "*":
        return left * right
    if op == "/":
        if right == 0:
            raise ValueError(f"Line {line_no}: Division by zero")
        return left / right
    if op == "%":
        if right == 0:
            raise ValueError(f"Line {line_no}: Modulo by zero")
        return left % right
    raise ValueError(f"Line {line_no}: Unknown operator '{op}'")


def _line_text(code, line_no):
    """Return original text for a source line."""
    lines = code.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""
