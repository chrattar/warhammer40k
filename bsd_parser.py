import glob
import os
import re
import uuid
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import pandas as pd


def clean_special_characters(text):
    """Remove special characters like ➤ from the beginning of text"""
    if not text:
        return text
    # Remove special characters at the start
    cleaned = re.sub(r"^[^\w\s]+\s*", "", text)
    return cleaned.strip()


def convert_to_number(value):
    """Convert string values to numbers, handling special cases"""
    if not value or value == "-":
        return 0

    # Remove quotes and plus signs
    cleaned = str(value).replace('"', "").replace("+", "").strip()

    # Handle d6 -> 7, d3 -> 4, etc.
    if "d6" in cleaned.lower():
        return 7
    elif "d3" in cleaned.lower():
        return 4
    elif "d" in cleaned.lower():
        # For other dice notation like 2d6, extract the number before d and multiply
        match = re.search(r"(\d+)d(\d+)", cleaned.lower())
        if match:
            num_dice = int(match.group(1))
            die_size = int(match.group(2))
            return num_dice * (die_size + 1)  # Average + 1 for d6->7 logic

    # Handle ranges like "6-12" - take the higher number
    if "-" in cleaned and cleaned.count("-") == 1:
        parts = cleaned.split("-")
        if len(parts) == 2 and parts[1].isdigit():
            return int(parts[1])

    # Extract first number found
    number_match = re.search(r"\d+", cleaned)
    if number_match:
        return int(number_match.group())

    return 0


def split_keywords(keywords_string, max_columns=5):
    """Split comma-separated keywords into separate columns"""
    if not keywords_string or keywords_string == "-":
        return [""] * max_columns

    keywords = [kw.strip() for kw in keywords_string.split(",")]
    # Pad with empty strings if fewer than max_columns
    while len(keywords) < max_columns:
        keywords.append("")
    # Truncate if more than max_columns
    return keywords[:max_columns]


def extract_faction_from_filename(filename):
    """Extract faction name from .cat filename"""
    # Remove .cat extension and path
    basename = Path(filename).stem

    # Handle different naming patterns
    if " - " in basename:
        # Format: "Aeldari - Craftworlds" -> "Aeldari Craftworlds"
        parts = basename.split(" - ")
        if len(parts) == 2:
            return f"{parts[0]} {parts[1]}"
        else:
            return " ".join(parts)
    else:
        # Single name like "Space Marines"
        return basename


def check_legends_status(unit_entry, namespace):
    """Check if unit is Legends based on descriptions and info"""
    # Check in various places where "legends" might appear

    # Check unit description
    descriptions = unit_entry.findall(f".//{namespace}description")
    for desc in descriptions:
        if desc.text and "legends" in desc.text.lower():
            return "Legends-NotActive"

    # Check info links
    info_links = unit_entry.findall(f".//{namespace}infoLink")
    for info in info_links:
        name = info.get("name", "").lower()
        if "legends" in name:
            return "Legends-NotActive"

    # Check category links
    category_links = unit_entry.findall(f".//{namespace}categoryLink")
    for cat in category_links:
        name = cat.get("name", "").lower()
        if "legends" in name:
            return "Legends-NotActive"

    # Check profiles for legends mention
    profiles = unit_entry.findall(f".//{namespace}profile")
    for profile in profiles:
        # Check profile name
        if "legends" in profile.get("name", "").lower():
            return "Legends-NotActive"

        # Check characteristics descriptions
        characteristics = profile.findall(f".//{namespace}characteristic")
        for char in characteristics:
            if char.text and "legends" in char.text.lower():
                return "Legends-NotActive"

    # Check comments or other text content
    for elem in unit_entry.iter():
        if elem.text and "legends" in elem.text.lower():
            return "Legends-NotActive"
        for attr_value in elem.attrib.values():
            if isinstance(attr_value, str) and "legends" in attr_value.lower():
                return "Legends-NotActive"

    return "TournamentPlay"


