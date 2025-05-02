from app.data.domaines import DOMAINES_LIST

def get_all_domaines(status=None):
    if status:
        return [d for d in DOMAINES_LIST if d['status'] == status]
    return DOMAINES_LIST

def get_domaine_by_id(domaine_id):
    return next((d for d in DOMAINES_LIST if d['id'] == domaine_id), None)

def count_domaines(status=None):
    return len(get_all_domaines(status))

def get_active_domaines():
    return [domaine for domaine in DOMAINES_LIST if domaine["status"] == 1]

def get_inactive_domaines():
    return [domaine for domaine in DOMAINES_LIST if domaine["status"] == 0]

def count_active_domaines():
    return len(get_active_domaines())

def get_inactive_domaines():
    return [domaine for domaine in DOMAINES_LIST if domaine["status"] == 0]

def count_inactive_domaines():
    return len(get_inactive_domaines())
