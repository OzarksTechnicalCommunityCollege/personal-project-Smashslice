from django.utils import timezone


class ChangeRequestTracker:
    SESSION_KEY = 'change_request_views'

    def __init__(self, request):
        self.request = request
        self.session = request.session
        self._data = self.session.get(self.SESSION_KEY)
        if self._data is None:
            self._data = {}
            self.session[self.SESSION_KEY] = self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for key in self._data.keys():
            yield int(key)

    def __contains__(self, request_number):
        return self._key(request_number) in self._data

    def __getitem__(self, request_number):
        return self._data[self._key(request_number)]

    def __bool__(self):
        return bool(self._data)

    def __gt__(self, other):
        if isinstance(other, ChangeRequestTracker):
            return len(self) > len(other)
        if isinstance(other, int):
            return len(self) > other
        return NotImplemented

    def view(self, change_request):
        key = self._key(change_request.request_number)
        self._data[key] = {
            'last_status': change_request.status,
            'viewed_at': timezone.now().isoformat(),
        }
        self._save()

    def seen(self, request_number):
        return self._key(request_number) in self._data

    def get_state(self, request_number):
        return self._data.get(self._key(request_number), {})

    def status_changed(self, change_request):
        state = self.get_state(change_request.request_number)
        last_status = state.get('last_status')
        return bool(last_status and last_status != change_request.status)

    def sync_status(self, change_request):
        key = self._key(change_request.request_number)
        if key not in self._data:
            return
        state = self._data[key]
        state['last_status'] = change_request.status
        state['viewed_at'] = timezone.now().isoformat()
        self._data[key] = state
        self._save()

    def remove(self, request_number):
        key = self._key(request_number)
        if key in self._data:
            del self._data[key]
            self._save()

    def clear(self):
        self._data = {}
        self._save()

    def _key(self, request_number):
        return str(request_number)

    def _save(self):
        self.session[self.SESSION_KEY] = self._data
        self.session.modified = True