def parse_battlescribe_catalogue(xml_file_path):
    """Parse BattleScribe catalogue XML and extract data into normalized tables"""

    # Extract faction name from filename
    faction_name = extract_faction_from_filename(xml_file_path)

    try:
        # Parse the XML
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
    except Exception as e:
        print(f"Error parsing {xml_file_path}: {e}")
        return None

    # Initialize data structures
    units_data = []
    weapons_data = []
    abilities_data = []
    unit_weapons_data = []
    unit_abilities_data = []

    # Extract namespace if present
    namespace = ""
    if root.tag.startswith("{"):
        namespace = root.tag.split("}")[0] + "}"

    def get_element_text(element, tag_name):
        """Helper to get element text, handling namespace"""
        elem = element.find(f"{namespace}{tag_name}")
        return elem.text if elem is not None else ""

    def get_element_attrib(element, attrib_name):
        """Helper to get element attribute"""
        return element.get(attrib_name, "")

    # Process all selectionEntry elements (units)
    for entry in root.findall(f".//{namespace}selectionEntry[@type='unit']"):
        unit_id = get_element_attrib(entry, "id")
        unit_name = clean_special_characters(get_element_attrib(entry, "name"))

        # Check legends status
        legends_status = check_legends_status(entry, namespace)

        # Extract unit profiles (stats)
        profiles = entry.findall(f".//{namespace}profile[@typeName='Unit']")

        for profile in profiles:
            profile_name = clean_special_characters(get_element_attrib(profile, "name"))

            # Extract characteristics (M, T, SV, W, LD, OC)
            characteristics = {}
            for char in profile.findall(f".//{namespace}characteristic"):
                char_name = get_element_attrib(char, "name")
                char_value = char.text if char.text else ""
                characteristics[char_name] = char_value

            # Add unit data with faction as first column and legends status
            unit_data = {
                "faction": faction_name,
                "unit_id": unit_id,
                "unit_name": unit_name,
                "profile_name": profile_name,
                "legends": legends_status,
                "movement": convert_to_number(characteristics.get("M", "")),
                "toughness": convert_to_number(characteristics.get("T", "")),
                "save": convert_to_number(characteristics.get("SV", "")),
                "wounds": convert_to_number(characteristics.get("W", "")),
                "leadership": convert_to_number(characteristics.get("LD", "")),
                "objective_control": convert_to_number(characteristics.get("OC", "")),
                "points_cost": 0,
            }

            # Get points cost
            costs = entry.findall(f".//{namespace}cost[@name='pts']")
            if costs:
                unit_data["points_cost"] = convert_to_number(
                    get_element_attrib(costs[0], "value")
                )

            units_data.append(unit_data)

        # Extract weapons from this unit
        extract_weapons_from_unit(
            entry, unit_id, faction_name, weapons_data, unit_weapons_data, namespace
        )

        # Extract abilities from this unit
        extract_abilities_from_unit(
            entry, unit_id, faction_name, abilities_data, unit_abilities_data, namespace
        )

    # Create DataFrames
    units_df = pd.DataFrame(units_data)
    weapons_df = pd.DataFrame(weapons_data)
    abilities_df = pd.DataFrame(abilities_data)
    unit_weapons_df = pd.DataFrame(unit_weapons_data)
    unit_abilities_df = pd.DataFrame(unit_abilities_data)

    return {
        "units": units_df,
        "weapons": weapons_df,
        "abilities": abilities_df,
        "unit_weapons": unit_weapons_df,
        "unit_abilities": unit_abilities_df,
    }


def extract_weapons_from_unit(
    unit_entry, unit_id, faction_name, weapons_data, unit_weapons_data, namespace
):
    """Extract all weapons from a unit entry"""

    # Find all weapon profiles (both ranged and melee)
    ranged_weapons = unit_entry.findall(
        f".//{namespace}profile[@typeName='Ranged Weapons']"
    )
    melee_weapons = unit_entry.findall(
        f".//{namespace}profile[@typeName='Melee Weapons']"
    )

    all_weapons = [(w, "Ranged") for w in ranged_weapons] + [
        (w, "Melee") for w in melee_weapons
    ]

    for weapon_profile, weapon_type in all_weapons:
        weapon_name = clean_special_characters(weapon_profile.get("name", ""))
        weapon_id = weapon_profile.get("id", str(uuid.uuid4()))

        # Extract weapon characteristics
        characteristics = {}
        for char in weapon_profile.findall(f".//{namespace}characteristic"):
            char_name = char.get("name", "")
            char_value = char.text if char.text else ""
            characteristics[char_name] = char_value

        # Split keywords into separate columns
        keywords_raw = characteristics.get("Keywords", "")
        keyword_columns = split_keywords(keywords_raw, 5)

        # Create weapon data entry with faction as first column
        weapon_data = {
            "faction": faction_name,
            "weapon_id": weapon_id,
            "weapon_name": weapon_name,
            "weapon_type": weapon_type,
            "range": convert_to_number(characteristics.get("Range", "")),
            "attacks": convert_to_number(characteristics.get("A", "")),
            "skill": convert_to_number(
                characteristics.get("WS" if weapon_type == "Melee" else "BS", "")
            ),
            "strength": convert_to_number(characteristics.get("S", "")),
            "ap": convert_to_number(characteristics.get("AP", "")),
            "damage": convert_to_number(characteristics.get("D", "")),
            "keyword01": keyword_columns[0],
            "keyword02": keyword_columns[1],
            "keyword03": keyword_columns[2],
            "keyword04": keyword_columns[3],
            "keyword05": keyword_columns[4],
        }

        weapons_data.append(weapon_data)

        # Create unit-weapon relationship with faction
        unit_weapons_data.append(
            {
                "faction": faction_name,
                "unit_id": unit_id,
                "weapon_id": weapon_id,
                "weapon_name": weapon_name,
            }
        )


