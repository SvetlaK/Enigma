from enigma.Enigma import Enigma
from enigma.Settings import Settings
import string
import itertools
import os
import csv

class Bombe:
    def __init__(self, code, cribs, knownsettings, permittedsettings):
        """
        - code:      the ciphertext string
        - cribs:     the known plaintext substring
        - knownsettings: dictionary, mapping each of the five stages either to:
             • a setting string (e.g. 'Beta Gamma V'),
             • 'x' if unknown,
        - permittedsettings: dictionary, mapping each of the five stages either to:
             • a single setting string containing all the possible options separated by a space (for elements with mappings)
             • empty if not applicable or no restrictions (for elements with ranges)
        """
        self.code = code
        self.cribs = cribs
        # fixed search order
        self.stages = ['Reflector','Rotors','Rings','Positions','Plugboard']
        # 1) Normalize knownsettings into a new dictionary per iterable stage
        self.known_options = {}
        self.nrotors=0 #number of rotors inferred from the input settings to allow handling different configurations
        for stage in self.stages:
            v = knownsettings[stage].split()
            self.known_options[stage] = v
        self.nrotors=len(self.known_options['Rotors']) #the input pattern assumes that for each rotor there will be an 'x' and that positions and notches would match

        # 2) Normalize permittedsettings into a new dictionary per iterable stage
        self.permitted_options = {}
        for stage in self.stages:
            v = permittedsettings[stage].split()
            self.permitted_options[stage] = v
        # 3) For pruning: keep track of which candidates have already failed
        self.discard = {stage: set() for stage in self.stages} #the discard pile per stage in the specific order embedded in self.stages to allow backtracking and efficient pruning


    def solve(self):
        """
        Starts the recursive search in the self.stages order with each method calling the deeper level.
        At the bottom the recursion does one of two options:
        - if no solution - discards the setting and bubbles up None
        - if solution - bubbles up the decoded cypher text.
        Whether a valid solution is obtained is determined by a _check method.
        The _check method simply generates an Enigma object with the settings passed by the Plugboard and attempts to decode the cypher text.
        If the crib is found somewhere in the attempt, it returns the decoded string, otherwise returns None.
        """
        # start with a settings dict; values will be strings
        settings = {stage: 'x' for stage in self.stages}
        return self._search_reflector(settings)



    #Stage 1: Reflector
    def _search_reflector(self, settings):
        self.discard['Reflector'].clear() #purges the discard pile once we move forward to avoid rejecting valid solutions
        for refl in self.known_options['Reflector']:
            if refl=='x': #unknown reflector, so used each permitted value in turn and recurses
               for value in self.permitted_options['Reflector']:
                   s = settings.copy() #avoid scrambling the main settings file
                   s['Reflector'] = value
                   solution = self._search_rotors(s) #the recursive call
                   if solution is not None: #bubbles up either None or the decoded string
                       return solution
                   self.discard['Reflector'].add(s['Reflector']) #discard the unsuccessful setting and iterate again
            elif refl == 'D': #custom reflector that calls a _tamper function and generates new reflector mappings
                s = settings.copy()
                # delegate to tamper stage
                s['Reflector'] = 'D'
                solution = self._tamper(s)
                if solution is not None:
                    return solution
            else: #known reflector, recurses
                s = settings.copy()
                s['Reflector'] = refl
                solution = self._search_rotors(s)
                if solution is not None:
                    return solution
        return None

    def _tamper(self, settings):
        """
        A method to tamper with the reflector board by scrambling four plugleads i.e. changing the mapping for eight letters.
        The method creates three list for the three permitted reflectors` mappings.
        For each list it reassigns four pairs in all possible ways,
         with each variant being written as a mapping in the CSVMapping.csv, the source for all mappings.
        From that point, _tamper recurses.
        When finally _check creates an Enigma with the settings file,
         the Settings object reads the mapping from element='D' in CSVMapping.csv.
        From there Enigma decodes as usual and returns the decoded string.
        _check bubbles up the result. If it reaches _tamper, it tries another variant of the four pairs and writes over D element in the csv.
        When all variants are exhausted, another set of pairs is created until a solution is found.
        """
        newsettings = Settings(settings)
        mapreflector=newsettings.load_mapping() #loads the CSV mapping in a suitable format
        maps=[None]*3
        maps[0]=mapreflector['A']['wiring']
        maps[1]=mapreflector['B']['wiring']
        maps[2]=mapreflector['C']['wiring']
        for map in maps: #first tries reflector A, then B, then C
            wiring=list(map) #creates a list from the mapping
            pairs = []
            for i, letter in enumerate(wiring): #list of pairs between the alphabet index and the mapping index
                j = ord(letter) - ord('A') #convert to an index
                if i < j:
                    pairs.append((i, j)) #create a list of pairs

            #For each choice of two distinct reflector wires (you have to scramble exactly two wires per go):
            for (i1, i2), (i3, i4) in itertools.combinations(pairs, 2):
                #Option A of first swap: reconnect i1–i3 & i2–i4
                interm1 = wiring.copy()
                interm1[i1], interm1[i3] = wiring[i3], wiring[i1]
                interm1[i2], interm1[i4] = wiring[i4], wiring[i2]

                #Option B of first swap: reconnect i1–i4 & i2–i3
                interm2 = wiring.copy()
                interm2[i1], interm2[i4] = wiring[i4], wiring[i1]
                interm2[i2], interm2[i3] = wiring[i3], wiring[i2]

                for interm in (interm1, interm2): #scramble another two wires for each combination produced above
                    #remove the two just-used pairs to ensure no repetition
                    remaining = [p for p in pairs if p not in ((i1, i2), (i3, i4))]

                    #second swap: pick two more from the remaining 11
                    for (i5, i6), (i7, i8) in itertools.combinations(remaining, 2):
                        # Option A₂: reconnect i5–i7 & i6–i8
                        final1 = interm.copy()
                        final1[i5], final1[i7] = interm[i7], interm[i5]
                        final1[i6], final1[i8] = interm[i8], interm[i6]
                        wA = ''.join(final1) #mapping variant 1


                        # Option B₂: reconnect i5–i8 & i6–i7
                        final2 = interm.copy()
                        final2[i5], final2[i8] = interm[i8], interm[i5]
                        final2[i6], final2[i7] = interm[i7], interm[i6]
                        wB = ''.join(final2) #mapping variant 2

                        wiringvariants = wA, wB #tuple to iterate


                        for wiringvariant in wiringvariants: #variant one writing in the csv file
                            base_dir = os.path.dirname(__file__)
                            csv_path = os.path.normpath(os.path.join(base_dir, "..", "wiring", "CSVMapping.csv"))
                            with open(csv_path, "r", encoding="utf-8-sig", newline="") as csvfile:
                                 reader = csv.DictReader(csvfile)
                                 # Each row is a dict with keys "name", "wiring", "notch"
                                 fieldnames = reader.fieldnames or ['Element', 'Wiring', 'Notch']
                                 rows = list(reader)

                            for row in rows:
                                if row.get('Element', '') == 'D':
                                   row['Wiring'] = wiringvariant
                                   row['Notch'] = ''

                            # Write everything back
                            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                                 writer = csv.DictWriter(f, fieldnames=fieldnames)
                                 writer.writeheader()
                                 writer.writerows(rows)

                            s = settings.copy()
                            s['Reflector'] = 'D' #pass reflector D below so that the Enigma reads the generated mapping in the csv
                            solution = self._search_rotors(s)
                            if solution is not None:
                               return solution
        return None



    # Stage 2: Rotors
    def _search_rotors(self, settings):
        domains = []
        for templ in self.known_options['Rotors']:
            if templ == 'x':
                domains.append([r for r in self.permitted_options['Rotors']
                                if r not in self.discard['Rotors']]) #creates a list of possible options removing anything in discard
            else:
                domains.append([templ]) #if the reflector is known, take the known value

        self.discard['Rotors'].clear()

        for combo in itertools.product(*domains): #creates combinations of the possible and known options
            rotor_str = list(combo)  # ['Beta', 'III', 'V']
            key = ' '.join(rotor_str)  # "Beta III V"

            #skip if already discarded
            if key in self.discard['Rotors']:
                continue

            s = settings.copy()
            s['Rotors'] = key
            solution = self._search_rings(s)
            if solution is not None:
                return solution

            self.discard['Rotors'].add(key)

        return None


    # Stage 3: Rings
    def _search_rings(self, settings):
        domains = []
        for templ in self.known_options['Rings']:
            if templ != 'x':
                domains.append([templ]) #take the known value
            else:
                if self.permitted_options['Rings']:
                    #use your permitted list if it’s non-empty
                    domains.append(self.permitted_options['Rings'])
                else:
                    #otherwise generate the full 01–26 range
                    domains.append([str(n).zfill(2) for n in range(1, 27)])
        self.discard['Rings'].clear()
        for combo in itertools.product(*domains):
            key = ' '.join(combo)  # "04 12 19"
            if key in self.discard['Rings']:
                continue
            s = settings.copy()
            s['Rings'] = key
            sol = self._search_positions(s)
            if sol is not None:
                return sol
            self.discard['Rings'].add(key)
        return None


    # Stage 4: Start positions
    def _search_positions(self, settings):
        domains = []
        for templ in self.known_options['Positions']:
            if templ != 'x':
                domains.append([templ])
            else:
                if self.permitted_options['Positions']:
                    domains.append(self.permitted_options['Positions'])
                else:
                    # otherwise generate the full 01–26 range
                    domains.append(list(string.ascii_uppercase))
        self.discard['Positions'].clear()
        for combo in itertools.product(*domains):
            key = ' '.join(combo)  # "A M Z"
            if key in self.discard['Positions']:
                continue
            s = settings.copy()
            s['Positions'] = key
            solution = self._search_plugboard(s)
            if solution is not None:
                return solution
            self.discard['Positions'].add(key)
        return None


    # Stage 5: Plugboard
    def _search_plugboard(self, settings):
        domains = []
        self.discard['Plugboard'].clear()
        for templ in self.known_options['Plugboard']:
            if len(templ) != 2:
                raise ValueError(f"Plugboard template must be length 2, got {templ!r}")
            a, b = templ[0], templ[1]
            # Case 1: fully known, e.g. "FL"
            if 'x' not in templ:
                domains.append([templ])
            # Case 2: both unknown → "xx"
            elif templ == 'xx':
                if self.permitted_options['Plugboard']:
                    domains.append(self.permitted_options['Plugboard'])
                else:
                    # fallback to all unordered pairs of letters A–Z
                    domains.append(
                        [''.join(p) for p in itertools.combinations(string.ascii_uppercase, 2)]
                    )
            # Case 3: one known, one unknown → e.g. "Jx" or "xM"
            else:
                known, pos = (a, 1) if b == 'x' else (b, 0)
                options = []
                for L in string.ascii_uppercase:
                    if L == known:
                        continue
                    # put the known letter in its fixed spot
                    pair = (L + known) if pos == 0 else (known + L)
                    options.append(pair)
                domains.append(options)
        for combo in itertools.product(*domains):
            key = ' '.join(combo)
            if key in self.discard['Plugboard']:
                continue
            s = settings.copy()
            s['Plugboard'] = key
            if self._check(s):
                return Enigma(s).enigma_encode(self.code)
            self.discard['Plugboard'].add(key)
        return None


    # Solution
    def _check(self, settings):
        enigma = Enigma(settings) #creates an enigma object with settings passed from the recursion
        pt = enigma.enigma_encode(self.code) #decodes the cypher text using that Enigma
        for i in range(len(pt) - len(self.cribs) + 1): #traverse the 'decoded' cypher
            if pt[i:i+len(self.cribs)] == self.cribs: #if we find the crib somewhere, return the crib
                print(settings) #also print the successul settings for reference
                return pt #return the decoded string
        return None

