import os
import csv


class Settings:
    """
    Takes the settings file used to instantiate an Enigma object and processes it into structures to be consumed by other methods.
    """

    def __init__(self, inputsettings):
        self.inputsettings = inputsettings
        self.mappings = self.load_mapping()

    #Loads mappings for rotors and reflectors
    def load_mapping(self):
        wmapping = {}
        #ensures the file can be found
        base_dir = os.path.dirname(__file__)
        csv_path = os.path.normpath(os.path.join(base_dir, "..", "wiring", "CSVMapping.csv"))

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            # Each row is a dict with keys "name", "wiring", "notch"
            for row in reader:
                element = row['Element'].strip()
                wiring = row['Wiring'].strip()
                notch = row.get('Notch').strip()
                wmapping[element] = {'wiring': wiring, 'notch': notch} #generates a dictionary for each element
        return wmapping

    def get_rotors(self):
        """
        Creates a list of rotors with all their corresponding settings extracted from the mapping file and settings dictionary.
        """
        names = self.inputsettings['Rotors'].split() #extract the Rotors settings
        ring_nums = [int(r) for r in self.inputsettings['Rings'].split()] #extract the rings and convert to integers
        ring_letters = [chr(num - 1 + ord('A')) for num in ring_nums]  #convert to letters to be uniform with positions for easier processing
        positions = self.inputsettings['Positions'].split() #extract positions

        #create a list where each element is a dictionary representing a rotor and its corresponding settings
        rotors = []
        for name, ring, pos in zip(names, ring_letters, positions):
            spec = self.mappings.get(name)
            if spec is None or spec['wiring'] is None:
                raise ValueError(f"Unknown rotor element: {name}")
            rotors.append({
                'element': name,
                'wiring': spec['wiring'],
                'notch': spec['notch'],
                'ring': ring,
                'position': pos,
            })
        return rotors

    def get_reflector(self):
        """
        Return a dict for the chosen reflector with keys: 'element', 'wiring'
        Looks up in the same specs dict as rotors.
        """
        ref = self.inputsettings.get('Reflector')
        spec = self.mappings.get(ref)
        if spec is None:
            raise ValueError(f"Unknown reflector element: {ref}")
        return {'element': ref, 'wiring': spec['wiring']}

    def get_plugboard_mapping(self):
        """
        Create the plugboard mapping using a list of the strings passed in the settings file.
        The plugboard object can be instantiated with such a list without the need to create pluglead objects.
        Just simpler to manage, even though it can do both to satisfy the task requirements.
        """
        pairs = self.inputsettings.get('Plugboard', [])
        # if it really is a string, split it; otherwise assume it's already a list
        if isinstance(pairs, str):
            return pairs.split()
        return pairs




