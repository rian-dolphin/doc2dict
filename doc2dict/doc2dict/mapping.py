class JSONTransformer:
    def __init__(self, mapping_dict):
        """Initialize transformer with mapping dictionary."""
        self.mapping_dict = mapping_dict
        self.id_to_text = {}
        self.used_matches = set()

    def _find_refs(self, data, search_key):
        """Find all references based on search key in the data."""
        matches = []
        
        if isinstance(data, dict):
            if search_key in data:
                matches.append(data)
            for value in data.values():
                matches.extend(self._find_refs(value, search_key))
        elif isinstance(data, list):
            for item in data:
                matches.extend(self._find_refs(item, search_key))
                
        return matches

    def _find_content(self, data, match_identifier, match_content):
        """Find all content entries in the data that match the identifier and content pattern."""
        matches = []
        
        if isinstance(data, dict):
            # Check if this dict has both the identifier and content keys
            if match_identifier in data and match_content in data:
                matches.append(data)
            for value in data.values():
                matches.extend(self._find_content(value, match_identifier, match_content))
        elif isinstance(data, list):
            for item in data:
                matches.extend(self._find_content(item, match_identifier, match_content))
                
        return matches

    def _build_mapping(self, data, transformation):
        """Build mapping between identifiers and their content."""
        match_rule = transformation['match']
        id_key = match_rule['identifier']
        content_key = match_rule['content']
        
        content_matches = self._find_content(data, id_key, content_key)
        
        for match in content_matches:
            if id_key in match and content_key in match:
                self.id_to_text[match[id_key]] = match[content_key]
                if match_rule.get('remove_after_use', False):
                    self.used_matches.add(match[id_key])

    def _remove_used_content(self, data, match_rule):
        """Remove the used content entries based on match rule."""
        if isinstance(data, dict):
            id_key = match_rule['identifier']
            
            # If this is a match we used (only need to check id), remove it
            if id_key in data and data.get(id_key) in self.used_matches:
                return None
                
            # Process remaining dict entries
            result = {}
            for k, v in data.items():
                processed = self._remove_used_content(v, match_rule)
                if processed is not None:
                    result[k] = processed
            
            # If dict is empty after processing, remove it
            return result if result else None
            
        elif isinstance(data, list):
            result = [item for item in data 
                     if (processed := self._remove_used_content(item, match_rule)) is not None]
            return result if result else None
            
        return data

    def transform(self, data):
        """Transform the data according to the mapping dictionary."""
        result = data.copy()
        
        for transformation in self.mapping_dict['transformations']:
            # Build mapping from ids to their content
            self._build_mapping(result, transformation)
            
            search_key = transformation['search']['key']
            search_id = transformation['search']['identifier']
            output_key = transformation['output']['key']
            
            # Find all references that need transformation
            refs = self._find_refs(result, search_key)
            
            # Transform each reference
            for ref in refs:
                ref_id = ref[search_key].get(search_id)
                if ref_id in self.id_to_text:
                    # Replace reference with content
                    ref[output_key] = self.id_to_text[ref_id]
                    del ref[search_key]
            
            # Remove the original content if specified
            if transformation['match'].get('remove_after_use', False):
                result = self._remove_used_content(result, transformation['match'])
        
        return result