#Decoding exercises


#Code 1

knownsettings={'Rotors': 'Beta Gamma V',
                   'Reflector': 'x',
                   'Rings': '04 02 14',
                   'Positions': 'M J M',
                   'Plugboard': 'KI XN FL'}

permittedsettings={'Rotors': 'Beta Gamma I II III IV V',
                   'Reflector': 'A B C D',
                   'Rings': '',
                   'Positions': '',
                   'Plugboard': ''}

newbombe=Bombe('DMEXBMKYCVPNQBEDHXVPZGKMTFFBJRPJTLHLCHOTKOYXGGHZ','SECRETS',knownsettings,permittedsettings)
#print(newbombe.solve())


#Code 2

knownsettings={'Rotors': 'Beta I III',
                   'Reflector': 'B',
                   'Rings': '23 02 10',
                   'Positions': 'x x x',
                   'Plugboard': 'VH PT ZG BJ EY FS'}

permittedsettings={'Rotors': 'Beta Gamma I II III IV V',
                   'Reflector': 'A B C D',
                   'Rings': '',
                   'Positions': '',
                   'Plugboard': ''}

newbombe=Bombe('CMFSUPKNCBMUYEQVVDYKLRQZTPUFHSWWAKTUGXMPAMYAFITXIJKMH','UNIVERSITY',knownsettings,permittedsettings)
#print(newbombe.solve())


