from library.botapp import botapp

class cache:
    """
    Always returns -1 if the cache is empty for the requested data.
    """
    @staticmethod
    def cache_perms(uuid, guid, permissions):
        botapp.d['permissions_cache'][f'{uuid}-{guid}'] = permissions
        return True

    @staticmethod
    def get_permissions(uuid, guid):
        try:
            data = botapp.d['permissions_cache'][f'{uuid}-{guid}']
            return data # Returns the permissions if they exist
        except KeyError:
            return -1

    @staticmethod
    def clear_cache():
        botapp.d['permissions_cache'] = {}