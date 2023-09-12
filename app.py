from flask import Flask, render_template, request, send_file
from translate import translate_text_with_glossary as twg
from ocr import pdf2images, mal_ocr
import joblib
from format import split_into_sentences_custom
from gpt4 import simp_clean

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# lines = []
# comp_sentences = []


@app.route('/convert', methods=['POST'])
def convert_pdf():
    # global comp_sentences
    pdf_file = request.files['file']

    pdf_file.save(f"documents/{pdf_file.filename}")
    fname = pdf_file.filename.rsplit('.', 1)[0]
    # with open(pdf_file.filename, 'ren') as pdfn_file:
    #     print(pdfn_file)
    if pdf_file and pdf_file.filename.endswith('.pdf'):
        pages = pdf2images(pdf_file)

        lines = []
        ocr_textls = []
        lnes = []
        for img in pages:  # if using PyMuPdf use 'images' instead of 'image_files_sorted'
            ocr_textls.append(mal_ocr(img))
        for line in ocr_textls:
            lines.append(line.split('\n'))
        for lst in lines:
            for line in lst:
                lnes.append(line)
        del lines
        lines = lnes
        del lnes

        comp_sentences = []

        loaded_model = joblib.load('random_forest_model.joblib')
        new_lines = lines

        def extract_features(line):
            char_count = len(line)
            ends_with_full_stop = line.endswith('.')
            # Count Malayalam characters
            malayalam_chars = sum(
                1 for char in line if '\u0D00' <= char <= '\u0D7F')

            return [char_count, int(ends_with_full_stop), malayalam_chars]

        # Extract features for the new lines
        new_data = [extract_features(line) for line in new_lines]

        # Make predictions using the loaded model
        predictions = loaded_model.predict(new_data)

        # Print the predictions for each line
        for line, prediction in zip(new_lines, predictions):
            if prediction:
                # print(f"{line}")
                comp_sentences.append(line)

            else:
                pass  # print(f"'{line}' is not relevant.")

        single_string = " ".join(comp_sentences)
        input_text = single_string

        # Split the text into sentences
        sentences = split_into_sentences_custom(input_text)

        # Print the resulting sentences
        for i, sentence in enumerate(sentences):
            print(f"Sentence {i+1}: {sentence}")

        translated_txt = []
        for sent in sentences:
            # translated_txt.append(translate_text_with_glossary(text='കോടി'))

            translated_txt.append(twg(text=sent))
        
        cleaned = []
        for sentence in translated_txt:
            clnd = simp_clean(sentence)
            cleaned.append(clnd)
            print(clnd)

        with open('output.txt', 'w', encoding='utf-8') as text_file:
            text_file.write("\n".join(cleaned))

        return send_file('output.txt', as_attachment=True, download_name=f'{fname}.txt')
    else:
        return "Invalid PDF file."


if __name__ == '__main__':
    app.run(debug=True)
