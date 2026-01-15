import PhoneInit

def multi_ip_process(phone_info_dict, func_name='create_process', processes_per_ip=2):
    """
    Process phone info grouped by IP address in sequence
    Args:
        phone_info_dict (dict): Dictionary with IP as key and list of phone records as value
        func_name (str): Function name to execute ('create_process' or 'login_process')
        processes_per_ip (int): Number of parallel processes per IP group
    """
    for ip, phone_records in phone_info_dict.items():
        try:
            print(f"Processing IP: {ip}")
            phone_init = PhoneInit.PhoneInit(ip=ip)
            phone_init.batch_process(phone_records, func_name=func_name, processes=processes_per_ip)  
        except Exception as e:
            print(f"Error processing IP {ip}: {e}")
    
    print("All IP groups processed!")


if __name__ == '__main__':
    # #Template
    # Phone_info = {
    #     '172.16.42.55': [
    #         ['1753348345857762993891', 7, '', '',],
    #         ['1753348345857762993891', 7, '', '',]
    #     ],
    #     '172.16.209.72': [
    #         ['1753348345857762993891', 7, '', '',]
    #     ]
    # }

    Phone_info = {
        '192.168.124.15': [
            ['1753348341892341806907', 1, '', '',],
            ['1753348463232143384321', 2, '', '',],
            ['1753348463232143384321', 3, '', '',]
        ],
        '192.168.124.19': [
            ['1753351072740828666988', 8, '', '',],
        ],
        '192.168.124.50': [
            ['1753351072740828666988', 8, '', '',],
        ]
    }
    multi_ip_process(Phone_info, func_name='print_process', processes_per_ip=2)
    # multi_ip_process(delete_info, func_name='delete_process', processes_per_ip=2)
    # # Process all IPs in parallel
    # multi_ip_process(Phone_info, func_name='create_process', processes_per_ip=2)
    
    # # Or for login
    # multi_ip_process(Phone_info, func_name='login_process', processes_per_ip=2)
