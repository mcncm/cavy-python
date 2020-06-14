class CavyRuntimeError(Exception):

    def __str__(self):
        return f"Error: {self.args[0]}"
