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
    if Id == configs.SELLER_ID : return True
    return False