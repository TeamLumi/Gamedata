import sys

## All that needs to change to change modes is this INPUT_NAME
## If you are using 3.0 files, change it to "3.0Input"
## Otherwise just set it to "input"
if len(sys.argv) > 1:
    if sys.argv[1] == "3.0":
        INPUT_NAME = "3.0Input"
        print("Running in 3.0 mode")
    elif sys.argv[1] == "2.0":
        INPUT_NAME = "input"
        print("Running in 2.0F mode")
else:
    INPUT_NAME = "input"

if INPUT_NAME == "input":
    GAME_MODE = "2.0"
    DEBUG_NAME = "Debug"
    OUTPUT_NAME = "output"
    POKEDEX_LENGTH = 1010
    NAT_DEX_LENGTH = 1455
    TROUBLE_MONS_NAMES = { 
        1242: 'Ash-Greninja',
        1285: 'Meowstic-F',
        1310: 'Rockruff Own-Tempo',
        1441: 'Indeedee-F',
        1454: 'Basculegion-F',
        1456: 'Oinkologne-F',
        1067: "Galarian Farfetch'd"
    }
elif INPUT_NAME == "3.0Input":
    GAME_MODE = "3.0"
    DEBUG_NAME = "3.0Debug"
    OUTPUT_NAME = "3.0Output"
    POKEDEX_LENGTH = 1025
    NAT_DEX_LENGTH = 1528
    TROUBLE_MONS_NAMES = { 
        1266: 'Ash-Greninja',
        1309: 'Meowstic-F',
        1335: 'Rockruff Own-Tempo',
        1466: 'Indeedee-F',
        1481: 'Basculegion-F',
        1483: 'Oinkologne-F',
        1083: "Galarian Farfetch'd"
    }

TRAINER_BATTLE = '_TRAINER_BTL_SET'
MULTI_TRAINER_BATTLE = '_TRAINER_MULTI_BTL_SET'
GYM_AREA_NAME = "GYM"
E4_AREA_NAME = "C10"
ROOM_AREA_NAME = "R0101"
PEARL_SPEAR_PILLAR = "d05r0115"
EVE_AREA_NAME = "SODATEYA"
MORIMOTO = "MORIMOTO_01"
SUPPORT_AREA_NAME = "SUPPORT"
SHINING_PEARL_FILE_PREFIX = "SP_"

# Gym Leader lookup based on the file name
GYM_LEADER_LOOKUP = {
    "c03gym0101":"roark",
    "c04gym0102":"gardenia",
    "c05gym0113":"fantina",
    "c07gym0101":"maylene",
    "c06gym0101":"wake",
    "c02gym0101":"byron",
    "c09gym0101":"candice",
    "c08gym0103":"volkner",
    "c10r0111":"cynthia",
    "c10r0109":"lucian",
    "c10r0107":"flint",
    "c10r0105":"bertha",
    "c10r0103":"aaron",
}

# Formats for the different battles
SINGLE_FORMAT = "Single Battle"
DOUBLE_FORMAT = "Double Battle"
MULTI_FORMAT = "Multi Battle Enemy"
MULTI_PARTNER_FORMAT = "Multi Battle Partner"
EVIL_TYPE = "Evil"

# Needed to hard code Wurmple's and Goomy's target evos
WURMPLE = 265
SILCOON = 266
CASCOON = 268
GOOMY = 704
SLIGGOO = 705
HISUI_SLIGGOO = 1287

