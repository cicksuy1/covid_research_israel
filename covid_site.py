

from flask import Flask, Response, request,render_template,url_for

from CovidSite.generate_plots import globalvars_class as data_maker


app = Flask(__name__)

plot_maker = data_maker()
generate_static = [plot_maker.res_plot_3ma(),plot_maker.res_first_test_and_pos_ema()]
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/interact_ma", methods=['GET','POST'])
def interact_page():
    try:
        plot_maker.moving_avarge = int(request.form.get("ma",7))
        print(plot_maker.moving_avarge)
    except:
        plot_maker.moving_avarge = 7
        print("changed did not")
    image = None
    if request.method == 'POST':
        if request.form.get('save')=="on":
            image="/inter_plot_saved.png"
        else:
            image = "/inter_plot.png"
    return render_template("emainteractive.html", database_date=plot_maker.database_date, ma=plot_maker.moving_avarge,image=image)


#Responsive ma graph
@app.route("/inter_plot.png")
def interact_plot():
    return plot_maker.interact_positive_ema(ma=plot_maker.moving_avarge)


@app.route("/inter_plot_saved.png")
def interact_saved_plot():
    return plot_maker.interact_positive_ma_saved(ma=plot_maker.moving_avarge)




@app.route("/research")
def research():
    return render_template("research.html")



#plotting 3 different ma to a picture
@app.route("/plot_3_ma.png")
def mul_ema_plot():
    return generate_static[0]


#plotting positive and first and not first test plot with ma
@app.route("/positive_first_ma.png")
def first_test_pos_ma():
    return generate_static[1]

#plotting positive and first and not first test plot


@app.route("/positive_first.png")
def first_test_pos():
    return generate_static[2]



@app.route("/quantire.png")
def quantire_plot():
    return generate_static[3]


if __name__ == "__main__":

    import webbrowser
    webbrowser.open("http://127.0.0.1:5000/")
    app.run(debug=True)