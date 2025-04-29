from flask import Flask, Blueprint, render_template, request, send_from_directory, send_file
import os, subprocess
import numpy as np
from app.plots import generate_plots
app = Flask(__name__)
views = Blueprint('views', __name__)



original = None                                                                         # we use this to come back to original file after filtering (later on)

# Define routes within the blueprint
@views.route('/')
def home():
    return render_template('index.html')                                                # this shows the daily prophet page upon opening site

@views.route('/upload')
def upload():
    return render_template('upload.html')                                               # this shows the file upload page

@views.route('/upload', methods=['POST'])                                             
def uploaded():
    global original
    
    file = request.files['logfile']  
    house = request.form.get('house')

    strippedname = file.filename[:-4]+".csv"                                            # get the bare name to make a csv
    csv_path = os.path.join('visualizations', strippedname)
    original = strippedname
    log_path = os.path.join('uploads', file.filename) 
    file.save(log_path)                                                                 # saves file to subdir uploads/
    subprocess.run(['bash', 'bash_scripts/validate.sh', log_path, csv_path])            # runs the script validate.sh on file
    
    with open('tmp/logtype.txt', 'r') as f:
        log_type = f.read().strip().lower()
        if (log_type == 'none') :
            return render_template('error.html')

    csv_path = os.path.join('visualizations', strippedname)                             # path to the csv my script made

    return render_template('results.html',filename=strippedname,house=house,log_type=log_type)            # shows result.html with some parameters

@views.route('/view_csv/', methods=['GET', 'POST'])
def view_csv():
    filename = request.args.get('filename')
    house = request.args.get('house')
    csv_path = os.path.join('visualizations', filename)
    global original

    # Get log type
    with open('tmp/logtype.txt', 'r') as f:
        log_type = f.read().strip().lower()

    # Set up header and delimiter
    header = []
    delim = ',' if log_type in ['apache', 'syslog'] else '!'        # i have used '!' as a delimiter for android logs because content contained ','
    shown=filename

    if log_type == "apache":                                        # here i have hardcoded header values so i can assign id to them for later use during filtering the csv
        header = [
            {"name": "Line ID", "id": 0},
            {"name": "Day", "id": 1},
            {"name": "Time", "id": 2},
            {"name": "Level", "id": 3},
            {"name": "Content", "id": 4},
            {"name": "Event", "id": 5},
            {"name": "Template", "id": 6},
        ]
        cols = [3,5]                                                # i have selected certain columns that make sense for filtering (line ID, content etc. isn't useful)
    elif log_type == "syslog":
        header = [
            {"name": "Line Id", "id": 0},
            {"name": "Time", "id": 1},
            {"name": "Level", "id": 2},
            {"name": "Component", "id": 3},
            {"name": "PID", "id": 4},
            {"name": "Content", "id": 5},
        ]
        cols = [2,3,4]
    elif log_type == "android":
        header = [
            {"name": "Line Id", "id": 0},
            {"name": "Time", "id": 1},
            {"name": "PID", "id": 2},
            {"name": "TID", "id": 3},
            {"name": "Level", "id": 4},
            {"name": "Component", "id": 5},
            {"name": "Content", "id": 6},
        ]
        cols = [2,3,4,5]
        
    # Handle date filtering (unchanged)
    if request.method == 'POST':
        start_time = request.form['start_time']                                         # this is for filtering the csv from and to given dates
        end_time = request.form['end_time']
        filtered_csv = os.path.join('visualizations', f"filtered_{filename}")
        cmd = [
            'bash', 'bash_scripts/filter_csv.sh',
            start_time, end_time, csv_path, filtered_csv
        ]
        subprocess.run(cmd)
        csv_path = filtered_csv
        shown=filename
        
        csv_data = []
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            for line in lines[1:]:
                csv_data.append([item.strip() for item in line.split(delim)])
                
            return render_template('display.html',
                            filename=csv_path,
                            header=header,
                            csv_data=csv_data,
                            house=house,
                            log_type=log_type,
                            cols=cols,
                            og=original)