# Tracker Variables
GALACTIC_HQ = "Galactic HQ"
GALACTIC_HQ_TRACKER_VAR = "lmpt-33"
LEAGUE = 'Pokemon League'
LEAGUE_TRACKER_VAR = 'lmpt-61'
RENEGADE = "Renegade Park"
RENEGADE_TRACKER_VAR = "lmpt-45" #This is Route 221 since there are no encounters in Renegade Park
DISTORTION = "Distortion Room"
DISTORTION_TRACKER_VAR = 'lmpt-56' #This is for Spear Pillar bc no encounters in Distortion Room
TROPHY_GARDEN_NAME = 'urayama'
TROPHY_GARDEN_TRACKER_VAR = 'lmpt-39'
TG_ETERNA_BUILDING = 'T.G. Eterna Bldg'
TG_ETERNA_BUILDING_TRACKER_VAR = 'lmpt-19'
POKEMON_LEAGUE = "Pokémon League"
POKEMON_LEAGUE_TRACKER_VAR = 'lmpt-61'
TRAINER_SCHOOL = 'Trainers\u2019 School'
TRAINER_SCHOOL_TRACKER_VAR = 'lmpt-7'
MANSION = "Pokémon Mansion"
MANSION_TRACKER_VAR = "lmpt-65"
TRACKER_VARS = {
    GALACTIC_HQ: GALACTIC_HQ_TRACKER_VAR,
    LEAGUE: LEAGUE_TRACKER_VAR,
    RENEGADE: RENEGADE_TRACKER_VAR,
    DISTORTION: DISTORTION_TRACKER_VAR,
    TG_ETERNA_BUILDING: TG_ETERNA_BUILDING_TRACKER_VAR,
    POKEMON_LEAGUE: POKEMON_LEAGUE_TRACKER_VAR,
    TRAINER_SCHOOL: TRAINER_SCHOOL_TRACKER_VAR,
    MANSION: MANSION_TRACKER_VAR,
}

EGG_GROUPS = {
    0: "None",
    1: "Monster",
    2: "Water 1",
    3: "Bug",
    4: "Flying",
    5: "Field",
    6: "Fairy",
    7: "Grass",
    8: "Human-Like",
    9: "Water 3",
    10: "Mineral",
    11: "Amorphous",
    12: "Water 2",
    13: "Ditto",
    14: "Dragon",
    15: "No Eggs",
}

BAD_ENCOUNTER_LIST = ["Gigantamax", "Eternamax", "Mega ", "Totem "]
STARTERS = ["piplup", "turtwig", "chimchar"]
MASTER_TRAINER_TYPES = ["fire", "water", "electric", "grass", "ice", "fighting", "poison", "ground", "flying", "psychic", "bug", "rock", "ghost", "dragon", "dark", "steel", "fairy"]
CELEBI = "Celebi"
AMPHAROS_PLACE_HOLDER = "AMPHAROS"
WRONG_FARFETCHD = "FARFETCHD"
RIGHT_FARFETCHD = "Farfetch\u2019d"

PLACE_DATA_METHOD = "Place Data"
SCRIPTED_METHOD = "Scripted"
TRACKER_METHOD = "Tracker"
E4_METHOD = "Elite Four Trainers"
DOCS_METHOD = "Docs"

GENDER = {"0": "MALE", "1": "FEMALE", "2": "NEUTRAL"}
MALE = "male"
FEMALE = "female"

MASTER_TRAINER = "Master"
ROUTE_224 = "R224"
ROUTE_210 = "R210B"
BAD_SUPPORT_LOOKUP1 = "ev_r207_func_17" ### These bad lookups are for Lucas and Dawn on Route 207
BAD_SUPPORT_LOOKUP2 = "ev_r207_func_20"
R224_BAD_SUPPORT_LOOKUP1 = "ev_r224_support_dawn_battle_party"
R224_BAD_SUPPORT_LOOKUP2 = "ev_r224_support_lucas_battle_party"
R210B_BAD_SUPPORT_LOOKUP1 = "ev_r210b_support_set_dawn_party_1"
R210B_BAD_SUPPORT_LOOKUP2 = "ev_r210b_support_set_lucas_party_1"

SUPPORT_LINK = "Support"
CITY_TRAINER = 'City'
LEAGUE_TRAINER = "League"

#Lookup values for ev_script
LDVAL_LOOKUP = "LDVAL"
MASTER_TRAINER_LOOKUP = "_LDVAL(@SCWK_PARAM1"
CELEBI_LOOKUP = "_LDVAL(@CON_TEMP05"
EVIL_LOOKUP = "LDVAL(@SCWK_TEMP"

