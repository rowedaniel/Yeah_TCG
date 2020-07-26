from PIL import Image, ImageFilter
#Read image
im1 = Image.open( 'cardtemplate2.png' )
im2 = Image.open( 'fonts/default.png' )

im1.paste(im2)
im1.show()
