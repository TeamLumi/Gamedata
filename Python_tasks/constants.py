TRAINER_BATTLE = '_TRAINER_BTL_SET'
MULTI_TRAINER_BATTLE = '_TRAINER_MULTI_BTL_SET'
GYM_AREA_NAME = "GYM"
E4_AREA_NAME = "C10"
ROOM_AREA_NAME = "R0101"
SINGLE_FORMAT = "Single"
DOUBLE_FORMAT = "Double"

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

MULTI_FORMAT = "Multi"
EVIL_TYPE = "Evil"

GENDER = {"0": "MALE", "1": "FEMALE", "2": "NEUTRAL"}
MALE = "male"
FEMALE = "female"

MASTER_TRAINER = "Master"
BAD_SUPPORT_LOOKUP1 = "ev_r207_func_17" ### These bad lookups are for Lucas and Dawn on Route 207
BAD_SUPPORT_LOOKUP2 = "ev_r207_func_20"
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
REPEAT_TRAINERS_LIST = ["Grunt", "Lucas", "Dawn", "Cedric"]

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
REGULAR_ENC_LIST = [REGULAR_ENC, DAY_ENC, NIGHT_ENC]
INCENSE_LIST = ["gbaRuby", "gbaSapp", "gbaEme", "gbaFire", "gbaLeaf"]

EVE_AREA_NAME = "SODATEYA"
MORIMOTO = "MORIMOTO_01"
ZONE_ORDER = [
    "Route 201",
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
    "Hearthome Gym",
    "Hearthome City",
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
    "Lake Verity (Before)",
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
    "Victory Road Nat Dex Area",
    "Victory Road Nat Dex Area B1F",
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
]