REMATCH_SUBSTRING = "rematch"
DESIRED_ORDER = [ 'areaName', 'zoneName', 'zoneId', 'trainerId', 'rematch', 'name', 'type', 'method', 'format', 'link' ]
BARRY = "barry"
CEDRIC = "Cedric"
REPEAT_TRAINERS_LIST = ["Grunt", "Lucas", "Dawn", "Barry"]

TEAM_REGEX = "Team \d+"
LDVAL_PATTERN = r"_LDVAL\(@(.*),\s?([1-9][0-9]*)\)"
TRAINER_PATTERN = r"_TRAINER_BTL_SET\s*\(\s*('?[^']+'?|@\w+|\d+)\s*,\s*('?[^']+'?|@\w+|\d+)\s*\)"
MULTI_TRAINER_PATTERN = r"_TRAINER_MULTI_BTL_SET\s*\(\s*((?:'[^']*'|@\w+|\d+)\s*(?:,\s*(?:'[^']*'|@\w+|\d+)\s*)*)\)"
HONEY_TREE_MATCH_REGEX = r"\[(.*?)\]\s*=\s*\{(.*?)\}"
HONEY_TREE_CONST_REGEX = r"const\s+int32_t\s+HONEY_TREES\[\s*NUM_ZONE_ID\s*\]\[\s*10\s*\]\s*=\s*\{\s*([\s\S]*?)\};"
HONEY_TREE = "Honey Tree"
TROPHY_GARDEN = "Daily Trophy Garden"
TROPHY_GARDEN_RATE = "5%"
TROPHY_GARDEN_LEVEL = 26

SURFING_INCENSE = "Surfing Incense"
INCENSE = "Incense"
SWARM = "tairyo"
RADAR = "swayGrass"
REGULAR_ENC = "ground_mons"
DAY_ENC = "day"
NIGHT_ENC = "night"
SURF_ENC = "water_mons"
OLD_ENC = "boro_mons"
GOOD_ENC = "ii_mons"
SUPER_ENC = "sugoi_mons"
REGULAR_ENC_LIST = [REGULAR_ENC, DAY_ENC, NIGHT_ENC]
ROD_ENC_LIST = [OLD_ENC, GOOD_ENC, SUPER_ENC]
INCENSE_LIST = ["gbaRuby", "gbaSapp", "gbaEme", "gbaFire", "gbaLeaf"]

OG_TOP_10 = ["Magikarp", "Gyarados", "Golbat", "Graveler", "Tentacruel", "Nosepass","Steelix","Golduck","Lunatone","Solrock"]
NEW_TOP_10 = ["Golbat", 54, 
              "Magikarp", 50, 
              "Gyarados", 49, 
              "Haunter", 35, 
              "Lunatone", 33,
              "Solrock", 33,
              "Chimecho", 32,
              "Graveler", 28,
              "Dusclops", 27,
              "Bronzong", 27,
              ]