def extract_abilities_from_unit(
    unit_entry, unit_id, faction_name, abilities_data, unit_abilities_data, namespace
):
    """Extract all abilities from a unit entry"""

    # Find all ability profiles
    ability_profiles = unit_entry.findall(
        f".//{namespace}profile[@typeName='Abilities']"
    )

    for ability_profile in ability_profiles:
        ability_name = clean_special_characters(ability_profile.get("name", ""))
        ability_id = ability_profile.get("id", str(uuid.uuid4()))

        # Extract ability description
        description = ""
        desc_char = ability_profile.find(
            f".//{namespace}characteristic[@name='Description']"
        )
        if desc_char is not None:
            description = desc_char.text if desc_char.text else ""

        # Create ability data entry with faction as first column
        ability_data = {
            "faction": faction_name,
            "ability_id": ability_id,
            "ability_name": ability_name,
            "description": description,
        }

        abilities_data.append(ability_data)

        # Create unit-ability relationship with faction
        unit_abilities_data.append(
            {
                "faction": faction_name,
                "unit_id": unit_id,
                "ability_id": ability_id,
                "ability_name": ability_name,
            }
        )


def remove_duplicates_from_tables(dataframes_dict):
    """Remove duplicates from all tables based on appropriate columns"""

    print("\n=== REMOVING DUPLICATES ===")

    # Define duplicate removal criteria for each table
    duplicate_criteria = {
        "units": [
            "faction",
            "unit_name",
            "profile_name",
            "movement",
            "toughness",
            "save",
            "wounds",
            "leadership",
            "objective_control",
        ],
        "weapons": [
            "faction",
            "weapon_name",
            "weapon_type",
            "range",
            "attacks",
            "skill",
            "strength",
            "ap",
            "damage",
            "keyword01",
            "keyword02",
            "keyword03",
            "keyword04",
            "keyword05",
        ],
        "abilities": ["faction", "ability_name", "description"],
        "unit_weapons": ["faction", "unit_id", "weapon_id"],
        "unit_abilities": ["faction", "unit_id", "ability_id"],
    }

    cleaned_data = {}

    for table_name, df in dataframes_dict.items():
        if not df.empty and table_name in duplicate_criteria:
            original_count = len(df)

            # Get columns that exist in the dataframe
            available_columns = [
                col for col in duplicate_criteria[table_name] if col in df.columns
            ]

            if available_columns:
                # Remove duplicates based on available columns
                df_cleaned = df.drop_duplicates(subset=available_columns, keep="first")
                duplicates_removed = original_count - len(df_cleaned)

                print(
                    f"{table_name.upper()}: {original_count} → {len(df_cleaned)} records ({duplicates_removed} duplicates removed)"
                )

                cleaned_data[table_name] = df_cleaned
            else:
                print(
                    f"{table_name.upper()}: No duplicate criteria columns found, keeping original"
                )
                cleaned_data[table_name] = df
        else:
            cleaned_data[table_name] = df

    return cleaned_data


