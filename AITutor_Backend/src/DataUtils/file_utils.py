from pptx import Presentation
import glob

def read_pptx_file(pptx_file):
    content = ''
    prs = Presentation(pptx_file)
    for slide in prs.slides:
        for shape in slide.shapes:
            if hasattr(shape, "text"):
                content+=shape.text+'\n'
    return content