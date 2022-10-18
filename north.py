import os, sqlite3, sys, urllib.request
from flask import Flask, render_template, request, redirect, url_for, Response, flash, send_from_directory

app = Flask(__name__)  # app = Flask('yourapplication')  # app = Flask(__name__.split('.')[0]) #print(app.config) #print(app.url_map)

os.chdir(os.path.join(os.path.dirname(__file__)))
databasename = "ndc.db" #"Trusted Vault" #"ChromeData.db"# "Northwind.db"

databasepath = os.path.join(os.path.dirname(sys.argv[0]), databasename )





staticdir = os.path.join(app.root_path, 'static')
if not os.path.exists(staticdir):
  os.mkdir(staticdir)
urllib.request.urlretrieve("https://img.icons8.com/external-justicon-lineal-color-justicon/64/000000/external-monkey-animal-justicon-lineal-color-justicon.png", os.path.join(app.root_path, 'static', 'favicon.ico'))

def get_tables_dictionary():
    global databasepath
    connection = sqlite3.connect(databasepath)
    cursor = connection.cursor()
    a = cursor.execute("select name from sqlite_master").fetchall()
    thedictionary = {}
    for i in a:
        try:
          q = cursor.execute("select * from '{n}'".format(n=i[0]))
          field_names = [i[0] for i in q.description]
          thedictionary[i[0].upper()]= field_names
        except:
            continue
    cursor.close()
    return thedictionary



def get_sql_data_for_col(table):
    global databasepath
    connection = sqlite3.connect(databasepath)
    cursor = connection.cursor()
    return cursor.execute("SELECT * FROM "+table).fetchall()


@app.route("/")
@app.route("/home")
@app.route("/index")
def mainpage():
  thedictionary = get_tables_dictionary()
  return render_template("index.html", thedictionary=thedictionary)




def display_table(name):
      thedictionary = get_tables_dictionary()
      columns_in_this_table = []
      listoflists = []
      for column in thedictionary[name]:
          columns_in_this_table.append(column)
          data = get_sql_data_for_col(name)
      listoflists.append(data)

      return render_template("table.html", thedictionary=thedictionary, 
      columns_in_this_table=columns_in_this_table, 
      listoflists=listoflists[0],
      tablename=name)
      



def deregister():
    global databasepath
    connection = sqlite3.connect(databasepath)
    db = connection.cursor()
    table = request.form.get("table")
    column = request.form.get("column")
    value = request.form.get("value")
    query = "DELETE FROM {table} WHERE {column} = {value}".format(table=table, column=column, value=value)
    db.execute(query)
    connection.commit()
    currentpage = "/table/{name}".format(name=table) 
    db.close()
    return redirect(currentpage)


querylist = []

def custom_sql():
        global databasepath
        connection = sqlite3.connect(databasepath)
        db = connection.cursor()
        query = request.form.get("query")
        querylist.append(query)
        q = db.execute(query)
        a = q.fetchall()
        tables_col = get_tables_dictionary()
        try:
            field_names = [i[0] for i in q.description]
            columns_in_this_table = field_names      
            return render_template("table.html", 
             querylist=querylist,
             columns_in_this_table= columns_in_this_table,
             thedictionary=tables_col, 
             listoflists=a,tablename="Custom query")
        except:
            return redirect("/")
        finally:
             connection.commit()



@app.route('/favicon.ico') 
def favicon(): 
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

#@app.errorhandler(404)
#def page_not_found(error):
#    return render_template('404.html'), 404

@app.route("/javasCript")
@app.route("/js")
def js():
    return render_template("jsconsole.html")

app.add_url_rule("/table/<name>", view_func=display_table)
app.add_url_rule("/", view_func=mainpage)
app.add_url_rule("/deregister",view_func=deregister, methods=['POST'])
app.add_url_rule("/custom",view_func=custom_sql, methods=['POST'])



#         <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/css/bootstrap.min.css">
#       <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.1/js/bootstrap.min.js"></script>
# #marginalize{margin-top:30px;}
templates_dictionary = {}
js_dictionary = {}

templates_dictionary["layoutdothtml"] = """
<!DOCTYPE html>

<html lang="en">
    <head>
        <meta name="viewport" content="initial-scale=1, width=device-width">
        <title>SQL Demo</title>


        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Sofia&effect=neon|outline|emboss|shadow-multiple">

        <style>
            body {
                background-color: lavender;
                text-align: center;
                font-family: 'Segoe UI', Tahoma, sans-serif;
                }
            form {margin:15px; text-align:left;}

            td:hover{
                font-weight: bold;
                font-family: Verdana, sans-serif
            }
            #table_name{
                color:red;
                margin: 0 auto;
                margin-top: 50px;
            }
            
            #Textarea1{max-width: 95%
            font-size:large;}

        </style>
    </head>
    <body>

      <nav  class="navbar navbar-expand-sm bg-dark ">
    <div class="container-fluid">
      <div class="navbar-header">
        <a class="navbar-brand" href="{{url_for("mainpage")}}">MainPage</a>
        <a class="navbar-brand" href="/js">JS</a>
      </div>
      <ul class="navbar-nav">
         {% for k,v in thedictionary.items() %}
        <li class="nav-item"><a class="nav-link" href='/table/{{k}}'>{{k}}</a></li>
        {%endfor%}
      </ul>
      </nav>
        <div id="marginalize">{% block body %}{% endblock %}</div>
    </body>
</html>
"""