def process_all_factions(repository_path):
    """Process all .cat files in the repository"""

    # Find all .cat files
    cat_files = glob.glob(os.path.join(repository_path, "*.cat"))

    # Initialize combined data structures
    all_units = []
    all_weapons = []
    all_abilities = []
    all_unit_weapons = []
    all_unit_abilities = []

    processed_files = []
    failed_files = []

    print(f"Found {len(cat_files)} .cat files to process...")

    for cat_file in cat_files:
        print(f"Processing: {os.path.basename(cat_file)}")

        try:
            # Parse the catalogue
            data_tables = parse_battlescribe_catalogue(cat_file)

            if data_tables:
                # Combine data
                if not data_tables["units"].empty:
                    all_units.append(data_tables["units"])
                if not data_tables["weapons"].empty:
                    all_weapons.append(data_tables["weapons"])
                if not data_tables["abilities"].empty:
                    all_abilities.append(data_tables["abilities"])
                if not data_tables["unit_weapons"].empty:
                    all_unit_weapons.append(data_tables["unit_weapons"])
                if not data_tables["unit_abilities"].empty:
                    all_unit_abilities.append(data_tables["unit_abilities"])

                processed_files.append(cat_file)
            else:
                failed_files.append(cat_file)

        except Exception as e:
            print(f"  Error: {e}")
            failed_files.append(cat_file)

    # Combine all DataFrames
    combined_data = {}

    if all_units:
        combined_data["units"] = pd.concat(all_units, ignore_index=True)
    else:
        combined_data["units"] = pd.DataFrame()

    if all_weapons:
        combined_data["weapons"] = pd.concat(all_weapons, ignore_index=True)
    else:
        combined_data["weapons"] = pd.DataFrame()

    if all_abilities:
        combined_data["abilities"] = pd.concat(all_abilities, ignore_index=True)
    else:
        combined_data["abilities"] = pd.DataFrame()

    if all_unit_weapons:
        combined_data["unit_weapons"] = pd.concat(all_unit_weapons, ignore_index=True)
    else:
        combined_data["unit_weapons"] = pd.DataFrame()

    if all_unit_abilities:
        combined_data["unit_abilities"] = pd.concat(
            all_unit_abilities, ignore_index=True
        )
    else:
        combined_data["unit_abilities"] = pd.DataFrame()

    print(f"\nProcessing complete!")
    print(f"Successfully processed: {len(processed_files)} files")
    print(f"Failed to process: {len(failed_files)} files")

    if failed_files:
        print("Failed files:")
        for file in failed_files:
            print(f"  - {os.path.basename(file)}")

    # Remove duplicates from all tables
    combined_data = remove_duplicates_from_tables(combined_data)

    return combined_data


def save_to_excel(dataframes_dict, output_file):
    """Save all dataframes to separate Excel sheets"""
    with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
        for sheet_name, df in dataframes_dict.items():
            if not df.empty:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
    print(f"Data saved to {output_file}")


def print_summary(dataframes_dict):
    """Print a summary of the extracted data"""
    print("\n=== FINAL DATABASE SUMMARY ===")
    for table_name, df in dataframes_dict.items():
        print(f"{table_name.upper()}: {len(df)} records")
        if not df.empty:
            print(f"  Columns: {', '.join(df.columns)}")
            if "faction" in df.columns:
                factions = df["faction"].nunique()
                print(f"  Unique factions: {factions}")
            if "legends" in df.columns:
                legends_count = len(df[df["legends"] == "Legends-NotActive"])
                tournament_count = len(df[df["legends"] == "TournamentPlay"])
                print(f"  Legends units: {legends_count}")
                print(f"  Tournament play units: {tournament_count}")
        print()


# Main execution
if __name__ == "__main__":
    # Set the path to your cloned repository
    repository_path = "C:\\users\\templar\\wh40\\wh40k-10e"  # Your specified path

    if not os.path.exists(repository_path):
        print(f"Repository path not found: {repository_path}")
        print("Please ensure the repository is cloned to the correct location.")
        exit(1)

    try:
        # Process all faction files
        all_data = process_all_factions(repository_path)

        # Print summary
        print_summary(all_data)

        # Save to Excel file
        save_to_excel(all_data, "wh40k_complete_database.xlsx")

        # Display sample data
        print("=== SAMPLE DATA ===")
        for table_name, df in all_data.items():
            if not df.empty:
                print(f"\n{table_name.upper()} (first 3 rows):")
                print(df.head(3).to_string(index=False))

    except Exception as e:
        print(f"Error processing repository: {e}")