#filename - file to be displayed, house - for color theme, log_type - for filtering, original - for coming back after filtering, cols - columns which will have dropdown for filtering

    # Read CSV data
    csv_data = []
    with open(csv_path, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            csv_data.append([item.strip() for item in line.split(delim)])
            
    filters = {}
    for idx in cols:
        val = request.args.get(f'filter_{idx}', '')
        if val:
            filters[idx] = val

    # apply filters to csv_data

    if filters:
        csv_data = [row for row in csv_data if all(row[idx] == req for idx, req in filters.items())]    # this does multi-column filtering 
        
        with open('filtered.csv', 'w') as f:
            for row in csv_data:
                line = delim.join(str(cell) for cell in row)  # join each row with commas
                f.write(line + '\n')  
                shown='filtered.csv'


    # extract unique values for each column - makes the drop-down filter possible without hardcoding
    unique_values = {col: set() for col in cols}
    for row in csv_data:
        for idx, value in enumerate(row):
            if idx in unique_values:
                unique_values[idx].add(value)
    unique_values = {k: list(v) for k, v in unique_values.items()}

    return render_template('display.html',
                            displayed=shown,
                            filename=filename,
                            header=header,
                            csv_data=csv_data,
                            house=house,
                            unique_values=unique_values,
                            log_type=log_type,
                            cols=cols,
                            og=original)



@views.route('/plot_options/<filename>/<house>', methods=['POST','GET'])
def plot_options(filename, house):
    csv_path=os.path.join('visualizations',filename[:-4]+".csv")
    output_dir = os.path.join('static', 'plots', filename[:-4])
    
    
    with open('tmp/logtype.txt', 'r') as f:
        log_type = f.read().strip().lower()

    
    
    if request.method=='POST':
        start_date = request.form.get('from', '')
        end_date = request.form.get('to', '')
        filtered_csv = os.path.join('visualizations', f"filtered_{filename}")
        cmd = [
            'bash', 'bash_scripts/filter_csv.sh',
            start_date, end_date, csv_path, filtered_csv
        ]
        subprocess.run(cmd)
        csv_path = filtered_csv
        
    subprocess.run(['bash','bash_scripts/epoch.sh',csv_path])
    generate_plots(log_type,"visualizations/times.csv", output_dir)
    if log_type == 'apache':
        plot_files = {
        "Events over time": ["plot1.png"],
        "Level Distrbution": ["plot2.png"],
        "EventID Distrbution": ["plot3.png"]
    }
    elif log_type == 'syslog':
        plot_files = {
        "Top Log Sources": ["plot1.png"],
        "Level Distrbution": ["plot2.png"],
        "Severity Breakdown": ["plot3.png"]
    }
    elif log_type == 'android':
        plot_files = {
            "Level Breakdowns": ["plot1.png"],
            "Traffic Trends": ["plot2.png"],
            "Event Component Distrbution": ["plot3.png"]
        }

    return render_template('plots.html', filename=filename, plot_files=plot_files, house=house)

    
@views.route('/download/<filename>')
def download(filename):
    return send_from_directory('visualizations',filename)



@views.route('/download_jpeg')
def download_jpeg():
    filename = request.args.get('filename')
    plotname = request.args.get('plotname')
    house = request.args.get('house','muggle')

    png_path = os.path.join('static', 'plots', filename, plotname)
    jpeg_path = png_path.replace('.png', f'_{house}.jpeg')

    if not os.path.exists(jpeg_path):
        from PIL import Image
        im = Image.open(png_path).convert("RGB")
        im.save(jpeg_path, "JPEG")

    return send_file(jpeg_path, as_attachment=True)

# Register the blueprint with a URL prefix
app.register_blueprint(views, url_prefix='/views')



if __name__ == '__main__':
    app.run(debug=True)
