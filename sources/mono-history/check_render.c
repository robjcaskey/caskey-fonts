#include <ft2build.h>
#include FT_FREETYPE_H
#include <stdio.h>
int main(int argc,char **argv) {
 FT_Library lib; if(FT_Init_FreeType(&lib)) return 2;
 unsigned long rendered=0, failures=0;
 const int sizes[]={14,19,24,28,32,37,38,42,56,72};
 for(int a=1;a<argc;a++) {
  FT_Face f; if(FT_New_Face(lib,argv[a],0,&f)) return 3;
  for(unsigned s=0;s<sizeof(sizes)/sizeof(*sizes);s++) {
   if(FT_Set_Pixel_Sizes(f,0,sizes[s])) return 4;
   for(FT_UInt g=0;g<f->num_glyphs;g++) {
    FT_Error e=FT_Load_Glyph(f,g,FT_LOAD_NO_AUTOHINT|FT_LOAD_NO_BITMAP|FT_LOAD_PEDANTIC);
    if(!e) e=FT_Render_Glyph(f->glyph,FT_RENDER_MODE_NORMAL);
    if(e) {fprintf(stderr,"%s glyph %u ppem %d error %d\n",argv[a],g,sizes[s],e); failures++; FT_Done_Face(f); if(FT_New_Face(lib,argv[a],0,&f) || FT_Set_Pixel_Sizes(f,0,sizes[s])) return 6; continue;}
    rendered++;
   }
  }
  FT_Done_Face(f);
 }
 FT_Done_FreeType(lib);printf("%lu native-hinted glyph rasters passed\n",rendered);return failures ? 5 : 0;
}
