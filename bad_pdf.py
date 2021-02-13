# Import libraries
from PIL import Image
import pytesseract
import sys
from pdf2image import convert_from_path
import os
from make_log import log_exceptions

#pytesseract_location = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
#pytesseract.pytesseract.tesseract_cmd = pytesseract_location


def text_from_pdf(pdf_path, outfile):
    try:
        if os.path.isfile(outfile):
            os.remove(outfile)
        rmfilelist = []
        # Path of the pdf
        PDF_file = pdf_path

        '''
        Part #1 : Converting PDF to images
        '''

        # Store all the pages of the PDF in a variable
        pages = convert_from_path(PDF_file, 200)

        # Counter to store images of each page of PDF to image
        image_counter = 1

        # Iterate through all the pages stored above
        pages = pages[:2] + pages[-1]
        for page in pages:
            # Declaring filename for each page of PDF as JPG
            # For each page, filename will be:
            # PDF page 1 -> page_1.jpg
            # PDF page 2 -> page_2.jpg
            # PDF page 3 -> page_3.jpg
            # ....
            # PDF page n -> page_n.jpg
            filename = os.path.dirname(outfile)+'/'+"page_" + str(image_counter) + ".jpg"

            # Save the image of the page in system
            page.save(filename, 'JPEG')

            # Increment the counter to update filename
            image_counter = image_counter + 1

        '''
        Part #2 - Recognizing text from the images using OCR
        '''
        3
        # Variable to get count of total number of pages
        filelimit = image_counter - 1

        # Creating a text file to write the output
        # outfile = outfile

        # Open the file in append mode so that
        # All contents of all images are added to the same file
        f = open(outfile, "a")


        # Iterate from 1 to total number of pages
        for i in range(1, filelimit + 1):
            # Set filename to recognize text from
            # Again, these files will be:
            # page_1.jpg
            # page_2.jpg
            # ....
            # page_n.jpg
            filename = os.path.dirname(outfile)+'/'+"page_" + str(i) + ".jpg"

            # Recognize the text as string in image using pytesserct
            text = str(((pytesseract.image_to_string(Image.open(filename)))))
            rmfilelist.append(filename)

            # The recognized text is stored in variable text
            # Any string processing may be applied on text
            # Here, basic formatting has been done:
            # In many PDFs, at line ending, if a word can't
            # be written fully, a 'hyphen' is added.
            # The rest of the word is written in the next line
            # Eg: This is a sample text this word here GeeksF-
            # orGeeks is half on first line, remaining on next.
            # To remove this, we replace every '-\n' to ''.
            text = text.replace('-\n', '')

            # Finally, write the processed text to the file.
            f.write(text)

        # Close the file after writing all the text.
        f.close()
        for j in rmfilelist:
            if os.path.isfile(j):
                os.remove(j)
        pass
    except:
        log_exceptions()