templates_dictionary["indexdothtml"] = '''
{% extends "layout.html" %}
{% block body %}
<div style="margin-top:50px;, text-align: left;">
  <fieldset style="text-align:left;">
    <legend>Query:</legend>

                            <form action="/custom" method="post">
                              
                            <label for="Textarea1" class="form-label">Type your Query here!</label>
                            <textarea rows="8" style="width:95%;" id="Textarea1" "class="form-control"  name=query placeholder="SELECT EmployeeID, LastName FROM Employees" type="text"></textarea>
                            <input onclick=handleQuery() class="btn btn-primary mb-3" type="submit" value="Submit">
                            </form></div>
                            <input style="text-align:left"; class="btn btn-info"  type ="button" onclick = "sayHello()" value = "Say Hello" />
  </fieldset>
  <form style="text-align:left;" >
  <input type="hidden" name=query value="select * from sqlite_master">
  <button type="sumbit" formmethod="POST" formaction="/custom" formtarget="_blank" class="btn btn-warning" >select * from sqlite_master</button>
  </form>
{% endblock %}
'''

templates_dictionary["tabledothtml"] = '''
{% extends "layout.html" %}
{% block title %}TABLE - {{tablename}} {% endblock %}
{% block body %}

<h3 id="table_name" data-bs-toggle="tooltip" data-bs-placement="bottom" title="{{querylist}}">{{tablename}}</h3>
<div class="container-fluid">
<table class="table table-hover">
        <thead>
            <tr>
            {% for i in columns_in_this_table %}
                <th>{{i}}</th>
            {%endfor%}
            </tr>
        </thead>
        <tbody>
            {% for atuble in listoflists %}
                <tr>
                   {% for j in atuble %} 
                    <td>{{ j  }}</td>

                    {% endfor %}
                    {%if tablename  != "Custom query"%}
                      <td style="width:10%">
                
                              <form action="/deregister" method="post">
                              <input  name=table value={{ tablename }} type="hidden">
                              <input  name=column value={{ columns_in_this_table[0] }} type="hidden">
                              <input  name=value value={{ atuble[0] }} type="hidden">
                              <input  onclick=sayHello() type="submit" class="btn btn-danger" value="Delete row">
                              </form>
                      </td>
		{% endif %}
                </tr>
            {% endfor %}
        </tbody>

</table>
</div>
{% endblock %}
'''
# <button onclick=confirm("hi") type="submit" formtarget=iframename formaction="/action_page2.php"  formmethod="post" >button as Admin</button>





js_dictionary["hellodotjs"] = '''
function sayHello() {
   a = confirm("Are you sure?")
   alert(a)
}

function handleQuery(){
var x = document.getElementById("Textarea1");
alert(x.value)
}


'''



def  add_js():
    first_template = str(os.getcwd()) + "\\" + "templates" + "\\" + list(templates_dictionary.keys())[0].replace("dothtml","") +  ".html"
    for k,v in js_dictionary.items():
        nm = k.replace("dotjs","")
        nm = nm + ".js"
        thelinkingtext = """<script type = "text/javascript" src = "/static/{filenm}" ></script>""".format(filenm=nm)
        dirr = str(os.getcwd()) + "\\" + "static"
        if not os.path.exists(dirr):
            os.mkdir(str(os.getcwd()) + "\\" + "static")
        mypath = str(os.getcwd()) + "\\" + "static" + "\\" + nm 
        with open(mypath, "w") as f:
            f.write(v)
        with open(first_template, "a") as f:
            f.write(thelinkingtext)



def build_templates():
    for k,v in templates_dictionary.items():
        nm = k.replace("dothtml","")
        dirr = str(os.getcwd()) + "\\" + "templates"
        if not os.path.exists(dirr):
            os.mkdir(str(os.getcwd()) + "\\" + "templates")
        mypath = str(os.getcwd()) + "\\" + "templates" + "\\" + nm + ".html"
        with open(mypath, "w") as f:
            f.write(v)
        

def see_ip():
    import socket 
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    s.connect(('10.255.255.255', 1))
    print(s.getsockname()[0])
    print(socket.gethostbyname(socket.gethostname()))
    print(socket.gethostbyname("localhost"))


if __name__ == '__main__':
    build_templates()
    add_js()
    app.run(host='0.0.0.0', debug = True, port="80")  # accessible from 169.254.51.47, 127.0.0.1 or 192.168.1.179
    pass



