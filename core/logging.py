import configs
def is_seller(Id):
    """
    Check the user(seller or customer).
    
    Args:
        Id(int):
            Received numeric id declere in /configs.
    Returns:
        bool: True, if user is seller . else False.
    """
    if Id == configs.Id : return True
    return False