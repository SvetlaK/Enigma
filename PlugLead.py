class PlugLead():
    def __init__(self,pair):
        """
        Generates a pluglead pair and encodes a letter
        """
        self.pair = pair

    def __repr__(self):
        """
        Ensures that when called or used in a list returns the string representation of the lead pair
        """
        return str(self.pair)

    def __str__(self):
        """
        Ensures that when called with str() returns the string representation of the lead pair
        """
        return str(self.pair)

    def encode(self, entry_char):
        """
        Encodes a letter
        """
        if entry_char==self.pair[0]:
            return self.pair[1]
        elif entry_char==self.pair[1]:
            return self.pair[0]
        else:
            return entry_char

