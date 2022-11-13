import argparse

class ArgumentParser:
    def __init__(self, description : str, argumendict : "dict((type, str))"):
        self.parser = argparse.ArgumentParser(description=description)
        for argname in argumendict.keys():
            type_input, desc_help = argumendict[argname]
            if type_input is None:
                self.parser.add_argument(argname, help=desc_help, action="store_true",const=True, default=False)
            else:
                self.parser.add_argument(argname, type=type_input, help=desc_help)
    
    def parse_args(self) -> argparse.Namespace:
        return self.parser.parse_args()