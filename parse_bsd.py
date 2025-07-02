import xml.etree.ElementTree as ET
import pandas as pd
import uuid
from collections import defaultdict

def parse_battlescribe_catalogue(xml_file_path):
    """Parse BattleScribe catalogue XML and extract data into normalized tables"""
    
    # Parse the XML
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    
    # Initialize data structures
    units_data = []
    weapons_data = []
    abilities_data = []
    unit_weapons_data = []
    unit_abilities_data = []
    
    # Extract namespace if present
    namespace = ''
    if root.tag.startswith('{'):
        namespace = root.tag.split('}')[0] + '}'
    
    def get_element_text(element, tag_name):
        """Helper to get element text, handling namespace"""
        elem = element.find(f"{namespace}{tag_name}")
        return elem.text if elem is not None else ""
    
    def get_element_attrib(element, attrib_name):
        """Helper to get element attribute"""
        return element.get(attrib_name, "")
    
    # Process all selectionEntry elements (units)
    for entry in root.findall(f".//{namespace}selectionEntry[@type='unit']"):
        unit_id = get_element_attrib(entry, 'id')
        unit_name = get_element_attrib(entry, 'name')
        
        # Extract unit profiles (stats)
        profiles = entry.findall(f".//{namespace}profile[@typeName='Unit']")
        
        for profile in profiles:
            profile_name = get_element_attrib(profile, 'name')
            
            # Extract characteristics (M, T, SV, W, LD, OC)
            characteristics = {}
            for char in profile.findall(f".//{namespace}characteristic"):
                char_name = get_element_attrib(char, 'name')
                char_value = char.text if char.text else ""
                characteristics[char_name] = char_value
            
            # Add unit data
            unit_data = {
                'unit_id': unit_id,
                'unit_name': unit_name,
                'profile_name': profile_name,
                'movement': characteristics.get('M', ''),
                'toughness': characteristics.get('T', ''),
                'save': characteristics.get('SV', ''),
                'wounds': characteristics.get('W', ''),
                'leadership': characteristics.get('LD', ''),
                'objective_control': characteristics.get('OC', ''),
                'points_cost': ""
            }
            
            # Get points cost
            costs = entry.findall(f".//{namespace}cost[@name='pts']")
            if costs:
                unit_data['points_cost'] = get_element_attrib(costs[0], 'value')
            
            units_data.append(unit_data)
        
        # Extract weapons from this unit
        extract_weapons_from_unit(entry, unit_id, weapons_data, unit_weapons_data, namespace)
        
        # Extract abilities from this unit
        extract_abilities_from_unit(entry, unit_id, abilities_data, unit_abilities_data, namespace)
    
    # Create DataFrames
    units_df = pd.DataFrame(units_data)
    weapons_df = pd.DataFrame(weapons_data)
    abilities_df = pd.DataFrame(abilities_data)
    unit_weapons_df = pd.DataFrame(unit_weapons_data)
    unit_abilities_df = pd.DataFrame(unit_abilities_data)
    
    # Remove duplicates from weapons and abilities (keep unique weapons/abilities)
    weapons_df = weapons_df.drop_duplicates(subset=['weapon_name', 'weapon_type', 'range', 'attacks', 'skill', 'strength', 'ap', 'damage', 'keywords'])
    abilities_df = abilities_df.drop_duplicates(subset=['ability_name', 'description'])
    
    return {
        'units': units_df,
        'weapons': weapons_df,
        'abilities': abilities_df,
        'unit_weapons': unit_weapons_df,
        'unit_abilities': unit_abilities_df
    }

def extract_weapons_from_unit(unit_entry, unit_id, weapons_data, unit_weapons_data, namespace):
    """Extract all weapons from a unit entry"""
    
    # Find all weapon profiles (both ranged and melee)
    ranged_weapons = unit_entry.findall(f".//{namespace}profile[@typeName='Ranged Weapons']")
    melee_weapons = unit_entry.findall(f".//{namespace}profile[@typeName='Melee Weapons']")
    
    all_weapons = [(w, 'Ranged') for w in ranged_weapons] + [(w, 'Melee') for w in melee_weapons]
    
    for weapon_profile, weapon_type in all_weapons:
        weapon_name = weapon_profile.get('name', '')
        weapon_id = weapon_profile.get('id', str(uuid.uuid4()))
        
        # Extract weapon characteristics
        characteristics = {}
        for char in weapon_profile.findall(f".//{namespace}characteristic"):
            char_name = char.get('name', '')
            char_value = char.text if char.text else ""
            characteristics[char_name] = char_value
        
        # Create weapon data entry
        weapon_data = {
            'weapon_id': weapon_id,
            'weapon_name': weapon_name,
            'weapon_type': weapon_type,
            'range': characteristics.get('Range', ''),
            'attacks': characteristics.get('A', ''),
            'skill': characteristics.get('WS' if weapon_type == 'Melee' else 'BS', ''),
            'strength': characteristics.get('S', ''),
            'ap': characteristics.get('AP', ''),
            'damage': characteristics.get('D', ''),
            'keywords': characteristics.get('Keywords', '')
        }
        
        weapons_data.append(weapon_data)
        
        # Create unit-weapon relationship
        unit_weapons_data.append({
            'unit_id': unit_id,
            'weapon_id': weapon_id,
            'weapon_name': weapon_name
        })

def extract_abilities_from_unit(unit_entry, unit_id, abilities_data, unit_abilities_data, namespace):
    """Extract all abilities from a unit entry"""
    
    # Find all ability profiles
    ability_profiles = unit_entry.findall(f".//{namespace}profile[@typeName='Abilities']")
    
    for ability_profile in ability_profiles:
        ability_name = ability_profile.get('name', '')
        ability_id = ability_profile.get('id', str(uuid.uuid4()))
        
        # Extract ability description
        description = ""
        desc_char = ability_profile.find(f".//{namespace}characteristic[@name='Description']")
        if desc_char is not None:
            description = desc_char.text if desc_char.text else ""
        
        # Create ability data entry
        ability_data = {
            'ability_id': ability_id,
            'ability_name': ability_name,
            'description': description
        }
        
        abilities_data.append(ability_data)
        
        # Create unit-ability relationship
        unit_abilities_data.append({
            'unit_id': unit_id,
            'ability_id': ability_id,
            'ability_name': ability_name
        })

def save_to_excel(dataframes_dict, output_file):
    """Save all dataframes to separate Excel sheets"""
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Data saved to {output_file}")

def print_summary(dataframes_dict):
    """Print a summary of the extracted data"""
    print("\n=== DATA EXTRACTION SUMMARY ===")
    for table_name, df in dataframes_dict.items():
        print(f"{table_name.upper()}: {len(df)} records")
        if not df.empty:
            print(f"  Columns: {', '.join(df.columns)}")
        print()

# Example usage
if __name__ == "__main__":
    # Parse the catalogue file
    xml_file_path = "your_catalogue_file.cat"  # Replace with your file path
    
    try:
        # Extract data
        data_tables = parse_battlescribe_catalogue(xml_file_path)
        
        # Print summary
        print_summary(data_tables)
        
        # Save to Excel file
        save_to_excel(data_tables, "battlescribe_database.xlsx")
        
        # Display sample data
        print("=== SAMPLE DATA ===")
        for table_name, df in data_tables.items():
            print(f"\n{table_name.upper()} (first 3 rows):")
            print(df.head(3).to_string(index=False))
            
    except Exception as e:
        print(f"Error processing file: {e}")
