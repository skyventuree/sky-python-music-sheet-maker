import io, json, importlib
from . import song_renderer
from skymusic import Lang
from skymusic.renderers.instrument_renderers.skyjson_ir import SkyjsonInstrumentRenderer
from skymusic.resources import Resources

class SkyjsonSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, song_bpm=Resources.DEFAULT_BPM):

        super().__init__(locale)
        if isinstance(song_bpm, (int, float)):
            self.song_bpm = song_bpm  # Beats per minute
        else:
            self.song_bpm = Resources.DEFAULT_BPM

    def write_buffers(self, song):

        meta = song.get_meta()
        dt = (60000/self.song_bpm)

        json_buffer = io.StringIO()

        instrument_renderer = SkyjsonInstrumentRenderer(self.locale)

        json_dict = {'name': meta['title'][1], 'author': meta['artist'][1], 'arrangedBy':'', 'transcribedBy': meta['transcript'][1], 'permission':'', 'isComposed': True, 'bpm': int(self.song_bpm), 'pitchLevel':0, 'bitsPerPage': 16, 'isEncrypted': False, 'songNotes': []}

        instrument_index = 0
        time = 0
        for line in song.get_lines():
            if len(line) > 0:
                if line[0].get_type().lower().strip() != 'voice':
                    for instrument in line:
                        instrument.set_index(instrument_index)
                        repeat = instrument.get_repeat()
                        for r in range(repeat):
                            time += dt
                            if not instrument.get_is_silent():
                                json_dict['songNotes'] += instrument_renderer.render(instrument, time)

                        instrument_index += 1

        json_buffer.seek(0)

        json.dump(json_dict, json_buffer)

        return [json_buffer]

    def generate_url(self, json_buffer, api_key=Resources.skyjson_api_key):
        # clears the sys.meta_path cache to reload packages(directory), does not really apply to top-level libraries
        importlib.invalidate_caches()
        try:
            import requests
        except (ImportError, ModuleNotFoundError):
            print("\n***WARNING: 'requests' package not installed: could not generate temp link to sky-music.herokuapp.com")
        
        else:
            json_buffer.seek(0)
            json_dict = json.load(json_buffer)
            json_dict = {'API_KEY': api_key, 'song': json_dict}
    
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            try:
                rep = requests.post(url=Resources.skyjson_api_url, json=json_dict, headers=headers, timeout=5)
                url = rep.text
    
            except (requests.ConnectionError, requests.HTTPError, requests.exceptions.ReadTimeout) as err:
                print('\n*** WARNING:'+Lang.get_string("warnings/skyjson_url_connection", self.locale)+':')
                print(err)
                url = None
    
            return url

