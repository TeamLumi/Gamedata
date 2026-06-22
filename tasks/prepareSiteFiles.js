const TrainerNames = require('../input/english_dp_trainers_name.json').labelDataArray.map(basicFileHandler);
const TrainerTypes = require('../input/english_dp_trainers_type.json').labelDataArray.map(basicFileHandler);
const ItemNames = require('../input/english_ss_itemname.json').labelDataArray.map(basicFileHandler);
const PokemonNames = require('../input/english_ss_monsname.json').labelDataArray.map(basicFileHandler);
const PokedexWords = require('../input/english_ss_pokedex.json').labelDataArray.map(basicFileHandler);
const Natures = require('../input/english_ss_seikaku.json').labelDataArray.map(basicFileHandler);
const Abilities = require('../input/english_ss_tokusei.json').labelDataArray.map(basicFileHandler);
const Types = require('../input/english_ss_typename.json').labelDataArray.map(basicFileHandler);
const MoveInfo = require('../input/english_ss_wazainfo.json').labelDataArray.map(basicFileHandler);
const MoveNames = require('../input/english_ss_wazaname.json').labelDataArray.map(basicFileHandler);
const FormNames = require('../input/english_ss_zkn_form.json').labelDataArray.map(basicFileHandler);
const PokemonHeight = require('../input/english_ss_zkn_height.json').labelDataArray.map(basicFileHandler);
const FormType = require('../input/english_ss_zkn_type.json').labelDataArray.map(basicFileHandler);
const PokemonWeight = require('../input/english_ss_zkn_weight.json').labelDataArray.map(basicFileHandler);
const EvolveTable = require('../input/EvolveTable.json').Evolve;
const EncounterTable = require('../input/FieldEncountTable_d.json');
const ItemTable = require('../input/ItemTable.json');
const PersonalTable = require('../input/PersonalTable.json');
const EggLearnsetTable = require('../input/TamagoWazaTable.json').Data;
const TrainerTable = require('../input/TrainerTable.json');
const fs = require('fs');
const path = require('path');


const POKEMON_NAME_MAP = PersonalTable.Personal.reduce(createPokemonMap, {});
const POKEMON_NAME_LIST = Object.values(POKEMON_NAME_MAP);


function createPokemonMap(pokemonNameMap, currentPokemon) {
    try {
      const { id } = currentPokemon;
      if(id === 0) return pokemonNameMap;
      const baseFormName = PokemonNames[id]?.[1];
      
      if (typeof baseFormName === 'string' && baseFormName.length > 0) {
        pokemonNameMap[id] = baseFormName;
        return pokemonNameMap;
      }
  
      const alternateFormName = FormNames[id][1];
      if (typeof alternateFormName === 'string' && alternateFormName.length > 0) {
        pokemonNameMap[id] = alternateFormName;
        return pokemonNameMap;
      }
  
      pokemonNameMap[id] = getFormNameOfProblematicPokemon(id);
      return pokemonNameMap;
    } catch (e) {
      throw Error(`${currentPokemon.id} - ${e}`);
    }
  }

  function getFormNameOfProblematicPokemon(id = 0) {
    switch (id) {
      case 1242:
        return 'Ash-Greninja';
      case 1285:
        return 'Meowstic-F';
      case 1310:
        return 'Rockruff Own-Tempo';
      case 1441:
        return 'Indeedee-F';
      case 1454:
        return 'Basculegion-F';
      case 1456:
        return 'Oinkologne-F';
      default:
        throw Error(`Bad Pokemon ID in PokemonNameMap: ${id}`);
    }
  }

function basicFileHandler(currentItem) {
    if(currentItem.labelName === "") return createDataObject("", "");
    return createDataObject(currentItem.labelName, currentItem.wordDataArray[0].str);
}

function createDataObject(labelName, data) {
    return [labelName, data];
}

function minifyItemObject(itemData) {
    const {no, type, iconid, price, bp_price, group_id, flags0} = itemData;
    return [
        no, type, iconid, price, bp_price, group_id, flags0
    ];
}

function minifyPersonalObject(p) {
    return Object.values(p);
}

function minifyTrainerTypeObject(t) {
    return {
        ID: t.TrainerID,
        Class: t.LabelTrType
    }
}

function minifyTrainerDataObject(t) {
    return {
        TypeID: t.TypeID,
        Name: t.NameLabel,
        money: t.Gold
    }
}

function minifyTrainerPartyObject(t) {
    let party = [];
   
    for(let i = 1; i < 7; i++) {
        if(t[`P${i}MonsNo`] === 0) continue;
        const mon = [
            t[`P${i}MonsNo`], t[`P${i}FormNo`], t[`P${i}Level`], t[`P${i}Sex`], t[`P${i}Seikaku`],
            t[`P${i}Tokusei`], t[`P${i}Waza1`], t[`P${i}Waza2`], t[`P${i}Waza3`], t[`P${i}Waza4`],
            t[`P${i}Item`], 
            t[`P${i}TalentHp`], t[`P${i}TalentAtk`], t[`P${i}TalentDef`],
            t[`P${i}TalentSpAtk`], t[`P${i}TalentSpDef`], t[`P${i}TalentAgi`], 
            t[`P${i}EffortHp`], t[`P${i}EffortAtk`], t[`P${i}EffortDef`],
            t[`P${i}EffortSpAtk`], t[`P${i}EffortSpDef`], t[`P${i}EffortAgi`]
        ];

        party.push(mon);
    }

    return party;
}