ZONE_ORDER = [
    "Route 201",
    "Lake Verity (Before)",
    "Route 202",
    "Jubilife City",
    "Route 204 South",
    "Route 203",
    "Oreburgh Gate 1F",
    "Oreburgh Gate B1F",
    "Oreburgh City",
    "Oreburgh Mine",
    "Oreburgh Mine B1F",
    "Oreburgh Gym",
    "Route 204 North",
    "Floaroma Town",
    "Floaroma Meadow",
    "Valley Windworks",
    "Route 205 South",
    "Eterna Forest",
    "Eterna Forest (Cut Tree Path)",
    "Route 205 North",
    "Route 211 West",
    "Route 211 East",
    "Route 216",
    "Route 206",
    "Eterna Gym",
    "Eterna City",
    "Route 207",
    "Wayward Cave",
    "Route 208",
    "Hearthome City",
    "Amity Square",
    "Hearthome Gym",
    "Route 212 North",
    "Route 209",
    "Lost Tower",
    "Lost Tower 1F",
    "Lost Tower 2F",
    "Lost Tower 3F",
    "Lost Tower 4F",
    "Lost Tower 5F",
    "Solaceon Town",
    "Solaceon Ruins",
    "Route 210 South",
    "Route 215",
    "Veilstone Gym",
    "Veilstone City",
    "Route 214",
    "Seven Starts Restaurant",
    "Route 213",
    "Route 212 South",
    "Pastoria City",
    "Pastoria Gym",
    "Route 210 North",
    "Celestic Town",
    "Route 218",
    "Fuego Ironworks (Outside)",
    "Fuego Ironworks (Inside)",
    "Route 219",
    "Route 220",
    "Route 221",
    "Ramanas Park",
    "Canalave City",
    "Iron Island (Outside)",
    "Iron Island 1F",
    "Iron Island B1F Left Cave",
    "Iron Island B1F Right Cave",
    "Iron Island B2F Left Cave",
    "Iron Island B3F Right Cave",
    "Iron Island B3F",
    "Canalave Gym",
    "Valor Lakefront",
    "Lake Valor (Before)",
    "Valor Cavern",
    "Lake Verity (After)",    
    "Route 217",
    "Snowpoint City",
    "Snowpoint Gym",
    "Galactic HQ",
    "Team Galactic HQ 1F",
    "Team Galactic HQ 2F",
    "Team Galactic HQ 3F",
    "Team Galactic HQ 4F",
    "Team Galactic HQ B1F",
    "Team Galactic HQ B2F",
    "Mt. Coronet 3F",
    "Mt. Coronet 4F",
    "Mt. Coronet Route 211 Entrance",
    "Mt. Coronet 6F",
    "Mt. Coronet 7F",
    "Mt. Coronet Summit",
    "Spear Pillar",
    "Distortion Room",
    "Route 222",
    "Sunyshore City",
    "Sunyshore Gym",
    "Route 223",
    "Route 224",
    "Victory Road 1F",
    "Victory Road 2F",
    "Victory Road B1F",
    "Victory Road 1F Back 1",
    "Victory Road 1F Back 2",
    "Victory Road 1F Back 3",
    "Pokemon League",
    "Fight Area",
    "Route 225",
    "Route 226",
    "Route 227",
    "Route 228",
    "Route 229",
    "Route 230",
    "Stark Mountain (Outside)",
    "Stark Mountain (Entrance)",
    "Stark Mountain (Interior)",
    "Sandgem Town",
]

