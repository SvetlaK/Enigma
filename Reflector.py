class Reflector:
    def __init__(self, settingsdict):
        self.wiring = settingsdict['wiring'] #get the reflector mapping from the settings dictionary

    def maprefl(self):
        forward_map = [ord(c) - ord('A') for c in self.wiring] #create indices
        return forward_map

    def encoderefl(self, inputchar):
        map=self.maprefl()
        stepped_in = (inputchar) % 26 #map and wrap around
        mapped = map[stepped_in]
        stepped_out = (mapped) % 26
        return stepped_out

