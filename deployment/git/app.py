from flask import Flask, render_template, request
from pymysql import connections
import os
import logging

app = Flask(__name__)

# Environment variables for database connection
DBHOST = os.environ.get("DBHOST") or "localhost"
DBUSER = os.environ.get("DBUSER") or "root"
DBPWD = os.environ.get("DBPWD") or "password"
DATABASE = os.environ.get("DATABASE") or "employees"
DBPORT = int(os.environ.get("DBPORT", 3306))

# Environment variables for S3 image URL and header name
#final push to git
S3_IMAGE_URL = os.environ.get('BACKGROUND_IMAGE_URL') #or "https://myvucket160896.s3.amazonaws.com/istockphoto-1456866576-612x612.jpg"
header_name = os.environ.get('HEADER_NAME') #or "Suma latha Pittala"

# Set up logging
logging.basicConfig(level=logging.INFO)

# Create a connection to the MySQL database
db_conn = connections.Connection(
    host=DBHOST,
    port=DBPORT,
    user=DBUSER,
    password=DBPWD,
    db=DATABASE
)

@app.route('/health', methods=['GET'])
def health_check():
    return "Healthy", 200
# Route for the home page
@app.route("/", methods=['GET', 'POST'])
def home():
    app.logger.info(f"Background image URL: {S3_IMAGE_URL}")
    return render_template('addemp.html', background_image=S3_IMAGE_URL,header_text=header_name)

# Route for the about page
@app.route("/about", methods=['GET', 'POST'])
def about():
    return render_template('about.html', background_image=S3_IMAGE_URL,header_text=header_name)

# Route to add an employee
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    primary_skill = request.form['primary_skill']
    location = request.form['location']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    try:
        cursor.execute(insert_sql, (emp_id, first_name, last_name, primary_skill, location))
        db_conn.commit()
        emp_name = f"{first_name} {last_name}"
    finally:
        cursor.close()

    return render_template('addempoutput.html', name=emp_name, background_image=S3_IMAGE_URL,header_text=header_name)

# Route to get employee information
@app.route("/getemp", methods=['GET', 'POST'])
def GetEmp():
    return render_template("getemp.html", background_image=S3_IMAGE_URL,header_text=header_name)

# Route to fetch employee data
@app.route("/fetchdata", methods=['GET', 'POST'])
def FetchData():
    emp_id = request.form['emp_id']

    output = {}
    select_sql = "SELECT emp_id, first_name, last_name, primary_skill, location FROM employee WHERE emp_id=%s"
    cursor = db_conn.cursor()

    try:
        cursor.execute(select_sql, (emp_id,))
        result = cursor.fetchone()
        
        if result:
            output["emp_id"] = result[0]
            output["first_name"] = result[1]
            output["last_name"] = result[2]
            output["primary_skills"] = result[3]
            output["location"] = result[4]
    except Exception as e:
        app.logger.error(f"Error fetching data: {e}")
    finally:
        cursor.close()

    return render_template("getempoutput.html", id=output.get("emp_id"), fname=output.get("first_name"),
                           lname=output.get("last_name"), interest=output.get("primary_skills"), 
                           location=output.get("location"), background_image=S3_IMAGE_URL,header_text=header_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81, debug=True)
