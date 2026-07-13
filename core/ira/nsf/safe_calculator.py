"""
Safe Calculator for NSF.
Implements the Shunting-Yard algorithm to evaluate infix mathematical expressions
safely without using eval() or exec().
"""
import re
import math
from typing import List, Union
from core.ira.shared.exceptions import SymbolicExecutionError

class SafeCalculator:
    def __init__(self):
        # Operators: (precedence, associativity)
        # L = Left, R = Right
        self.operators = {
            '+': (2, 'L'),
            '-': (2, 'L'),
            '*': (3, 'L'),
            '/': (3, 'L'),
            '%': (3, 'L'),
            '^': (4, 'R')
        }
        
        self.functions = {
            'sqrt': math.sqrt,
            'sin': math.sin,
            'cos': math.cos,
            'tan': math.tan,
            'log': math.log,
            'log10': math.log10,
            'abs': abs,
            'ceil': math.ceil,
            'floor': math.floor,
            'round': round
        }

    def evaluate(self, expression: str) -> float:
        expr = expression.strip()
        if not expr:
            raise SymbolicExecutionError(expression, "Empty expression")
            
        try:
            tokens = self._tokenize(expr)
            rpn = self._shunting_yard(tokens)
            result = self._eval_rpn(rpn)
            return float(result)
        except SymbolicExecutionError:
            raise
        except Exception as e:
            raise SymbolicExecutionError(expression, str(e))

    def _tokenize(self, expr: str) -> List[Union[float, str]]:
        # Regex to match numbers (including floats and scientific notation),
        # word tokens (functions/variables), and single operators/parentheses.
        token_specification = [
            ('NUMBER',   r'\d+(?:\.\d*)?(?:[eE][+-]?\d+)?'),
            ('FUNCTION', r'[a-zA-Z_][a-zA-Z0-9_]*'),
            ('OPERATOR', r'[+\-*/^%]'),
            ('LPAREN',   r'\('),
            ('RPAREN',   r'\)'),
            ('SKIP',     r'\s+'),
            ('MISMATCH', r'.')
        ]
        
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        tokens = []
        
        for mo in re.finditer(tok_regex, expr):
            kind = mo.lastgroup
            value = mo.group()
            
            if kind == 'NUMBER':
                tokens.append(float(value))
            elif kind == 'FUNCTION':
                if value not in self.functions:
                    raise SymbolicExecutionError(expr, f"Unknown function: {value}")
                tokens.append(value)
            elif kind in ('OPERATOR', 'LPAREN', 'RPAREN'):
                tokens.append(value)
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                raise SymbolicExecutionError(expr, f"Unexpected character: {value}")
                
        # Handle unary minus/plus
        processed_tokens = []
        for i, tok in enumerate(tokens):
            if tok in ('+', '-'):
                # Unary if it is the first token, or if it follows an operator or left parenthesis
                is_unary = (i == 0) or (tokens[i - 1] in self.operators or tokens[i - 1] == '(')
                if is_unary:
                    if tok == '-':
                        # Represent unary minus as a special operator 'u-'
                        processed_tokens.append('u-')
                    elif tok == '+':
                        # Unary plus is a no-op, just ignore
                        continue
                else:
                    processed_tokens.append(tok)
            else:
                processed_tokens.append(tok)
                
        return processed_tokens

    def _shunting_yard(self, tokens: List[Union[float, str]]) -> List[Union[float, str]]:
        output_queue = []
        operator_stack = []
        
        for token in tokens:
            if isinstance(token, float):
                output_queue.append(token)
            elif token in self.functions:
                operator_stack.append(token)
            elif token in self.operators or token == 'u-':
                # Determine precedence and associativity of token
                if token == 'u-':
                    token_prec, token_assoc = 5, 'R' # High precedence for unary minus
                else:
                    token_prec, token_assoc = self.operators[token]
                    
                while operator_stack:
                    top = operator_stack[-1]
                    if top == '(':
                        break
                        
                    if top in self.functions:
                        output_queue.append(operator_stack.pop())
                        continue
                        
                    # Top of stack operator precedence/assoc
                    if top == 'u-':
                        top_prec, top_assoc = 5, 'R'
                    else:
                        top_prec, top_assoc = self.operators[top]
                        
                    if (token_assoc == 'L' and token_prec <= top_prec) or (token_assoc == 'R' and token_prec < top_prec):
                        output_queue.append(operator_stack.pop())
                    else:
                        break
                operator_stack.append(token)
            elif token == '(':
                operator_stack.append(token)
            elif token == ')':
                peeled = False
                while operator_stack:
                    top = operator_stack.pop()
                    if top == '(':
                        peeled = True
                        break
                    output_queue.append(top)
                if not peeled:
                    raise SymbolicExecutionError("", "Mismatched parentheses")
                    
                if operator_stack and operator_stack[-1] in self.functions:
                    output_queue.append(operator_stack.pop())
                    
        while operator_stack:
            top = operator_stack.pop()
            if top in ('(', ')'):
                raise SymbolicExecutionError("", "Mismatched parentheses")
            output_queue.append(top)
            
        return output_queue

    def _eval_rpn(self, rpn: List[Union[float, str]]) -> float:
        stack = []
        
        for token in rpn:
            if isinstance(token, float):
                stack.append(token)
            elif token == 'u-':
                if not stack:
                    raise SymbolicExecutionError("", "Malformed RPN: stack underflow for unary operator")
                val = stack.pop()
                stack.append(-val)
            elif token in self.operators:
                if len(stack) < 2:
                    raise SymbolicExecutionError("", f"Malformed RPN: stack underflow for operator {token}")
                b = stack.pop()
                a = stack.pop()
                res = self._apply_operator(token, a, b)
                stack.append(res)
            elif token in self.functions:
                if not stack:
                    raise SymbolicExecutionError("", f"Malformed RPN: stack underflow for function {token}")
                arg = stack.pop()
                res = self._apply_function(token, arg)
                stack.append(res)
                
        if len(stack) != 1:
            raise SymbolicExecutionError("", f"Malformed RPN: expected single result, got stack {stack}")
            
        return stack[0]

    def _apply_operator(self, op: str, a: float, b: float) -> float:
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '*':
            return a * b
        elif op == '/':
            if b == 0:
                raise SymbolicExecutionError(f"{a} / {b}", "Division by zero")
            return a / b
        elif op == '%':
            if b == 0:
                raise SymbolicExecutionError(f"{a} % {b}", "Modulo by zero")
            return a % b
        elif op == '^':
            try:
                # Limit power size to avoid overflow crashes
                if a == 0 and b < 0:
                    raise SymbolicExecutionError(f"{a} ^ {b}", "Zero raised to a negative power")
                return math.pow(a, b)
            except OverflowError:
                raise SymbolicExecutionError(f"{a} ^ {b}", "Numerical overflow")
        else:
            raise SymbolicExecutionError(f"{a} {op} {b}", f"Unknown operator {op}")

    def _apply_function(self, func_name: str, arg: float) -> float:
        func = self.functions.get(func_name)
        if not func:
            raise SymbolicExecutionError(func_name, f"Unknown function {func_name}")
            
        try:
            # Handle math domain errors (e.g. sqrt(-1))
            return func(arg)
        except ValueError as e:
            raise SymbolicExecutionError(f"{func_name}({arg})", f"Math domain error: {e}")
        except OverflowError:
            raise SymbolicExecutionError(f"{func_name}({arg})", "Numerical overflow")
