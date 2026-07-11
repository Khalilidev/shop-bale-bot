def clear_user_state(user_state, temp_customer, temp_transaction, temp_ecxel, 
                     temp_product, temp_id, temp_message, temp_contact, chat_id):
    """
    Clear all temporary data for a user
    
    Args:
        user_state: dict
        temp_customer: dict
        temp_transaction: dict
        temp_ecxel: dict
        temp_product: dict
        temp_id: dict
        temp_message: dict
        temp_contact: dict
        chat_id: int
    """
    user_state.pop(chat_id, None)
    temp_customer.pop(chat_id, None)
    temp_transaction.pop(chat_id, None)
    temp_ecxel.pop(chat_id, None)
    temp_product.pop(chat_id, None)
    temp_id.pop(chat_id, None)
    temp_message.pop(chat_id, None)
    temp_contact.pop(chat_id, None)