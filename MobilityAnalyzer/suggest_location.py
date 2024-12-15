import re
import pandas as pd
import Levenshtein as Lev


def suggest_location(raw_location_name: str, location_names_source_path: str) -> list:
    """
    Reads the Excel list of Ottoman location names
    and makes 25 suggestions using Levenshtein distance.
    Args:
        location_names_source_path:
        raw_location_name: Location name as generated by
        OCR and Latinization.
    Returns:
         An array of 25 suggested location names as string.
    """

    if (raw_location_name == ""
            or raw_location_name is None or not bool(re.search(r'[a-zA-Z]', raw_location_name))
            or raw_location_name == "Not specified"):
        return ["No suggestion."]

    raw_location_name_lowercased = raw_location_name.lower()

    # Normalize some Turkish characters
    replacements = {
        'û': 'u',
        'ç': 'c',
        'ü': 'u',
        'ö': 'o',
        'î': 'i',
        'â': 'a',
        'ş': 's',
        'ı': 'i',
        'ğ': 'g'
    }

    # Apply all replacements
    for old, new in replacements.items():
        raw_location_name_lowercased = raw_location_name_lowercased.replace(old, new)

    # Some location names may include administrative unit
    # suffixes, such as X Village, Y Town. We need to remove them before working on them.
    # List of suffixes to remove
    suffixes = [
        ' nahiyesi',
        ' karyesi',
        ' koyu',
        ' kasabasi',
        ' mahallesi',
        ' ilcesi',
        ' vilayeti',
        ' sancagi',
        ' sancak',
        ' kazasi',
        ' kaza',
        ' sehri',
        ' ceziresi',
    ]

    # Remove suffix if found
    suffix_from_raw = ""
    for suffix in suffixes:
        if raw_location_name_lowercased.endswith(suffix):
            suffix_from_raw = suffix
            raw_location_name_lowercased = raw_location_name_lowercased[:-len(suffix)]
            break  # Exit after first match, as there can be only one suffix

    # Read the Excel file containing the Ottoman location names
    df = pd.read_excel(location_names_source_path)

    # Calculate the Levenshtein distance
    df['distance'] = (df['cleaned_location_name'].
                      apply(lambda x: Lev.distance(str(x), str(raw_location_name_lowercased))))

    # Sort the DataFrame by the distance and filter out same results
    df = df.sort_values(by='distance')
    df = df.drop_duplicates(subset='cleaned_location_name')

    # Return the top 25 suggestions as json
    return df['cleaned_location_name'].head(25).apply(lambda x: x + suffix_from_raw).to_list()