function minifyTrainerTable() {
    const t = {};
    t.TrainerType = TrainerTable.TrainerType.map(minifyTrainerTypeObject);
    t.TrainerData = TrainerTable.TrainerData.map(minifyTrainerDataObject).slice(0, 2000);
    t.TrainerPoke = TrainerTable.TrainerPoke.map(minifyTrainerPartyObject).slice(0, 2000);
    return t
}

function minifyItemTable() {
    const t = {};
    t.Item = ItemTable.Item.map(minifyItemObject);
    t.WazaMachine = t.WazaMachine
    return t;
}

function minifyPersonalTable() {
    return PersonalTable.Personal.map(minifyPersonalObject);
}

function writeToOutput(filename, data) {
    fs.writeFileSync(path.join(__dirname, '..', 'output', filename), JSON.stringify(data), 'utf-8');
}

function HoneyTreeData() {
    const const_regex = /const\s+int32_t\s+HONEY_TREES\[\s*NUM_ZONE_ID\s*\]\[\s*10\s*\]\s*=\s*\{\s*([\s\S]*?)\};/;
    const array_regex = /\[(.*?)\]\s*=\s*\{(.*?)\}/;

    const file = fs.readFileSync(path.join(__dirname, '..', 'input', 'honeywork.cpp'), 'utf-8');
    const data = file.toString();

    // Extract honey trees data
    const match = data.match(const_regex);
    if (match) {
        const values_str = match[1];
        const honey_trees = {};
        values_str.split("\n").forEach(line => {
            line = line.trim();
            if (!line) {
                return;
            }
            const submatch = line.match(array_regex);
            if (submatch) {
                const key = submatch[1];
                const values = submatch[2].split(",").map(v => v.trim());
                if (!values.includes("AMPHAROS")) {
                    honey_trees[key] = values;
                }
            }
        });
        return honey_trees;
    }
    throw Error(data)
}

const HONEY_ZONES = {
    "D02": 197,
    "D03": 199,
    "D04": 201,    
    "D13R0101": 253,
    "R206": 362,
    "R207": 364,
    "R205A": 359,
    "R205B": 361,
    "R208": 365,
    "R209": 367,
    "R210A": 373,
    "R210B": 375,
    "R211B": 378,
    "R212A": 379,
    "R212B": 383,
    "R213": 385,
    "R214": 392,
    "R215": 394,
    "R218": 400,
    "R221": 404,
    "R222": 407
}
function minifyHoneyData(input) {
    const honeyData = Object.entries(input);
    const getPokemonId = (s) => {
        const properName = capitalizeFirstLetter(s);
        const pokemonId = POKEMON_NAME_LIST.findIndex(e => e === properName)
        if(pokemonId === -1) throw Error(`bad Pokemon name: ${properName}, ${s}`)
        return pokemonId;
    }

    const minifiedData = [];
    for(let [zone, encounters] of honeyData) {
        let zoneId = HONEY_ZONES[zone];
        minifiedData.push([zoneId, encounters.map(getPokemonId)])
    }

    return minifiedData;
}

function capitalizeFirstLetter(string) {
    if(string === 'FARFETCHD') return "Farfetch’d"
    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}


writeToOutput('english_dp_trainers_name.json', TrainerNames);
writeToOutput('english_dp_trainers_type.json', TrainerTypes);
writeToOutput('english_ss_itemname.json', ItemNames);

writeToOutput('english_ss_monsname.json', PokemonNames);
writeToOutput('english_ss_pokedex.json', PokedexWords);
writeToOutput('english_ss_seikaku.json', Natures);

writeToOutput('english_ss_tokusei.json', Abilities);
writeToOutput('english_ss_typename.json', Types);
writeToOutput('english_ss_wazainfo.json', MoveInfo);

writeToOutput('english_ss_wazaname.json', MoveNames);
writeToOutput('english_ss_zkn_form.json', FormNames);
writeToOutput('english_ss_zkn_height.json', PokemonHeight);

writeToOutput('english_ss_zkn_type.json', FormType);
writeToOutput('english_ss_zkn_weight.json', PokemonWeight);
writeToOutput('EvolveTable.json', EvolveTable);

writeToOutput('FieldEncountTable_d.json', EncounterTable);
writeToOutput('TamagoWazaTable.json', EggLearnsetTable);
writeToOutput('EvolveTable.json', EvolveTable);

writeToOutput('TrainerTable.json', minifyTrainerTable());
writeToOutput('ItemTable.json', minifyItemTable());
writeToOutput('PersonalTable.json', minifyPersonalTable());

writeToOutput('HoneyData.json', minifyHoneyData(HoneyTreeData()));