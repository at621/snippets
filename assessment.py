import yaml

CONFIG_FILE = 'parameter_config.yml'


with open(CONFIG_FILE, "r") as stream:
    config = yaml.safe_load(stream)


class Evaluator():
    def __init__(self) -> None:
        pass

    def equals(self, source, target):
        return source == target

    def not_equals(self, source, target):
        return source != target

    def less_or_equal(self, source, target):
        return source <= target
    
    def great_or_equal(self, source, target):
        return source >= target

    def higher(self, source, target):
        return source > target
    
    def lower(self, source, target):
        return source < target

    def between(self, source, target_range):
        if type(target_range) != list:
            raise ValueError("Target value must be a list of two values for between operator")
        if len(target_range) != 2:
            raise ValueError("Target value must be a list of two values for between operator")
        return target_range[0] <= source <= target_range[1]


def assess(value, test_name, segment):
    if test_name not in config:
        raise ValueError(f"Test name '{test_name}' is not present in the rule config")

    if segment not in config[test_name]:
        raise ValueError(f"Segment name '{segment}' is not present in the rule config for test: '{test_name}'")

    test_config = config[test_name][segment]
    
    evaluator = Evaluator()
    for rule in test_config['rules']:
        try:
            rule_operator = rule['operator']
            evaluator_func = getattr(evaluator, rule['operator'])
        except AttributeError as e:
            raise ValueError(f"operator '{rule_operator}' is not supported")
            
        result = evaluator_func(value, rule['value'])
        if result:
            return rule.color
    return None # none of the rules matched
    
assess(1, 'JEFFREYS_TEST', 'HIGH_DEFAULT_PORTFOLIO')
