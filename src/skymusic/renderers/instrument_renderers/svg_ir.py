from . import instrument_renderer
from skymusic.renderers.note_renderers.svg_nr import SvgNoteRenderer

class SvgInstrumentRenderer(instrument_renderer.InstrumentRenderer):
    
    def __init__(self, locale=None):
        super().__init__(locale)

    def render_voice(self, instrument, x, width: str, height: str, aspect_ratio):
        """Renders the lyrics text in SVG"""
        voice_render = (f'\n<svg x="{x :.2f}" y="0" width="100%" height="{height}" class="voice voice-{instrument.get_index()}">'
                        f'\n<text x="0%" y="50%" class="voice voice-{instrument.get_index()}">{instrument.get_lyric(strip_html=True)}</text>'
                        f'</svg>')

        return voice_render


    def render_harp(self, instrument, x, harp_width, harp_height, aspect_ratio):
        """
        Renders the Instrument in SVG
        """
        harp_silent = instrument.get_is_silent()
        harp_broken = instrument.get_is_broken()

        if harp_broken:
            class_suffix = "broken"
        elif harp_silent:
            class_suffix = "silent"
        else:
            class_suffix = ''

        note_renderer = SvgNoteRenderer()

        # The harp SVG container
        harp_render = f'\n<svg x="{x :.2f}" y="0" width="{harp_width}" height="{harp_height}" class="{instrument.get_type()}-{instrument.get_index()} {class_suffix}">'

        # The harp rectangle with rounded edges
        harp_render += f'<rect x="0.7%" y="0.7%" width="98.6%" height="98.6%" rx="7.5%" ry="{7.5 * aspect_ratio :.2f}%" class="{instrument.get_type()} {instrument.get_type()}-{instrument.get_index()}"/>'

        for row in range(instrument.get_row_count()):
            for col in range(instrument.get_column_count()):
                note = instrument.get_note_from_position((row, col))
                
                rescale_ratio = (instrument.get_aspect_ratio()/(5/3))**2
                note_width = 0.21*rescale_ratio
                xn0 = 0.12*rescale_ratio
                yn0 = 0.15*rescale_ratio
                xn = xn0 + col * (1 - 2 * xn0) / (instrument.get_column_count() - 1) - note_width / 2.0
                yn = yn0 + row * (1 - 2 * yn0*1.07) / (instrument.get_row_count() - 1) - note_width / 2.0

                # NOTE RENDER
                harp_render += note_renderer.render(note, x=f"{100*xn :.2f}%", y=f"{100*yn :.2f}%", width=f"{100*note_width :.2f}%")
                
        harp_render += '\n</svg>'

        return harp_render
