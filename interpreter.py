from contextlib import contextmanager
from typing import Any, List

from circuits.circuit import Circuit
import circuits.gates as gates
from environment import Environment
from functions import BUILTINS, AbstractFunction, Function
from lang_ast import *
from lang_token import TokenType
from lang_types import Array, Qubit, QubitMeasurement, is_linear


class InterpreterError(Exception):
    pass


class _TypeError(InterpreterError):
    pass


class Interpreter(ExprVisitor, StmtVisitor):
    def __init__(self):
        self.environment = Environment(defaults=BUILTINS)
        self.circuit = Circuit()

    def visit_binop(self, expr: BinOp) -> Any:
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        token_type = expr.op.token_type
        if token_type == TokenType.PLUS:
            return left + right
        elif token_type == TokenType.STAR:
            return left * right
        elif token_type == TokenType.EQUALEQUAL:
            return left == right
        elif token_type == TokenType.TILDEEQUAL:
            return left != right
        elif token_type == TokenType.STOPSTOP:
            return range(left, right)

    def visit_unop(self, expr: UnOp) -> Any:
        right = self.evaluate(expr.right)
        token_type = expr.op.token_type

        if token_type == TokenType.TILDE:
            if isinstance(right, Qubit):
                gates_ = self.environment.embed_gate(
                    gates.NotGate(right.index))
                self.circuit.add_gates(gates_)
                return right
            else:
                return not right

        elif token_type == TokenType.QUESTION:
            if isinstance(right, bool):
                # Stack-allocate a brand new qubit
                qubit = self.environment.alloc_one()
                if right:
                    gates_ = self.environment.embed_gate(
                        gates.NotGate(qubit.index)
                    )
                    self.circuit.add_gates(gates_)
                return qubit
            else:
                # TODO Figure out how to get a location out of expr
                raise InterpreterError(
                    0,
                    f"The value '{right}' cannot be linearized."
                )

        elif token_type == TokenType.BANG:
            if isinstance(right, Qubit):
                gates_ = self.environment.embed_gate(
                    gates.StrongMeasurementGate(right.index)
                )
                self.circuit.add_gates(gates_)
                return QubitMeasurement(right.index)
            else:
                # TODO Figure out how to get a location out of expr
                raise InterpreterError(
                    0,
                    f"The value '{right}' cannot be delinearized"
                )

    def visit_literal(self, expr: Literal) -> Any:
        return expr.literal.data

    def visit_group(self, expr: Group) -> Any:
        return self.evaluate(expr.expr)

    def visit_variable(self, expr: Variable) -> Any:
        # TODO error handling
        return self.environment[expr]

    def visit_extensionalarray(self, expr: ExtensionalArray) -> Any:
        return Array([self.evaluate(item) for item in expr.items])

    def visit_intensionalarray(self, expr: IntensionalArray) -> Any:
        reps = self.evaluate(expr.reps)
        return Array([self.evaluate(expr.item) for head in range(reps)])

    def visit_index(self, expr: Index) -> Any:
        root = self.evaluate(expr.root)
        index = self.evaluate(expr.index)
        return root[index]

    def visit_call(self, expr: Call) -> Any:
        callee = self.evaluate(expr.callee)
        if not isinstance(callee, AbstractFunction):
            raise _TypeError(f"{callee} not a function")
        args = [self.evaluate(arg) for arg in expr.args]
        if len(args) != callee.arity:
            raise InterpreterError(
                expr.paren,
                f"Function takes {callee.arity} arguments; got {len(args)}.")
        return callee.call(self, args)

    def visit_exprstmt(self, stmt: ExprStmt) -> None:
        self.evaluate(stmt.expr)

    def visit_printstmt(self, stmt: PrintStmt) -> None:
        value = self.evaluate(stmt.expr)
        print(value)

    def visit_assnstmt(self, stmt: AssnStmt) -> None:
        value = self.evaluate(stmt.rhs)
        self.environment[Variable(stmt.lhs)] = value

        # NOTE We now need to pass some extra information into the circuit if this is
        # a measurement result. If we sample from the circuit, we’d like the
        # sampled values to be mapped to the names of variables containing
        # results in this program. This feels pretty kludgy to me, but for the
        # time being I’m not sure there’s a substantially cleaner way to
        # accomplish it.
        if isinstance(value, QubitMeasurement):
            self.circuit.qubit_labels[stmt.lhs.data] = value.index

    def visit_blockstmt(self, stmt: BlockStmt) -> None:
        self.execute_blockstmt(stmt.stmts, Environment(self.environment))
        return None

    def visit_ifstmt(self, stmt: IfStmt) -> None:
        with self.coevaluate(stmt.cond) as cond_value:
            # TODO replace this check with a check on the linearity of the
            # value's type
            if isinstance(cond_value, Qubit):
                # The visitor pattern is broken here. This seems, though, to be the
                # easiest way to pass in the control data, and it should be
                # guaranteed by the parser that this is a block statement.
                control = cond_value.index
                self.execute_blockstmt(
                    stmt.then_branch.stmts,
                    Environment(self.environment, control=control))

            # classical type: this is an "ordinary" `if` statement
            elif isinstance(cond_value, bool):
                if cond_value:
                    self.execute(stmt.then_branch)
                    return
                if (else_branch := stmt.else_branch):
                    self.execute(else_branch)

            else:
                raise _TypeError(f"{cond_value} is an invalid type in a condition")

    def visit_letstmt(self, stmt: LetStmt) -> None:
        binder = stmt.binder.data
        with self.coevaluate(stmt.expr) as expr_value:
            self.execute_blockstmt(
                stmt.body.stmts,
                Environment(self.environment, defaults={binder: expr_value})
            )

    def visit_forstmt(self, stmt: ForStmt) -> None:
        binder = stmt.binder.data
        with self.coevaluate(stmt.iterator) as iterator:
            for iter_val in iterator:
                self.execute_blockstmt(
                    stmt.body.stmts,
                    Environment(self.environment, defaults={binder: iter_val})
                )

    def visit_fnstmt(self, stmt: FnStmt) -> None:
        """Define a function!
        """
        self.environment[Variable(stmt.name)] = Function(stmt.params, stmt.body)

    def evaluate(self, expr: Expression) -> Any:
        return expr.accept(self)

    @contextmanager
    def coevaluate(self, expr: Expression) -> Any:
        """This method allows code to be evaluated 'passively,' 'contravariantly,' or
        'as a change of basis'.

        NOTE This implementation is experimental and *extremely ugly.* It feels
        like a *terrible* antipattern to monkey patch the circuit and
        environment methods. Even worse, Python 3 doesn't want to let you monkey
        patch magic methods like __getitem__, and for this reason I've added a
        layer of indirection, with an inner '_getitem' method on Environment. I
        *really* have to implement this in a less offensive way. However, I do
        like using a contextmanager for it, and would like to also use a
        contextmanager for the *body* of an 'if' statement.

        NOTE 'coevaluate' might mean something else to PLT people: something
        about codata?

        """

        basis_transformation = []
        bindings = []
        add_gates_old = self.circuit.add_gates
        getitem_old = self.environment._getitem

        def add_gates_new(gates):
            # Just collect the active transformation; don’t apply it yet!
            nonlocal basis_transformation
            basis_transformation += gates

        def getitem_new(var):
            value = getitem_old(var)
            if is_linear(value):
                bindings.append((var, value))
            return value

        self.circuit.add_gates = add_gates_new
        self.environment._getitem = getitem_new
        val = self.evaluate(expr)
        self.environment._getitem = getitem_old
        self.circuit.add_gates = add_gates_old

        # Having collected the transformation gates, we time-reverse and apply
        # them.
        inv = [gate.conjugate() for gate in reversed(basis_transformation)]
        self.circuit.add_gates(inv)

        try:
            yield val

        finally:
            self.circuit.add_gates(basis_transformation)
            # After uncomputing the basis change, re-bind names that were used
            for name, value in bindings:
                self.environment[name] = value

    def execute(self, stmt: Statement) -> None:
        """Because of Python's dynamic typing, `execute` actually does exactly the same
        thing as `evaluate`. The distinction is preserved as a usage hint.
        """
        return stmt.accept(self)

    def execute_blockstmt(self, stmts: List[Statement],
                          env: Environment) -> None:
        # TODO consider changing the Environment implementation to be a context
        # manager.
        prev = self.environment
        self.environment = env
        try:
            for stmt in stmts:
                self.execute(stmt)
        finally:
            self.environment = prev

    def interpret(self, statements: List[Statement]) -> None:
        for stmt in statements:
            self.execute(stmt)
