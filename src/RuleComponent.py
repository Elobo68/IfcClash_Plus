import ifcopenshell


class RuleFile:
    def __init__(self):
        self.id: str = ""
        self.list_ifc_path: list[str] = []
        self.list_ifc_file: list[ifcopenshell.file] = []
        self.contains: list = []  # Union of folder or Rule

    def run(self):
        for rulecheck_or_folder in self.contains:
            rulecheck_or_folder.run()


class RuleFolder:
    def __init__(self):
        self.id: str = "AZE"
        self.activation_rule: str = True
        self.activation_case: str = "ALLTRUE"
        self.contains: list = []  # Union of folder or Rule

    def check_Activation_Rule(self):
        if self.activation_rule is None:
            return True
        # @todo do the activation rule
        return True

    def run(self):
        if self.check_Activation_Rule():
            for rulecheck_or_folder in self.contains:
                rulecheck_or_folder.run()
        else:
            return False
