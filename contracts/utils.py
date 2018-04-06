from colorsys import hsv_to_rgb

def pseudocolor(val, minval=0, maxval=100):
    """ Convert val in range minval..maxval to the range 0..120 degrees which
        correspond to the colors Red and Green in the HSV colorspace.
    """
    val = 100-val
    h = (float(val-minval) / (maxval-minval)) * 120

    # Convert hsv color (h,1,1) to its rgb equivalent.
    # Note: hsv_to_rgb() function expects h to be in the range 0..1 not 0..360
    r, g, b = hsv_to_rgb(h/360, 1., 1.)
    return 'rgb(%s, %s, %s, 0.3)' % (int(round(r*255)), int(round(g*255)), int(round(b*255)))


def insert_html(string, index, insertion):
    return string[:index] + insertion + string[index:]


def multi_replace(text, translations):
    for original, replacement in translations:
        text = text.replace(original, replacement)
    return text
