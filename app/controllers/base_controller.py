from app.data.bases import BASES_LIST

def get_all_bases(status=None):
    if status:
        return [b for b in BASES_LIST if b['status'] == status]
    return BASES_LIST

def get_base_by_id(id):
    return next((base for base in BASES_LIST if base["id"] == id), None)

def count_bases(status=None):
    return len(get_all_bases(status))

def get_active_bases():
    return [base for base in BASES_LIST if base["status"] == 1]

def get_inactive_bases():
    return [base for base in BASES_LIST if base["status"] == 0]

def count_active_bases():
    return len(get_active_bases())

def get_inactive_bases():
    return [base for base in BASES_LIST if base["status"] == 0]

def count_inactive_bases():
    return len(get_inactive_bases())
