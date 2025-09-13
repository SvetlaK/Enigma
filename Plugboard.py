from enigma.PlugLead import PlugLead

class Plugboard():
    """
    Creates a plugboard from either a string passed in the arguments or from pluglead objects.
    Encodes letters using the pluglead pairs.
    """
    def __init__(self, newplugleads):
        self.pairs=newplugleads
        self.plugls=[]

    def add(self, pluglead):
        """
        Used to handle pluglead objects.
        """
        self.plugls.append(str(PlugLead(pluglead)))
        return self.plugls

    def encode(self, inputchar):
        """
        Encodes letters using the pluglead pairs.
        If Plugboard is instatiated with a list, use that, otherwise create a list from the pluglead strings.
        If the input character is some of the letters in the pluglead pairs, return the other letter from the pair as resultchar.
        """
        leads = self.pairs
        if self.pairs==[]:
           leads=self.plugls
        resultchar=inputchar
        for i in range(len(leads)):
            pair = leads[i]
            a, b = pair[0], pair[1]
            if inputchar == a:
               resultchar = b
            elif inputchar == b:
                 resultchar = a
        return resultchar