#Code 3

knownsettings={'Rotors': 'x x x',
                   'Reflector': 'x',
                   'Rings': 'x x x',
                   'Positions': 'E M Y',
                   'Plugboard': 'FH TS BE UQ KD AL'}

permittedsettings={'Rotors': 'Beta Gamma II IV',
                   'Reflector': 'A B C D',
                   'Rings': '00 02 04 06 08 20 22 24 26',
                   'Positions': '',
                   'Plugboard': ''}

newbombe=Bombe('ABSKJAKKMRITTNYURBJFWQGRSGNNYJSDRYLAPQWIAGKJYEPCTAGDCTHLCDRZRFZHKNRSDLNPFPEBVESHPY','THOUSANDS',knownsettings,permittedsettings)
#code3=newbombe.solve()

#Code 4

knownsettings={'Rotors': 'V III IV',
                   'Reflector': 'A',
                   'Rings': '24 12 10',
                   'Positions': 'S W U',
                   'Plugboard': 'WP RJ Ax VF Ix HN CG BS'}

permittedsettings={'Rotors': 'Beta Gamma I II III IV V',
                   'Reflector': 'A B C D',
                   'Rings': '',
                   'Positions': '',
                   'Plugboard': ''}

newbombe=Bombe('SDNTVTPHRBNWTLMZTQKZGADDQYPFNHBPNHCQGBGMZPZLUAVGDQVYRBFYYEIXQWVTHXGNW','MAKINGOFTHESEEXAMPLES',knownsettings,permittedsettings)
#print(newbombe.solve())

#Code 5

knownsettings={'Rotors': 'V II IV',
                   'Reflector': 'D',
                   'Rings': '06 18 07',
                   'Positions': 'A J L',
                   'Plugboard': 'UG IE PO NX WT'}

permittedsettings={'Rotors': 'Beta Gamma I II III IV V',
                   'Reflector': 'A B C D',
                   'Rings': '',
                   'Positions': '',
                   'Plugboard': ''}

newbombe=Bombe('HWREISXLGTTBYVXRCWWJAKZDTVZWKBDJPVQYNEQIOTIFX','INSTAGRAM',knownsettings,permittedsettings)
#print(newbombe.solve())
