import io
from . import song_renderer
from skymusic.renderers.instrument_renderers.svg_ir import SvgInstrumentRenderer
from skymusic.modes import CSSMode
from skymusic.resources import Resources

class SvgSongRenderer(song_renderer.SongRenderer):

    def __init__(self, locale=None, aspect_ratio=16/9.0, theme=Resources.get_default_theme()):
        
        super().__init__(locale)
        Resources.load_theme(theme)

        self.aspect_ratio = aspect_ratio
        self.maxIconsPerLine = round(10*aspect_ratio/(16/9.0))
        
        self.SVG_viewPort = (0.0, 0.0, 750*self.aspect_ratio, 750.0)
        self.minDim = self.SVG_viewPort[2] * 0.01
        self.SVG_viewPortMargins = (13.0, 7.5)       
        self.SVG_line_width = self.SVG_viewPort[2] - self.SVG_viewPortMargins[0]
        
        self.pt2px = 96.0 / 72
        self.fontpt = 12
        self.SVG_text_height = self.fontpt * self.pt2px  # In principle this should be in em
        self.maxFiles = Resources.MAX_NUM_FILES
        
        self.harp_relspacings = (0.13, 0.1)# Fraction of the harp width that will be allocated to the spacing between harps
        
        self.SVG_harp_width = max(self.minDim, (self.SVG_viewPort[2] - self.SVG_viewPortMargins[0]) / (
                1.0 * self.maxIconsPerLine * (1 + self.harp_relspacings[0])))
                
        self.harp_relAspectRatio = 1.455/(5/3)
        #self.harp_AspectRatio = 1.455       
        self.set_harp_AspectRatio(5/3, self.harp_relAspectRatio)

    def set_harp_AspectRatio(self, harp_AspectRatio, harp_relAspectRatio=1):
        
        self.harp_AspectRatio = harp_AspectRatio*harp_relAspectRatio
        self.SVG_harp_size = (self.SVG_harp_width, max(self.minDim, self.SVG_harp_width / self.harp_AspectRatio))
        self.SVG_harp_spacings = (
            self.harp_relspacings[0] * self.SVG_harp_width,
            self.harp_relspacings[1] * self.SVG_harp_width / self.harp_AspectRatio)
        
    def get_voice_SVG_height(self):
        """Tries to predict the height of the lyrics text when rendered in SVG"""
        return self.fontpt * self.pt2px

    def write_headers(self, svg_buffer, filenum, song, css_mode):
         
        rel_css_path = Resources.rel_css_path
        meta = song.get_meta()                 
        # SVG/XML headers
        svg_buffer.write('<?xml version="1.0" encoding="utf-8" ?>')

        if css_mode == CSSMode.HREF:
            svg_buffer.write(f'\n<?xml-stylesheet href="{rel_css_path}" type="text/css" alternate="no" media="all"?>')

        svg_buffer.write(f'\n<svg baseProfile="full" version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:ev="http://www.w3.org/2001/xml-events" xmlns:xlink="http://www.w3.org/1999/xlink"'
                         f' width="100%" height="100%"'
                         f' viewBox="{self.SVG_viewPort[0] :.2f} {self.SVG_viewPort[1] :.2f} {self.SVG_viewPort[2] :.2f} {self.SVG_viewPort[3] :.2f}" preserveAspectRatio="xMinYMin">')

        if css_mode == CSSMode.EMBED:
            svg_buffer.write('\n<defs><style type="text/css"><![CDATA[\n')
            svg_buffer.write(Resources.CSS['common'].getvalue())
            svg_buffer.write(Resources.CSS['svg'].getvalue())
            svg_buffer.write('\n]]></style></defs>')
        elif css_mode == CSSMode.IMPORT:
            svg_buffer.write('\n<defs><style type="text/css">')
            svg_buffer.write("@import url(\'%s\');</style></defs>" % rel_css_path.replace('\\','/'))
        else:
            svg_buffer.write('\n<defs></defs>')

        svg_buffer.write(f"\n<title>{meta['title'][1]}-{filenum}</title>")        


    def write_buffers(self, song, css_mode=CSSMode.EMBED, start_row=0, start_col=0, buffer_list=None):

        if buffer_list is None:
            buffer_list = []
        if len(buffer_list) >= self.maxFiles:
            print(f"\n***WARNING: Your song is too long. Stopping at {self.maxFiles} files.")
            return buffer_list

        instrument_renderer = SvgInstrumentRenderer(self.locale)
        self.set_harp_AspectRatio(song.get_harp_aspect_ratio(), self.harp_relAspectRatio)
        #self.set_harp_AspectRatio(1.455)

        svg_buffer = io.StringIO()
        filenum = len(buffer_list)
        meta = song.get_meta()

        self.write_headers(svg_buffer, filenum, song, css_mode)             
       
        # Header SVG container
        song_header = (f'\n<svg x="{self.SVG_viewPortMargins[0] :.2f}" y="{self.SVG_viewPortMargins[1] :.2f}"'
                       f' width="{self.SVG_line_width :.2f}" height="{(self.SVG_viewPort[3] - self.SVG_viewPortMargins[1]) :.2f}">'
                       )

        x = 0
        y = self.SVG_text_height  # Because the origin of text elements of the bottom-left corner

        if filenum == 0:
            song_header += f"\n<text x=\"{x :.2f}\" y=\"{y :.2f}\" class=\"title\">{meta['title'][1]}</text>"           
            
            for k in meta:
                if k != 'title':
                    y += 2 * self.SVG_text_height
                    song_header += f'\n<text x="{x :.2f}" y="{y :.2f}" class="headers">{meta[k][0]} {meta[k][1]}</text>'
                    
        else:
            song_header += f"\n<text x=\"{x :.2f}\" y=\"{y :.2f}\" class=\"title\">{meta['title'][1]} (page {(filenum + 1)})</text>"

        # Dividing line
        y += self.SVG_text_height
                
        song_header += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{(self.SVG_harp_spacings[1] / 2.0) :.2f}">'
                        f'\n<line x1="0" y1="50%" x2="100%" y2="50%" class="divide"/> '
                        f'\n</svg>')
                
        y += self.SVG_text_height

        song_header += '\n</svg>'

        svg_buffer.write(song_header)

        # Song SVG container
        ysong = y

        song_render = (f'\n<svg x="{self.SVG_viewPortMargins[0] :.2f}" y="{y :.2f}"'
                       f' width="{self.SVG_line_width :.2f}" height="{(self.SVG_viewPort[3] - y) :.2f}" class="song">'
                      )
        y = 0  # Because we are nested in a new SVG
        x = 0
        instrument_index = 0
        end_row = song.get_num_lines()
        end_col = 0
        ncols = self.maxIconsPerLine
        page_break = False
        for row in range(start_row, end_row):

            line = song.get_line(row)
            if row > start_row:
                start_col = 0
            linetype = line[0].get_type()
            ncols = len(line) - start_col
            end_col = len(line)
            
            # Line SVG container
            if linetype.lower().strip() == 'voice':
                
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_text_height :.2f}"'
                                f' class="line-{row}">'
                               )
                y += self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0
                
            else:
                # Dividing line
                y += self.SVG_harp_spacings[1] / 4.0
                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{(self.SVG_harp_spacings[1] / 2.0) :.2f}">'
                                f'\n<line x1="0" y1="50%" x2="100%" y2="50%" class="divide"/>'
                                f'\n</svg>'
                               )
                y += self.SVG_harp_spacings[1] / 4.0

                y += self.SVG_harp_spacings[1] / 2.0

                song_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_harp_size[1] :.2f}"'
                                f' class="line-{row}">'
                                )

                y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1] / 2.0

            line_render = ''
            sub_line = 0
            x = 0
            for col in range(start_col, end_col):

                instrument = song.get_instrument(row, col)
                instrument.set_index(instrument_index)

                # Creating a new line if max number is exceeded
                if (int(1.0 * (col-start_col) / self.maxIconsPerLine) - sub_line) > 0:
                    
                    # Closing previous instrument-line
                    line_render += '\n</svg>'
                    sub_line += 1
                    x = 0

                    # New Line SVG placeholder
                    if linetype.lower().strip() == 'voice':
                        line_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_text_height :.2f}"'
                                        f' class="line-{row}-{sub_line}">'
                                        )
                        y += self.SVG_text_height + self.SVG_harp_spacings[1] / 2.0
                    else:
                        y += self.SVG_harp_spacings[1] / 2.0

                        line_render += (f'\n<svg x="0" y="{y :.2f}" width="{self.SVG_line_width :.2f}" height="{self.SVG_harp_size[1] :.2f}"'
                                        f' class="line-{row}-{sub_line}">'
                                        )

                        y += self.SVG_harp_size[1] + self.SVG_harp_spacings[1] / 2.0

                #NEW
                if linetype.lower().strip() == 'voice':
                    ypredict = y + ysong
                else:
                    ypredict = y + ysong
                if ypredict > (self.SVG_viewPort[3] - self.SVG_viewPortMargins[1]):
                    page_break = True
                    end_col = col
                    break

                # INSTRUMENT RENDER
                instrument_render = instrument_renderer.render(instrument, x, f"{(100.0 * self.SVG_harp_size[0] / self.SVG_line_width) :.2f}%", "100%", self.harp_AspectRatio)

                # REPEAT
                if instrument.get_repeat() > 1:

                    instrument_render += (f'\n<svg x="{(x + self.SVG_harp_size[0]) :.2f}" y="0%" class="repeat"'
                                          f' width="{(100.0 * self.SVG_harp_size[0] / self.SVG_line_width) :.2f}%" height="100%">'
                                         )
                    instrument_render += f'\n<text x="2%" y="98%" class="repeat">x{instrument.get_repeat()} </text></svg>'

                    x += self.SVG_harp_spacings[0]

                line_render += instrument_render
                instrument_index += 1
                x += self.SVG_harp_size[0] + self.SVG_harp_spacings[0]

            #end loop on cols: closing line
            line_render += '\n</svg>'  # Close instrument-line SVG
            song_render += line_render

            if page_break:
                end_row = row
                break

        #End loop on rows                
        song_render += '\n</svg>'  # Close song-class SVG
        
        svg_buffer.write(song_render)
        svg_buffer.write('\n</svg>')  # Close file SVG

        svg_buffer.seek(0)
        buffer_list.append(svg_buffer)

        
        # Open new file
        if end_row < song.get_num_lines() or 0 < end_col < ncols:
            buffer_list = self.write_buffers(song, css_mode, end_row, end_col, buffer_list)

        return buffer_list
