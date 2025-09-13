from enigma.Plugboard import Plugboard
from enigma.Settings import Settings
from enigma.Rotor import Rotor
from enigma.Reflector import Reflector

class Enigma:

    def __init__(self, inputsettings):
        self.inputsettings = inputsettings
        """
        Enigma objects are instantiated with a dictionary of settings for all elements of the machine.
        The enigma_encode method is called with a string containing the cypher text to be encoded/ decoded.
        The method processes the Enigma object settings with a Settings object and instantiates 
         rotor, reflector and plugboard objects that have encoding methods.
        It then processes the input string and starts encoding letter by letter until it reaches the end of the string.
        It calls the encode functions arranged in the correct order and passes the result to the next one.
        It also calls step_rotors() method to simulated the movements of the rotors considering the current positions and mapped notches.
        Finally, it appends the character to an output string and returns the encoded/ decoded text.
        """


    def step_rotors(self, positions, notches):
        """
        Advance the rightmost wheel every keypress, and then
        cascade any notch‐triggered turnovers to the left.
        positions and notches are parallel lists of length number of rotors.
        """
        n = len(positions)
        pos_on_notch = [False]*n # assume no positions are on the notch
        pos_on_notch[-1] = True  # rightmost always steps

        #Any wheel whose right neighbor is at its notch also steps
        for i in range(n-2, 0, -1):
            if notches[i+1] is not None and positions[i+1] == notches[i+1]:
                pos_on_notch[i] = True # flag where a turnover is needed

        #Advance flagged positions
        for i in range(n):
            if pos_on_notch[i]:
                positions[i] = (positions[i] + 1) % 26

    def enigma_encode(self, cyphertext):
        """
        Input settings and strings to be encoded/ decoded.
        Use settings to create plugboard, rotors and reflector instances.
        For each letter in the input string encode forward and backward through the sequence of objects and generate output string.
        """
        #Settings input
        newsettings = Settings(self.inputsettings)

        #Settings processing

         ##Plugboard
        newplugleads=newsettings.get_plugboard_mapping() # a list where each element is a plug lead pair
        newplugboard=Plugboard(newplugleads) # plugboard object

         ##Rotors
        rotors=[]
        positions=[]
        notches=[]
        newrotors = newsettings.get_rotors() # a dictionary where each rotor element has attributes wiring, notches, position

        for i in range(len(newrotors)):
                rotors.append(Rotor(newrotors[i])) # generate a list of rotor objects
                positions.append(ord(newrotors[i]['position'])-ord('A'))
                if newrotors[i]['notch']:
                   notches.append(ord(newrotors[i]['notch'])-ord('A'))
                else:
                    notches.append(None)

         ##Reflector
        reflector=Reflector(newsettings.get_reflector())

        #Input code
        inputstr=cyphertext
        outputstr=''
        encodedchar=0

        #Encoding - loop over the string for each character
        for i in range(len(inputstr)):
            inputchar=inputstr[i]

            ##Plugboard encoding and transforming to an index to lookup the mappings in the next steps
            encodedchar=ord(newplugboard.encode(inputchar))-ord('A')

            ##Rotor positions setup

            self.step_rotors(positions, notches)

            ##Encode forward through the rotors
            for j in range(len(rotors)-1,-1,-1):
                encodedchar=rotors[j].encodeforward(encodedchar,positions[j])

            ##Reflector
            encodedchar =reflector.encoderefl(encodedchar)

            ##Encode backward through the rotors
            for j in range(len(rotors)):
                encodedchar = rotors[j].encodebackward(encodedchar, positions[j])

            ##Convert back to character and final pass through the plugboard
            encodedchar= chr(encodedchar + ord('A'))
            outputchar = newplugboard.encode(encodedchar)

            outputstr += outputchar

        return outputstr







