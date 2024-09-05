import re # regex
import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image
import mplcursors
import requests
from io import BytesIO
import pygraphviz

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
    name_end = re.search(r" +\d", line).start()
    name_end = re.search(r" +\d", line).start()
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
                        if teammate_name not in all_pokemon_dict:
                            all_pokemon_dict[teammate_name] = PokemonNode(teammate_name)
                f.seek(pos)
###
### now we do another round ###
#with open("gen9ou-1695.txt", "r") as f:
    #active_pokemon = " "
    #barline = f.readline() # the first line will tell us how wide the dividing line is
    #line = f.readline() # should have first mon with some padding
    #line = (clean_padding(line))

# print(all_pokemon_dict)

spritesFolder = 'https://play.pokemonshowdown.com/sprites/dex/'
# Function to get an image from a URL
def get_image_from_url(url):
    response = requests.get(url)
    img_data = BytesIO(response.content)  # Convert the response content to a BytesIO object
    return Image.open(img_data)  # Open the image using PIL

monlist = []
for name, mon in all_pokemon_dict.items():
    monlist.append(name)

# Create a graph and add nodes
G = nx.Graph()

G.add_nodes_from(monlist)
# Create a shell layout with explicit node names in nlist
nlist = []
for mon in monlist:
        nlist.append([mon])  # Ensure both nodes are included in nlist
# Generate the shell layout positions for the nodes


for name, mon in all_pokemon_dict.items():
    for teammate in mon.get_teammates():
        G.add_edge(name, teammate[0], weight=0.1)


edges = G.edges(data=True)
edge_weights = [d['weight'] for (u, v, d) in edges]



# Draw the graph with weighted edges
nx.draw_shell(G, nlist=nlist, node_color='none', with_labels=False)
pos = nx.nx_agraph.pygraphviz_layout(G)
nx.draw_networkx_edges(G, pos)



for mon in monlist:
    url = spritesFolder + mon.replace(' ', '').lower() + '.png'  # Replace with the actual URL of the image
    try:
        img = get_image_from_url(url)
    except:
        img = get_image_from_url('https://play.pokemonshowdown.com/sprites/itemicons/0.png')
    img = OffsetImage(img, zoom=0.1)  # Adjust the zoom to fit the node size
    if mon in pos:  # Ensure the node has a position
        node_pos = pos[mon]
        ab = AnnotationBbox(img, (node_pos[0], node_pos[1]), frameon=False)
        ax = plt.gca()
        ax.add_artist(ab)

# Load and add the image for 'Kingambit' from a URL

# Adding hover functionality to display labels on hover

labels = {node: node for node in G.nodes()}  # Create a label dictionary
print(labels)
nodes = [plt.scatter(*pos[node], alpha=0) for node in G.nodes()]  # Invisible node markers

# Use mplcursors to display node labels on hover
cursor = mplcursors.cursor(nodes, hover=True)

@cursor.connect("add")
def on_add(sel):
    node = list(G.nodes)[sel.target.index]
    sel.annotation.set_text(labels[node])

# Display the plot
plt.show()

