from flask import Flask, request, render_template, redirect, url_for, flash
import os
from werkzeug import secure_filename
from pybtex.database.input import bibtex
from sqlalchemy import create_engine, MetaData, Table

UPLOAD_FOLDER='/files/uploads'
ALLOWED_EXTENSIONS=set(['bib'])
parser=bibtex.Parser()


app=Flask(__name__)
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER
engine=create_engine('sqlite:///bib.db',convert_unicode=True)
metadata=MetaData(bind=engine)
collections=Table('bibfile',metadata,autoload=True)
coll_names=[]
current_dir=os.getcwd()

@app.route("/",methods=["GET","POST"])
@app.route("/main")
def index():
	print coll_names
	return render_template("main.html",coll_names=coll_names)



@app.route("/insert", methods=["GET","POST"])
def insert():
	message=""
	print request.args, request.method
	if request.method=='GET' and 'filename' in request.args:
		con=engine.connect()
		filename=request.args["filename"]
		coll_name='collection_noname'
		if 'collname' in request.args:
			coll_name=request.args["collname"]
		
		filename=current_dir+"/"+UPLOAD_FOLDER+filename
		bib_data=parser.parse_file(str(filename))
		i=0
		for each in bib_data.entries.keys():
			try: 
				ref_tag=bib_data.entries[each].fields['keywords']
				author=bib_data.entries[each].fields['author']
				journal=bib_data.entries[each].fields['journal']
				volume=bib_data.entries[each].fields['volume']
				pages=bib_data.entries[each].fields['pages']
				year=bib_data.entries[each].fields['year']
				title=bib_data.entries[each].fields['title']
				collection=coll_name
				#print ref_tag,author,journal,volume,pages,year,title,collection
				con.execute(collections.insert(),ref_tag=ref_tag,author=author,journal=journal,volume=volume,pages=pages,year=year,title=title,collection=collection)
			except KeyError as e:
				i+=1
				
		message="Upload successful!"
		con.close()		
		coll_names.append(coll_name)
	
		return render_template("main.html",coll_names=coll_names)
	else:
		return render_template("insert.html",msg=message)

@app.route("/query",methods=["GET","POST"])
def query():
	results=''
	if 'search' in request.form:
		query=request.form['search']
		print query
		try:
			result=engine.execute('select title from bibfile where '+str(query))
			results=[r for r in result]
		
		except:
			print 'result'
			
	return render_template("query.html",result=results)

def allowed_file(filename):
	return '.' in filename and filename.rsplit('.',1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload',methods=['GET','POST'])
def upload_file():
	if request.method=='POST':
		print "Uploading..."
		if 'file' in request.files:
			file=request.files['file']
			collname=request.form['collname']
		if file and allowed_file(file.filename):
			print "Loading..."
			filename=secure_filename(file.filename)
			uploads_dir=current_dir+"/"+UPLOAD_FOLDER+filename
			file.save(uploads_dir)
			return redirect(url_for('insert',filename=filename,collname=collname))
		return


if __name__=='__main__':
	app.run(port=8000,debug=True)