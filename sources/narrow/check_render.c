#include <ft2build.h>
#include FT_FREETYPE_H
#include <stdio.h>
int main(int argc, char **argv) {
 FT_Library lib; if (FT_Init_FreeType(&lib)) return 2;
 unsigned long n=0, errors=0;
 int sizes[]={19,24,28,32,38,42};
 for(int a=1;a<argc;a++) {
  FT_Face face; if(FT_New_Face(lib,argv[a],0,&face)) return 3;
  for(unsigned s=0;s<sizeof(sizes)/sizeof(*sizes);s++) {
   if(FT_Set_Pixel_Sizes(face,0,sizes[s])) return 4;
   for(unsigned c=32;c<127;c++) {
    FT_Error e=FT_Load_Char(face,c,FT_LOAD_RENDER|FT_LOAD_NO_AUTOHINT|FT_LOAD_PEDANTIC);
    if(e) { fprintf(stderr,"%s char %u size %d error %d\n",argv[a],c,sizes[s],e); errors++; }
    else n++;
   }
  }
  FT_Done_Face(face);
 }
 FT_Done_FreeType(lib); printf("%lu hinted ASCII rasters passed; %lu errors\n",n,errors);
 return errors ? 1 : 0;
}
