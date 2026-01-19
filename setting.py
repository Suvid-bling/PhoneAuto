info_pools = [
    ["4376663538", 1, "", ""], #[_phonenumber,_index,_sendUrl,_verifiedUrl]
    ["5797683178", 1, "", ""],
    ["6134686749", 2, "", ""],
    ["4508371242", 3, "", ""],
    ["5797683243", 3, "", ""],
    ["5797683260", 4, "", ""],
    ["6134687707", 4, "", ""],
    ["5797683288", 5, "", ""],
    ["6134687224", 5, "", ""],
    ["6134687710", 5, "", ""],
    ["5797683304", 6, "", ""],
    ["6134687286", 7, "", ""],
    ["6134687791", 7, "", ""],
    ["4385542111", 8, "", ""],
    ["5797683331", 8, "", ""]


  ]

def group_pools(info_pools=info_pools):
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
def batch_slice(batch_size=4):
    """
    Select items from different groups to avoid same index in one batch.
    Each batch contains batch_size items from different groups.
    """ 
    import random
    
    # Get grouped pools
    groups = group_pools()
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
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Update the key
        config[key] = value
        
        # Write back to file
        with open('config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        return True
    except Exception as e:
        print(f"Error writing config: {e}")
        return False
