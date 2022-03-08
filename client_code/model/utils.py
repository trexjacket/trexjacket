def clean_record_key(key):
    """Clean the record keys from tableau"""
    return key.replace("(generated)", "").strip().lower().replace(" ", "_")
