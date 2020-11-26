# Covid-19-research-israel

A mini web application that contains research of Covid-19 pandemic in Israel and interactive graph.
### 
The main branch is for local web application.
###
Live application implementation is in different branch

## Table of contents
* [Data](#Data)
* [External python libraries used](#External-python-libraries-used)
* [Live-application](#Live-application)
* [Plotly JavaScript method](#Plotly-JS)
* [Screenshot](#Screenshot)
* [Contact](#contact)

python version: 3.7.9
## Data
The application fetches data from [https://data.gov.il/](https://data.gov.il/dataset/covid-19/resource/dcf999c1-d394-4b57-a5e0-9d014a62e046) by using its ckan API request.
The data requested as CSV inside JSON and transferred to pandas dataframe.
## How to run
make sure that all of the external libraries are installed and run the file
```
python flask_site.py
```
## External-python-libraries-used
* Flask 1.1.1
* Plotly 4.12.0
* Pandas 1.0.1
* Requests 2.22.0


## Plotly-JS
This is the method i used to show the plotly graph inside the html
```
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.6/d3.min.js"></script>

  <div class="chart" id="covid graph"> 
        <script>
            var graphs = {{json_plotly_graph | safe}};
            Plotly.plot('covid graph',graphs,{autorange: true});
        </script>
    </div>
```


## Live-application
https://covidgraphs.superus.tech/

## Screenshot
![screenshot](https://i.postimg.cc/VLw4FsdV/Screenshot-4.png)



## Contact
Created by Ben Baldut Mail: xxlostangle@gmail.com
