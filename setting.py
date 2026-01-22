

def group_pools(info_pools:dict):
    #Group items by their index (second element)
    from collections import defaultdict
    
    grouped = defaultdict(list)
    for item in info_pools:
        index = item[1]
        grouped[index].append(item)
    
    # Convert to list of lists, sorted by index
    group_list = [grouped[i] for i in sorted(grouped.keys())]
    return group_list

#The Goal is slice pool but avoid select same index list in one slice
def batch_slice(groups:list, batch_size=4):
    """
    Select items from different groups to avoid same index in one batch.
    Each batch contains batch_size items from different groups.
    """ 
    import random
    
    # Create a copy to modify
    groups_copy = [group[:] for group in groups]
    
    slice_quene = []
    
    while any(len(group) > 0 for group in groups_copy):
        batch = []
        
        # Get available groups (non-empty)
        available_groups = [i for i, group in enumerate(groups_copy) if len(group) > 0]
        
        # If we have enough groups, select batch_size items
        if len(available_groups) >= batch_size:
            selected_groups = random.sample(available_groups, batch_size)
        else:
            # Use all remaining groups
            selected_groups = available_groups
        
        # Pick one item from each selected group
        for group_idx in selected_groups:
            item = groups_copy[group_idx].pop(0)
            batch.append(item)
        
        slice_quene.append(batch)
    
    return slice_quene

def write_configs(key:str,value:str):
    """
    Open config.json, write value to the specified key, and save.
    """
    import json
    
    try:
        # Read existing config
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Update the key
        config[key] = value
        
        # Write back to file with custom formatting
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json(config, f)
        
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False

def append_configs(key:str,value):
    """
    Open config.json, append value to the specified key (assumes key is a list), and save.
    Only appends if the value doesn't already exist in the list.
    """
    import json
    
    try:
        # Read existing config
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Append to the key (assumes it's a list)
        if key not in config:
            config[key] = []
        
        # Only append if value doesn't already exist
        if value not in config[key]:
            config[key].append(value)
        
        # Write back to file with custom formatting
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json(config, f)
        
        return True
    except Exception as e:
        print(f"Error appending config: {e}")
        return False

def clear_configs(key:str):
    """
    Open config.json, clear the value of the specified key (set to empty list or empty string), and save.
    """
    import json
    
    try:
        # Read existing config
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Clear the key value
        if key in config:
            if isinstance(config[key], list):
                config[key] = []
            elif isinstance(config[key], dict):
                config[key] = {}
            else:
                config[key] = ""
        
        # Write back to file with custom formatting
        with open('config.json', 'w', encoding='utf-8') as f:
            _write_formatted_json(config, f)
        
        return True
    except Exception as e:
        print(f"Error clearing config: {e}")
        return False

def _write_formatted_json(config, file):
    """
    Write JSON with custom formatting: inner arrays on single lines, outer structure indented.
    """
    import json
    
    file.write('{\n')
    keys = list(config.keys())
    for i, key in enumerate(keys):
        file.write(f'  "{key}": ')
        value = config[key]
        
        if isinstance(value, list) and value and isinstance(value[0], list):
            # List of lists - each inner list on one line
            file.write('[\n')
            for j, item in enumerate(value):
                file.write(f'    {json.dumps(item, ensure_ascii=False)}')
                if j < len(value) - 1:
                    file.write(',\n')
                else:
                    file.write('\n')
            file.write('  ]')
        else:
            # Regular value
            file.write(json.dumps(value, indent=2, ensure_ascii=False).replace('\n', '\n  '))
        
        if i < len(keys) - 1:
            file.write(',\n')
        else:
            file.write('\n')
    file.write('}\n')