DOCS_ZONE_ORDER = [
    "Twinleaf Town",
    "Route 201",
    "Lake Verity (Before)",
    "Route 202",
    "Jubilife City",
    "Route 204 (South)",
    "Ravaged Path",
    "Route 203",
    "Oreburgh Gate - 1F",
    "Oreburgh Gate - B1F",
    "Oreburgh City",
    "Oreburgh Mine B1F",
    "Oreburgh Mine B2F",
    "Oreburgh - Gym",
    "Route 204 (North)",
    "Floaroma Town",
    "Valley Windworks (Outside)",
    "Floaroma Meadow",
    "Valley Windworks (Inside)",
    "Route 205 (South)",
    "Eterna Forest",
    "Eterna Forest (Overworld)",
    "Old Chateau - Lobby",
    "Old Chateau - Dining Room",
    "Old Chateau - 2F Small Rooms",
    "Old Chateau - 2F Hallway",
    "Old Chateau - Hallway Room 1",
    "Old Chateau - Hallway Room 2",
    "Old Chateau - Hallway Room 3",
    "Old Chateau - Hallway Room 4",
    "Old Chateau - Hallway Room 5",
    "Route 205 (North)",
    "Eterna City",
    "Route 211 (West)",
    "Mt. Coronet - Route 211 Entrance",
    "Route 211 (East)",
    "Mt. Coronet - Tunnel to Route 211 Entrance",
    "Mt. Coronet - B1F",
    "Mt. Coronet - Route 216 Entrance",
    "Route 216",
    "Eterna - Gym Main Room",
    "T.G. Building 1F",
    "T.G. Building 2F",
    "T.G. Building 3F",
    "T.G. Building 4F",
    "Route 206",
    "Route 207",
    "Wayward Cave - Main Area",
    "Wayward Cave - Secret Area",
    "Mt. Coronet - Route 207 Entrance",
    "Route 208",
    "Hearthome City",
    "Amity Square",
    "Hearthome - Gym Lobby",
    "Hearthome - Gym Trainer Room 1",
    "Hearthome - Gym Trainer Room 2",
    "Hearthome - Gym Question 2",
    "Hearthome - Gym Trainer Room 3",
    "Hearthome - Gym Question 3",
    "Hearthome - Gym Trainer Room 4",
    "Hearthome - Gym Question 4",
    "Hearthome - Gym Trainer Room 5",
    "Hearthome - Gym Trainer Room 6",
    "Hearthome - Gym Trainer Room 7",
    "Hearthome - Gym Trainer Room 8",
    "Hearthome - Gym Leader Room",
    "Route 212 (North)",
    "Pokémon Mansion - Lobby",
    "Pokémon Mansion - Rooms (Left)",
    "Pokémon Mansion - Backlot Room",
    "Trophy Garden",
    "Route 209",
    "Lost Tower - 1F",
    "Lost Tower - 2F",
    "Lost Tower - 3F",
    "Lost Tower - 4F",
    "Lost Tower - 5F",
    "Solaceon Town",
    "Solaceon Ruins - 2F",
    "Solaceon Ruins - 1F",
    "Solaceon Ruins - F Room Dead End (NE)",
    "Solaceon Ruins - 1F Dead End (NW)",
    "Solaceon Ruins - F Room",
    "Solaceon Ruins - 1F Dead End (SE)",
    "Solaceon Ruins - R Room",
    "Solaceon Ruins - F Room Dead End (SE)",
    "Solaceon Ruins - N Room Dead End (SE)",
    "Solaceon Ruins - E Room Dead End (SW)",
    "Solaceon Ruins - R Room Dead End (NW)",
    "Solaceon Ruins - R Room Dead End (SW)",
    "Solaceon Ruins - I Room",
    "Solaceon Ruins - N Room",
    "Solaceon Ruins - E Room",
    "Solaceon Ruins - D Room",
    "Solaceon Ruins - I Room Dead End (SE)",
    "Solaceon Ruins - N Room Dead End (NW)",
    "Solaceon Ruins - E Room Dead End (SE)",
    "Route 210 (South)",
    "Route 210 - Café Cabin",
    "Route 215",
    "Veilstone - Gym",
    "Veilstone City",
    "Route 214",
    "Ruin Maniac Cave - Small",
    "Ruin Maniac Cave - Large",
    "Maniac Tunnel",
    "Valor Lakefront",
    "Route 213",
    "Pastoria City",
    "Great Marsh - Area 1",
    "Great Marsh - Area 2",
    "Great Marsh - Area 3",
    "Great Marsh - Area 4",
    "Great Marsh - Area 5",
    "Great Marsh - Area 6",
    "Route 212 (South)",
    "Pastoria - Gym",
    "Route 210 (North)",
    "Celestic Town",
    "Route 219",
    "Route 220",
    "Route 221",
    "Ramanas Park",
    "Route 218",
    "Fuego Ironworks (Outside)",
    "Fuego Ironworks (Inside)",
    "Canalave City",
    "Iron Island (Overworld)",
    "Iron Island - 1F",
    "Iron Island - B1F Left",
    "Iron Island - B1F Right",
    "Iron Island - B2F Left (Riley's Room)",
    "Iron Island - B2F Right",
    "Iron Island - B3F",
    "Iron Island - B3F Right",
    "Canalave - Gym",
    "Valor Lakefront",
    "Valor Lakefront - Restaurant",
    "Lake Valor (Before)",
    "Valor Cavern",
    "Lake Verity (After)",
    "Route 217",
    "Snowpoint City",
    "Snowpoint - Gym",
    "Galactic HQ",
    "Team Galactic HQ - 1F",
    "Team Galactic HQ - 2F",
    "Team Galactic HQ - 3F",
    "Team Galactic HQ - 4F",
    "Team Galactic HQ - B1F",
    "Team Galactic HQ - B2F",
    "Team Galactic HQ - Lake Trio Room",
    "Acuity Lakefront",
    "Snowpoint Temple - 1F",
    "Snowpoint Temple - B1F",
    "Snowpoint Temple - B2F",
    "Snowpoint Temple - B3F",
    "Snowpoint Temple - B4F",
    "Snowpoint Temple - B5F",
    "Lake Acuity (After)",
    "Mt. Coronet - 2F",
    "Mt. Coronet - 3F",
    "Mt. Coronet - Snow Area",
    "Mt. Coronet - 4F (Waterfall)",
    "Mt. Coronet - 4F (Towards Spear Pillar)",
    "Mt. Coronet - Summit",
    "Mt. Coronet - 5F",
    "Mt. Coronet - 6F",
    "Spear Pillar",
    "Sendoff Spring",
    "Lake Valor (After)",
    "Turnback Cave - Entrance",
    "Route 222",
    "Route 222 - House 1 (Left)",
    "Sunyshore City",
    "Sunyshore - Gym",
    "Sunyshore - Gym Room 1",
    "Sunyshore - Gym Room 2",
    "Sunyshore - Gym Room 3",
    "Route 223",
    "Victory Road - 1F",
    "Victory Road - 2F",
    "Victory Road - B1F",
    "Victory Road - 1F Back (Marley)",
    "Victory Road - 1F Back (Entrance)",
    "Victory Road - 1F Back (214 Exit)",
    "Pokemon League",
    "Fight Area",
    "Route 224",
    "Turnback Cave - d17r0103",
    "Turnback Cave - d17r0104",
    "Turnback Cave - d17r0105",
    "Turnback Cave - d17r0106",
    "Turnback Cave - d17r0107",
    "Turnback Cave - d17r0108",
    "Turnback Cave - d17r0109",
    "Turnback Cave - d17r0110",
    "Turnback Cave - d17r0111",
    "Turnback Cave - d17r0112",
    "Turnback Cave - d17r0113",
    "Turnback Cave - d17r0114",
    "Turnback Cave - d17r0115",
    "Turnback Cave - d17r0116",
    "Turnback Cave - d17r0117",
    "Turnback Cave - d17r0118",
    "Turnback Cave - d17r0119",
    "Turnback Cave - d17r0120",
    "Turnback Cave - d17r0121",
    "Turnback Cave - d17r0122",
    "Route 225",
    "Route 226",
    "Route 227",
    "Route 228",
    "Route 229",
    "Resort Area",
    "Route 230",
    "Stark Mountain (Overworld)",
    "Stark Mountain - Entrance",
    "Stark Mountain - Interior",
    "Sandgem Town",
]

