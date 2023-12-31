from flask import *
import os, shutil
from werkzeug.utils import secure_filename
from utils import stem, stop_words
import math
import uuid


app = Flask(__name__)
ALLOWED_EXTENSIONS = {'txt'}


@app.route('/')
def main():
    return render_template("./index.html")

@app.route('/upload_query', methods=['POST'])
def upload_query():
    if request.method == 'POST':
        # Get the list of files from webpage
        directory_id = uuid.uuid1()
        files = request.files.getlist("file")
        parent_dir = "/root/irs/"
        path = os.path.join(parent_dir, 'dir_'+str(directory_id))
        os.mkdir(path)
        # Iterate for each file in the files List, and Save them
        for file in files:
            # file.save(file.filename, './uploads')
            file.save(os.path.join(path, secure_filename(file.filename)))

        return render_template("query.html", dir_id = directory_id)

@app.route('/query_result', methods=['POST'])
def query_result():
    if request.method == 'POST':
        query = request.form.get("query")
        directory_id = request.form.get("directory_id")
        # print(directory_id)
        directory = '/root/irs/dir_'+directory_id+'/'
        file_count=1
        for path in os.scandir(directory):
            if path.is_file():
                file_count += 1
                # print(file_count)
        # final_terms_list = 
        words_in_doc=dict()
        doc_id_terms=dict()
        doc_name = dict()
        terms = set()
        doc_id = 1
        for filename in os.listdir(directory):
            f = os.path.join(directory, filename)
            # checking if it is a file
            if os.path.isfile(f):
                with open(os.path.join(directory, filename), 'r') as f:
                    contents = f.read().lower().replace(',','').replace('.','').replace('-', ' ')
                f.close
                words_list = contents.split()
                words_list = stem(words_list)
                words_in_doc['d'+str(doc_id)]=words_list
                doc_name['d'+str(doc_id)]=filename
                print(doc_name)
                words_list = set(words_list)
                stop_words_removed = words_list.difference(stop_words)
                doc_id_terms['d'+str(doc_id)]=stop_words_removed
                doc_id+=1
                terms = terms.union(stop_words_removed)
        terms = sorted(terms)
        terms = list(terms)

        # print(len(terms))
        word_freq=dict()
        doc_id=1
        for i in range(1,file_count):
            # init dict value to empty list
            word_freq['d'+str(doc_id)]=[]
            for term in terms:
                word_freq['d'+str(doc_id)].append(words_in_doc['d'+str(doc_id)].count(term))
            doc_id+=1

        # print(word_freq)

        # Calculating max_freq from word_freq dict
        max_word_freq = dict()
        doc_id = 1
        for i in range(1,file_count):
            max_word_freq['d'+str(doc_id)]=max(word_freq['d'+str(doc_id)])
            # print(len(word_freq['d'+str(doc_id)]))
            doc_id+=1
        # print(max_word_freq)

        term_occurance_in_docs=dict()

        for term in terms:
            term_index = 0
            term_occurance_in_docs[term]=0
            for doc_id in range(1,file_count):
                term_occurance_in_docs[term]+= 1 if word_freq['d'+str(doc_id)][term_index]>=1 else 0
                term_index+=1
        # print(term_occurance_in_docs)

        wd_vector = dict()
        c1 = 0.6
        c2 = 0.4
        N=5
        for doc_id in range(1,file_count):
            # init empty list and append upcoming wd values
            wd_vector['d'+str(doc_id)]=[]
            for term in range(len(terms)):
                term_inside_parentheses = c1 + c2 * word_freq['d'+str(doc_id)][term] / max_word_freq['d'+str(doc_id)]
                log_term = math.log10(N / term_occurance_in_docs[terms[term]])
                wd_vector['d'+str(doc_id)].append(term_inside_parentheses * log_term)
        # print(wd_vector)

        query_terms = query.lower().replace('?','').split()
        query_terms = set(query_terms)
        query_terms = query_terms.difference(stop_words)
        sorted(query_terms)
        query_terms = list(query_terms)
        # print(query_terms)
        query_terms_freq=[]
        doc_id=1
        for term in terms:
            query_terms_freq.append(query_terms.count(term))

        # ranking
        doc_rank=dict()
        for doc_id in range(1,file_count):
            doc_rank['d'+str(doc_id)]=0
            for i in range(len(query_terms_freq)):
                if query_terms_freq[i]>=1:
                    doc_rank['d'+str(doc_id)] += query_terms_freq[i] * wd_vector['d'+str(doc_id)][i]
        doc_ranks_processed = dict(sorted(doc_rank.items(), key=lambda item: item[1], reverse =  True))
        # print(doc_ranks_processed)

        doc_names_resolved = {}

        for key, value in doc_ranks_processed.items():
            print(key, value)
            doc_names_resolved[doc_name[key]]=value
        
        print(doc_names_resolved)
        try:
            shutil.rmtree(directory)
            # print("Directory removed successfully")
        except OSError as o:
            pass
            # print(f"Error, {o.strerror}: {directory}")
        return render_template("results.html", doc_ranks=doc_names_resolved)

@app.route('/download')
def downloadFile ():
    path = "/root/irs/example_files/sample_files.zip"
    return send_file(path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
