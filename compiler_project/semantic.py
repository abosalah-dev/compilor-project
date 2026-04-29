"""Semantic analyzer that validates declarations, assignments, and brackets."""

from scanner import IDENTIFIER_TYPES, tokenize

OPERATORS = {"+", "-", "*", "/", "%"}


def _is_operand(token):
    return token["type"] in {"Variable", "Number"}


def _find_in_scopes(scopes, name):
    for scope in reversed(scopes):
        if name in scope:
            return True
    return False


def analyze(code):
    """Analyze source code and return semantic errors and warnings."""
    errors = []
    warnings = []

    if not code or not code.strip():
        return {"errors": ["Line 1: Empty input"], "warnings": warnings}

    tokens = tokenize(code)
    if not tokens:
        return {"errors": ["Line 1: No valid tokens found"], "warnings": warnings}

    scopes = [set()]
    paren_stack = []
    brace_stack = []
    statement_tokens = {}

    for token in tokens:
        line = token["line"]
        statement_tokens.setdefault(line, []).append(token)
        value = token["value"]

        if value == "(":
            paren_stack.append(line)
        elif value == ")":
            if not paren_stack:
                errors.append(f"Line {line}: Closing ')' without matching '('")
            else:
                paren_stack.pop()
        elif value == "{":
            brace_stack.append(line)
        elif value == "}":
            if not brace_stack:
                errors.append(f"Line {line}: Closing '}}' without matching '{{'")
            else:
                brace_stack.pop()

    for line in sorted(statement_tokens):
        line_tokens = statement_tokens[line]
        close_braces = sum(1 for t in line_tokens if t["value"] == "}")
        open_braces = sum(1 for t in line_tokens if t["value"] == "{")

        # Close scopes first so a line beginning with '}' exits the old scope.
        for _ in range(close_braces):
            if len(scopes) > 1:
                scopes.pop()

        # Ignore pure brace lines for statement-level checks.
        meaningful = [t for t in line_tokens if t["value"] not in {"{", "}"}]
        if not meaningful:
            for _ in range(open_braces):
                scopes.append(set())
            continue

        if meaningful[-1]["value"] != ";":
            errors.append(f"Line {line}: Statement must end with ';'")
            for _ in range(open_braces):
                scopes.append(set())
            continue

        core = meaningful[:-1]
        if not core:
            for _ in range(open_braces):
                scopes.append(set())
            continue

        # Rule: no two operators in sequence and operator has valid neighbors.
        for i, token in enumerate(core):
            if token["value"] in OPERATORS:
                if i == 0 or i == len(core) - 1:
                    errors.append(f"Line {line}: Operator '{token['value']}' missing operand")
                    continue
                if not _is_operand(core[i - 1]) or not _is_operand(core[i + 1]):
                    errors.append(f"Line {line}: Invalid operands around '{token['value']}'")

        first = core[0]
        # Declaration: <type> <var> [= expr]
        if first["value"] in IDENTIFIER_TYPES:
            if len(core) < 2 or core[1]["type"] != "Variable":
                errors.append(f"Line {line}: Invalid declaration syntax")
                continue

            var_name = core[1]["value"]
            current_scope = scopes[-1]
            if var_name in current_scope:
                errors.append(f"Line {line}: Variable '{var_name}' already declared")
            else:
                current_scope.add(var_name)

            if len(core) > 2:
                if core[2]["value"] != "=":
                    errors.append(f"Line {line}: Expected '=' after declaration of '{var_name}'")
                    continue
                expr = core[3:]
                if not expr:
                    errors.append(f"Line {line}: Missing assignment value for '{var_name}'")
                    continue
                if not _validate_expression(expr, scopes, line, errors):
                    continue
        # Assignment: <var> = expr
        elif first["type"] == "Variable":
            var_name = first["value"]
            if not _find_in_scopes(scopes, var_name):
                errors.append(f"Line {line}: Variable '{var_name}' used before declaration")
                continue

            if len(core) < 3 or core[1]["value"] != "=":
                errors.append(f"Line {line}: Assignment must follow 'variable = expression'")
                continue

            expr = core[2:]
            if not _validate_expression(expr, scopes, line, errors):
                continue
        else:
            errors.append(f"Line {line}: Unsupported statement")

        for _ in range(open_braces):
            scopes.append(set())

    for open_line in paren_stack:
        errors.append(f"Line {open_line}: Opening '(' without matching ')'")
    for open_line in brace_stack:
        errors.append(f"Line {open_line}: Opening '{{' without matching '}}'")

    # Remove duplicates while preserving order.
    unique_errors = list(dict.fromkeys(errors))
    return {"errors": unique_errors, "warnings": warnings}


def _validate_expression(expr_tokens, scopes, line, errors):
    """Validate expression operands and undeclared variable usage."""
    if not expr_tokens:
        errors.append(f"Line {line}: Empty expression")
        return False

    expect_operand = True
    for token in expr_tokens:
        value = token["value"]
        token_type = token["type"]

        if expect_operand:
            if token_type == "Variable":
                if not _find_in_scopes(scopes, value):
                    errors.append(f"Line {line}: Variable '{value}' used before declaration")
                    return False
                expect_operand = False
            elif token_type == "Number":
                expect_operand = False
            else:
                errors.append(f"Line {line}: Expected operand, found '{value}'")
                return False
        else:
            if value not in OPERATORS:
                errors.append(f"Line {line}: Expected operator, found '{value}'")
                return False
            expect_operand = True

    if expect_operand:
        errors.append(f"Line {line}: Expression cannot end with an operator")
        return False

    return True