# This will make sure that defined locations in the mapper won't get grouped together incorrectly
EXCLUSIVE_ZONE_IDS = [
    0, # Jubilife City
    355, # Route 202
    429, # Sandgem Town
    346, # Verity Lakefront
    326, # Lake Verity Cavern
    328, # Lake Valor Cavern
    331, # Lake Acuity Cavern
    265, # Turnback Cave
    211, # Mt. Coronet 6F
    216, # Spear Pillar
    624, # Distortion Room
    354, # Route 201
    422, # Twinleaf Town
    323, # Lake Verity
    400, # Route 218
    24, # Canalave City
    446, # Solaceon Town
    225, # Solaceon Ruins
    368, # Lost Tower
    367, # Route 209
    252, # Ravaged Path
    358, # Route 204 (North)
    357, # Route 204 (South)
    438, # Floaroma Town
    253, # Floaroma Meadow
    201, # Fuego Ironworks (Outside)
    202, # Fuego Ironworks (Inside)
    359, # Route 205 South
    361, # Route 205 North
    197, # Valley Windworks (Outside)
    198, # Valley Windworks (Inside)
    200, # Eterna Forest
    199, # Eterna Forest (Outside)
    306, # Old Chateau (Lobby)
    307, # Old Chateau (Dining Room)
    308, # Old Chateau (2F Side Rooms)
    309, # Old Chateau (2F Hallway)
    310, # Old Chateau (Room 1 Hallway)
    311, # Old Chateau (Room 2 Hallway)
    312, # Old Chateau (Room 3 Hallway)
    313, # Old Chateau (Room 4 Hallway)
    314, # Old Chateau (Room 5 Hallway)
    54, # Eterna City
    62, # T.G. Building (1F)
    63, # T.G. Building (2F)
    64, # T.G. Building (3F)
    65, # T.G. Building (4F)
    362, # Route 206
    292, # Wayward Cave
    293, # Wayward Cave (Secret Area)
    364, # Route 207
    356, # Route 203
    255, # Oreburgh Gate (1F)
    256, # Oreburgh Gate (B1F)
    38, # Oreburgh City
    195, # Oreburgh Mine (B1F)
    196, # Oreburgh Mine (B2F)
    250, # Renegade Park
    404, # Route 221
    485, # Route 220
    403, # Route 219
    365, # Route 208
    74, # Hearthome City
    96, # Amity Square
    377, # Route 211 (West)
    379, # Route 212 (North)
    383, # Route 212 (South)
    380, # Pokémon Mansion
    205, # Mt. Coronet 3F
    204, # Mt. Coronet 2F
    203, # Mt. Coronet Route 207
    213, # Mt. Coronet 216 Entrance
    215, # Mt. Coronet B1F
    214, # Mt. Coronet 211 Entrance
    212, # Mt. Coronet Tunnel To 211 Entrance
    208, # Mt. Coronet 4F
    207, # Mt. Coronet Summit
    999, # Regice Ruins
    210, # Mt. Coronet 5F
    209, # Mt. Coronet 4F To Spear Pillar
    206, # Mt. Coronet Snow Area
    378, # Route 211 (East)
    456, # Celestic Town
    375, # Route 210 (North)
    373, # Route 210 (South)
    395, # Route 216
    397, # Route 217
    351, # Acuity Lakefront
    330, # Lake Acuity
    286, # Snowpoint Temple (1F)
    287, # Snowpoint Temple (B1F)
    288, # Snowpoint Temple (B2F)
    289, # Snowpoint Temple (B3F)
    290, # Snowpoint Temple (B4F)
    291, # Snowpoint Temple (B5F)
    159, # Snowpoint City
    394, # Route 215
    315, # T.G. H.Q. (1F)
    316, # T.G. H.Q. (2F)
    317, # T.G. H.Q. (3F)
    318, # T.G. H.Q. (4F)
    319, # T.G. H.Q. (B1F)
    320, # T.G. H.Q. (B2F)
    315, # T.G. H.Q. Lake Trio
    315, # T.G. H.Q. Hall To Lake Trio
    123, # Veilstone City
    392, # Route 214
    296, # Maniac Tunnel
    352, # Spring Path
    263, # Sendoff Spring
    998, # Distortion World
    327, # Lake Valor
    385, # Route 213
    347, # Valor Lakefront
    219, # The Great Marsh (Area 1-2)
    221, # The Great Marsh (Area 3-4)
    223, # The Great Marsh (Area 5-6)
    110, # Pastoria City
    407, # Route 222
    486, # Route 223
    142, # Sunyshore City
    169, # Pokémon League (Pre-Victory Road)
    411, # Route 224
    244, # Victory Road (1F)
    245, # Victory Road (2F)
    246, # Victory Road (B1F)
    247, # Victory Road (1F Back Marley)
    248, # Victory Road (1F Back Entrance)
    249, # Victory Road (1F Back 214 Exit)
    167, # Pokémon League (Outside)
    490, # Seabreak Path
    285, # Flower Paradise
    336, # Battle Tower
    186, # Fight Area
    412, # Route 225
    465, # Survival Area
    472, # Battle House
    487, # Route 226
    414, # Route 227
    416, # Route 228
    997, # Regirock Ruins
    420, # Route 229
    489, # Route 230
    473, # Resort Area
    259, # Stark Mountain (Outside)
    260, # Stark Mountain (Entrance)
    261, # Stark Mountain (Interior)
    262, # Stark Mountain (Heatran Room)
    996, # Registeel Ruins
    298, # Iron Island (Outside)
    299, # Iron Island (1F)
    300, # Iron Island (B1F Left)
    301, # Iron Island (B1F Right)
    302, # Iron Island (B2F Right)
    303, # Iron Island (B2F Left)
    304, # Iron Island (B3F)
    257, # Fullmoon Island
    332, # Newmoon Island
]