import re # regex

class PokemonNode:
    def __init__(self, name):
        self.name = name
        self.count = 0
        self.teammates = []
        self.checks_counters = []

    def __str__(self):
        return self.name

    def get_num_teammates(self):
        return len(self.teammates)

    def get_teammates(self):
        return self.teammates
all_pokemon_dict = {}

def clean_padding(line):
    # x = re.search("\| (.*[^ ]) +\|", line) # it's the first group, but re doesn't seem to do group isolation

    # note: deleting spaces isn't clever if we ever want to parse spreads
    end_pad_match = re.search("[^ ] +\|", line)
    end_pad = end_pad_match.span()[0] + 1
    return line[3:end_pad]

def read_check_counter(f, barline):
    line = f.readline()
    if line == barline:
        return "fin", 0, 0, 0
    line = clean_padding(line)
    name_end = re.search(r" \d", line).start() -1
    counter_name = line[0 : name_end]
    # find the rating or the percentage or whatever
    line = f.readline()
    # do more stats with this line
    return counter_name, 0, 0, 0

def read_teammate(f, barline):
    line = f.readline()
    if line == barline:
        return "fin", 0
    line = clean_padding(line)
    name_end = re.search(r" \d", line).start()
    teammate_name = line[0 : name_end]
    teammate_freq = line[name_end+1 : name_end+5] # the next 4 chars
    # do more stats with this line
    return teammate_name, float(teammate_freq)


with open("gen9ou-1695.txt", "r") as f:
    active_pokemon = " "

    barline = f.readline() # the first line will tell us how wide the dividing line is
    line = f.readline() # should have first mon with some padding
    line = (clean_padding(line))
    active_pokemon = PokemonNode(line)
    all_pokemon_dict[line] = active_pokemon

    while(line):
        line = f.readline()
        if line == barline:     # every new category starts with a barline
            line = f.readline() # so we read the next

            if line == barline: # barline again means next mon
                pokemon_name = clean_padding(f.readline())
                active_pokemon = PokemonNode(pokemon_name)
                all_pokemon_dict[pokemon_name] = active_pokemon
            elif "Raw count" in line:
                raw_count = re.search("[0-9]+", line).group()
                active_pokemon.count = raw_count
            elif "Checks and Counters" in line: # parse some checks and counters
                cc_name = ""
                while cc_name != "fin":
                    pos = f.tell()
                    cc_name, rating, switch, ko = read_check_counter(f, barline)
                    #if cc_name != "fin":
                        # print(str(active_pokemon) + "<-- " + cc_name)
                f.seek(pos)
            elif "Teammates" in line: # parse some checks and counters
                teammate_name = ""
                while teammate_name != "fin":
                    pos = f.tell()
                    teammate_name, freq = read_teammate(f, barline)
                    if teammate_name != "fin":
                        # print(str(active_pokemon) + "<--> " + teammate_name)
                        active_pokemon.teammates.append((teammate_name, freq))
                f.seek(pos)

### now we do another round ###
#with open("gen9ou-1695.txt", "r") as f:
    #active_pokemon = " "
    #barline = f.readline() # the first line will tell us how wide the dividing line is
    #line = f.readline() # should have first mon with some padding
    #line = (clean_padding(line))

# print(all_pokemon_dict)


"""
for name, mon in all_pokemon_dict.items():
    print(mon)
    print(mon.getTeammates())
"""
#print (str(all_pokemon_dict["Dragapult"]))
#print (str(all_pokemon_dict["Araquanid"]))
print(all_pokemon_dict["Kingambit"].teammates)
