from abc import ABC
from abc import abstractmethod
from enigma.PlugLead import PlugLead
from enigma.Plugboard import Plugboard
from enigma.Settings import Settings
from enigma.Rotor import Rotor
from enigma.Reflector import Reflector
from enigma.Enigma import Enigma


if __name__ == "__main__":
    """
    Ignore - a class to play with the enigma
    """

    inputsettings = {'Reflector': 'D', 'Rotors': 'V II IV', 'Rings': '06 18 07', 'Positions': 'A J L', 'Plugboard': 'UG IE PO NX WT'}
    inputstr='HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX'
    newenigma=Enigma(inputsettings)
    print(newenigma.enigma_encode(inputstr))







