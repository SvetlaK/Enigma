class Rotor:
    """
        Instantiates rotor objects using the settings dictionary.
        Creates maps for the wiring.
        Encodes letters forward/ backward applying appropriate offsets for positions and rings.
    """
    def __init__(self, settingsdict):
        self.wiring = settingsdict['wiring']
        self.position = settingsdict["position"]
        self.ring = ord(settingsdict["ring"])-ord('A')
        self.notch = settingsdict["notch"]

    #Create the forward map using the wiring mapping
    def rotormapforward(self):
        forward_map = [ord(c) - ord('A') for c in self.wiring]
        return forward_map

    #Reverse the forward map to create the backward one
    def rotormapbackward(self):
        backward_map = [0] * 26
        for i, v in enumerate(self.rotormapforward()): #reverse the forward map
            backward_map[v] = i
        return backward_map

    #Encode a letter using the forward map, applying position and ring offsets
    def encodeforward(self, inputchar, offsetpos):
        mapfwd=self.rotormapforward()
        stepped_in = (inputchar+offsetpos-self.ring) % 26 #add the offsets and wrap around
        mapped = mapfwd[stepped_in]
        stepped_out = (mapped-offsetpos+self.ring) % 26
        return stepped_out

    #Encode a letter using the backward map, adjusting for position and ring settings
    def encodebackward(self, inputchar, offsetpos):
        mapbwd = self.rotormapbackward()
        stepped_in = (inputchar+offsetpos-self.ring) % 26
        mapped = mapbwd[stepped_in]
        stepped_out = (mapped-offsetpos+self.ring) % 26
        return stepped_out

    #Simple rotor for the task
    def simplerotorforward(self, inputchar):
        mapfwd = self.rotormapforward()
        input=ord(inputchar)-ord('A')
        stepped_in = (input) % 26
        mapped = mapfwd[stepped_in]
        stepped_out = (mapped) % 26
        return chr(stepped_out + ord('A'))

    # Simple rotor for the task
    def simplerotorbackward(self, inputchar):
        mapbwd = self.rotormapbackward()
        input=ord(inputchar)-ord('A')
        stepped_in = (input) % 26
        mapped = mapbwd[stepped_in]
        stepped_out = (mapped) % 26
        return chr(stepped_out + ord('A'))


