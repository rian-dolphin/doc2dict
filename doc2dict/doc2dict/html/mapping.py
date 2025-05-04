import re
from collections import OrderedDict

# EXAMPLE MAPPING DICT

# Looks like we need to add is_section to the data dict
# also add cleaning
example_mapping_dict = {
    "hierarchy": {
        "1": [
            {
                "section": "part", 
                "regex": r"^p\s*a\s*r\s*t\s+([ivxlcdm]+)$",
                "format": "{section} {1}",  # use capture group 1
            },
        ],
        "2": [
            {
                "section": "item", 
                "regex": r"^i\s*t\s*e\s*m\s+(\d+)$",
                "format": "{section} {1}",  # use capture group 1
            },
            {
                "section": "signatures", 
                "regex": r"^s\s*i\s*g\s*n\s*a\s*t\s*u\s*r\s*e\s?$",
                "format": "{section}",  # no capture groups needed
            },
        ],
    }
}

def map_dict(dct, mapping_dict):
    if mapping_dict is None:
        return dct
    
    # First, flatten the dictionary to get a linear view of all content
    flattened = []
    
    def flatten_dict(obj, path="", parent_path=""):
        """Flatten nested dict to list of (key, value, path) tuples"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}/{key}" if path else key
                
                # Store the dict node itself
                flattened.append((key, value, current_path, parent_path))
                
                if isinstance(value, dict):
                    flatten_dict(value, current_path, path)
    
    flatten_dict(dct)
    
    # Find all section headers matching our patterns
    sections = []
    matched_paths = set()  # Track paths of matched sections
    
    for idx, (key, value, path, parent_path) in enumerate(flattened):
        # Only process if this is a section header
        if isinstance(value, dict) and value.get('is_section_header', False):
            key_lower = key.lower()
            
            # Check against all hierarchy patterns
            for level, patterns in mapping_dict.get("hierarchy", {}).items():
                for pattern_info in patterns:
                    regex = pattern_info["regex"]
                    match = re.match(regex, key_lower, re.IGNORECASE)
                    
                    if match:
                        # Extract capture groups
                        groups = match.groups()
                        
                        # Format the new key name
                        format_str = pattern_info["format"]
                        
                        # Replace {section} with actual section name
                        new_key = format_str.replace("{section}", pattern_info["section"])
                        
                        # Replace numbered placeholders with capture groups
                        for i, group in enumerate(groups, start=1):
                            new_key = new_key.replace(f"{{{i}}}", group)
                        
                        new_key = new_key.lower()
                        
                        sections.append({
                            'index': idx,
                            'original_key': key,
                            'new_key': new_key,
                            'level': level,
                            'value': value,
                            'path': path,
                            'parent_path': parent_path
                        })
                        matched_paths.add(path)
                        break
                if sections and sections[-1]['index'] == idx:
                    break  # Found a match, no need to check other levels
    
    # Sort sections by their appearance order
    sections.sort(key=lambda x: x['index'])
    
    # If no sections found, return original
    if not sections:
        return dct
    
    # Rebuild the hierarchy
    result = {}
    
    # Process each section and its content
    for i, section in enumerate(sections):
        level = section['level']
        new_key = section['new_key']
        
        # Initialize level if needed
        if level not in result:
            result[level] = OrderedDict()
        
        # Find content that belongs to this section
        # (everything from this section until the next section)
        start_idx = section['index']
        end_idx = sections[i + 1]['index'] if i + 1 < len(sections) else len(flattened)
        
        # Collect all content for this section
        section_content = {}
        
        for j in range(start_idx, end_idx):
            item_key, item_value, item_path, item_parent_path = flattened[j]
            
            # Skip if this is the section itself
            if j == start_idx:
                if isinstance(item_value, dict):
                    section_content = item_value.copy()
                continue
            
            # Skip if this is another matched section
            if item_path in matched_paths:
                continue
            
            # Add content to this section
            # Calculate relative path from section
            if item_path.startswith(section['path'] + '/'):
                # This is a child of the section
                relative_path = item_path[len(section['path']) + 1:]
                nested_set(section_content, relative_path.split('/'), item_value)
        
        result[level][new_key] = section_content
    
    # Build a clean structure without the matched sections
    def clean_dict(obj, path=""):
        """Rebuild dictionary without matched sections"""
        if not isinstance(obj, dict):
            return obj
        
        cleaned = {}
        for key, value in obj.items():
            current_path = f"{path}/{key}" if path else key
            
            # Skip if this path was matched (it's being moved)
            if current_path in matched_paths:
                continue
            
            # Skip if all children are matched sections
            if isinstance(value, dict):
                cleaned_value = clean_dict(value, current_path)
                if cleaned_value:  # Only add if there's content left
                    cleaned[key] = cleaned_value
            else:
                cleaned[key] = value
        
        return cleaned
    
    # Clean the original structure
    cleaned_original = clean_dict(dct)
    
    # Add remaining content to unmatched
    if cleaned_original:
        result['unmatched'] = cleaned_original
    
    return result
def nested_set(d, keys, value):
    """Set a value in a nested dictionary using a list of keys"""
    for key in keys[:-1]:
        d = d.setdefault(key, {})
    d[keys[-1]] = value