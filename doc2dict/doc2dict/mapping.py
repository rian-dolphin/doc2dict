import re

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

class RuleProcessor:
    def __init__(self, rules_dict):
        self.rules = rules_dict
        
    def _apply_remove_rules(self, lines):
        if 'remove' not in self.rules:
            return lines
            
        result = lines.copy()
        for rule in self.rules['remove']:
            pattern = rule['pattern']
            match_type = rule.get('match_type', 'exact')
            
            if match_type == 'exact':
                result = [line for line in result if pattern != line]
            elif match_type == 'strip':
                result = [line for line in result if pattern != line.strip()]
                
        return result
        
    def _find_matching_end(self, lines, start_idx, end_pattern):
        """Find matching end pattern considering nesting."""
        pattern_name = None
        nesting_level = 1
        
        for i in range(start_idx + 1, len(lines)):
            line = lines[i]
            
            # Check for nested start patterns
            if pattern_name and re.match(pattern_name, line):
                nesting_level += 1
            # Check for end pattern
            elif re.match(end_pattern, line):
                nesting_level -= 1
                if nesting_level == 0:
                    return i
                    
        return len(lines) - 1
        
    def _process_block(self, lines, start_idx, rule, mappings):
        """Process a block of content, handling nested blocks."""
        content = []
        current_idx = start_idx + 1
        end_idx = None
        
        if rule.get('end'):
            end_idx = self._find_matching_end(lines, start_idx, rule['end'])
        else:
            # If no end pattern, collect until next hierarchy match
            for i in range(start_idx + 1, len(lines)):
                if any(re.match(r['pattern'], lines[i]) 
                      for r in mappings if r.get('hierarchy') is not None):
                    end_idx = i - 1
                    break
            if end_idx is None:
                end_idx = len(lines) - 1
                
        # Process content between start and end
        while current_idx < end_idx:
            line = lines[current_idx]
            matched = False
            
            # Check for nested patterns
            for nested_rule in mappings:
                if re.match(nested_rule['pattern'], line):
                    nested_content, next_idx = self._process_block(
                        lines, current_idx, nested_rule, mappings
                    )
                    if nested_content:
                        content.append(nested_content)
                    current_idx = next_idx + 1
                    matched = True
                    break
                    
            if not matched:
                content.append(line)
                current_idx += 1
                
        return {
            'type': rule['name'],
            'content': content
        }, end_idx
        
    def _apply_mapping_rules(self, lines):
        if 'mappings' not in self.rules:
            return {'content': lines}
            
        result = {'content': []}
        mappings = sorted(
            self.rules['mappings'],
            key=lambda x: x.get('hierarchy', float('inf'))
        )
        
        i = 0
        current_section = None
        
        while i < len(lines):
            line = lines[i]
            matched = False
            
            for rule in mappings:
                if re.match(rule['pattern'], line):
                    if rule.get('hierarchy') is not None:
                        # Handle hierarchical section
                        current_section = {
                            'type': rule['name'],
                            'text': line,
                            'content': []
                        }
                        result['content'].append(current_section)
                        i += 1
                    else:
                        # Handle block with potential nesting
                        block, end_idx = self._process_block(lines, i, rule, mappings)
                        if current_section:
                            current_section['content'].append(block)
                        else:
                            result['content'].append(block)
                        i = end_idx + 1
                    matched = True
                    break
                    
            if not matched:
                if current_section:
                    current_section['content'].append(line)
                else:
                    result['content'].append(line)
                i += 1
                
        return result

class DocumentProcessor:
    def __init__(self, config):
        self.rules = config.get('rules', {})
        self.transformations = config.get('transformations', [])
        self.rule_processor = RuleProcessor(self.rules)
        self.json_transformer = JSONTransformer({'transformations': self.transformations}) if self.transformations else None
        
    def process(self, lines):
        filtered_lines = self.rule_processor._apply_remove_rules(lines)
        structured_data = self.rule_processor._apply_mapping_rules(filtered_lines)
        
        if self.json_transformer:
            structured_data = self.json_transformer.transform(structured_data)
            
        return structured_data