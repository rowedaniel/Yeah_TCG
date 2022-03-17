##import re, os
import os


# source directories
SOURCE_DIR = 'source'
HOMEPAGE_NAME = 'index.html'
HEADER_NAME = 'header.html'
FOOTER_NAME = 'footer.html'

# deployment directories
DEPLOYMENT_DIR = 'deployment'



def wipe_file(filename : str):
    """ make new file / wipe it if it exists """
    with open(filename, 'w') as outfile:
        outfile.write('')
        outfile.close()

def convert_path(filename : str) -> str:
    """ Convert any (probably windows) path to web-compatible URIs """
    if filename.startswith(SOURCE_DIR):
        filename = filename[len(SOURCE_DIR):]
    while '\\' in filename:
        filename = filename.replace('\\', '/')
    return filename



def get_menu_categories(basedir : str = SOURCE_DIR) -> dict:
    """
    Build a nested dictionary to represent the filesystem.
    
    example:
        source
          |
          +---- category1
          |       |
          |       +==== file.html
          |
          +==== index.html
          |
          +==== otherfile.html

        would turn into:

        {
            'category1': {'file.html': {} },
            'otherfile.html': {}
        }
    """

    categories = {}

    for d in os.listdir(basedir):
        if d.startswith('.'):
            continue
        
        currentdir = os.path.join(basedir, d)

        if os.path.isdir(currentdir):
            subcategories = get_menu_categories(currentdir)
            categories[d] = subcategories
        elif not (d == HOMEPAGE_NAME or \
                  d == HEADER_NAME or \
                  d == FOOTER_NAME):
            categories[d] = {}

    return categories



def deparse_filename(name : str) -> str:
    # first, set it to the name by itself
    out = name.split('.')[0]

    # next, do some preprocessing (title case, _ turns into a space, etc.)
    out = out.title().replace('_', ' ')

    return out
    


def build_menu_item(basedir : str,
                    name : str) -> str:
    """
    Builds an item (link to a particular page) for the menu.
    note that this is NOT responseible for building categories of menus.
    """

    link = convert_path(os.path.join(basedir, name))
    
    out = deparse_filename(name)

    # then, encapsulate it in other stuff
    out = f"<p>{out}</p>"
    out = f'<div class="menuItem">{out}</div>'
    out = f'<a href="{link}">{out}</a>'

    return out
    

def build_menu(categories : dict,
               basedir : str = SOURCE_DIR,
               first : bool = True) -> str:
    """
    Build the menu (as given by get_menu_categories, and returns the string
    """
    
    out = ''

    # first get all the contents
    for c in categories:
        cat = ''
        
        # it's a file
        if categories[c] == {}:
            cat = build_menu_item(basedir, c)

        # it's a category (folder), so make it a menu
        else:

            # get sub content            
            cat = build_menu(categories[c],
                             os.path.join(basedir, c),
                             False)

            # encapsulate it in other stuff
            menuName = deparse_filename(c)
            cat = f'<div>{cat}</div>'
            cat = f'<div class="menu"><p>{menuName}</p>{cat}</div>'

        # weird html/css formatting stuff requires this
        if first:
            cat = f'<div>{cat}</div>'

        out += cat

    if first:
        out = f'<div id="documentOutline" class="menu">{out}</div>'

    return out


def write_page(filename : str, menu : str):
    """
    Writes the page content from the source to the deployment directories.
    """
    # (TODO: make this description longer & better)


    outfilename = os.path.join(DEPLOYMENT_DIR, filename)
    
    wipe_file(outfilename)
    with open(outfilename, 'a') as outfile:

        # header
        with open(os.path.join(SOURCE_DIR, HEADER_NAME), 'r') as infile:
            outfile.write(infile.read())

        # menu
        outfile.write(menu)
    
        # main body
        with open(os.path.join(SOURCE_DIR, filename), 'r') as infile:
            outfile.write(infile.read())

        # footer
        with open(os.path.join(SOURCE_DIR, FOOTER_NAME), 'r') as infile:
            outfile.write(infile.read())

def write_pages(categories : dict, menu : str, basedir : str = ''):
    """
    Writes all pages and subpages from the source to the deployment directories.

    NOTE:
        unlike the previous functions, this one does not take the source
        directory as the base directory, as the point of it is to build from
        source to deployment.
    
    """

    # for first-level only (may want to expand this later...):
    if basedir == '':
        write_page('index.html', menu)

    # if the directory doesn't exist, then create it.
    depdir = os.path.join(DEPLOYMENT_DIR, basedir)
    if not os.path.isdir(depdir):
        os.mkdir(depdir)

    for c in categories:

        # it's a file, so write it now
        if categories[c] == {}:
            write_page(os.path.join(basedir,c), menu)

        else: 
            write_pages(categories[c], menu, os.path.join(basedir,c))


def make_all():

    # get all main menu categories
    categories = get_menu_categories()
    menu = build_menu(categories)

    write_pages(categories, menu)






if __name__ == '__main__':
    make_all()
