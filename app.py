from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/plot/")
def plot():
    import pandas_datareader.data as web
    import datetime
    from bokeh.plotting import figure, output_file, show
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2019, 1, 1)
    end = datetime.datetime(2020, 4, 8)
    company = "TSLA"
    df = web.DataReader(company, "stooq")

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]

    df["Middle"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Open - df.Close)

    p = figure(x_axis_type="datetime", width=1000, height=300)
    p.title.text = "Candlestick Chart of " + company
    p.grid.grid_line_alpha = 0.3
    hours_12 = 12 * 60 * 60 * 1000

    p.segment(df.index, df.High, df.index, df.Low, color="gray")

    p.rect(
        df.index[df.Status == "Increase"],
        df.Middle[df.Status == "Increase"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="green",
        line_color="green",
    )
    p.rect(
        df.index[df.Status == "Decrease"],
        df.Middle[df.Status == "Decrease"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="red",
        line_color="red",
    )

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files

    return render_template(
        "plot.html",
        script1=script1,
        div1=div1,
        cdn_js=cdn_js,
        cdn_css=cdn_css,
        company=company,
    )


@app.route("/plot/", methods=["POST"])
def plot_post():
    import pandas_datareader.data as web
    import datetime
    from bokeh.plotting import figure, output_file, show
    from bokeh.embed import components
    from bokeh.resources import CDN

    start = datetime.datetime(2019, 1, 1)
    end = datetime.datetime(2020, 4, 8)

    company = request.form["company"]
    df = web.DataReader(company, "stooq")

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]

    df["Middle"] = (df.Open + df.Close) / 2
    df["Height"] = abs(df.Open - df.Close)

    p = figure(x_axis_type="datetime", width=1000, height=300)
    p.title.text = "Candlestick Chart of " + company
    p.grid.grid_line_alpha = 0.3
    hours_12 = 12 * 60 * 60 * 1000

    p.segment(df.index, df.High, df.index, df.Low, color="gray")

    p.rect(
        df.index[df.Status == "Increase"],
        df.Middle[df.Status == "Increase"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="green",
        line_color="green",
    )
    p.rect(
        df.index[df.Status == "Decrease"],
        df.Middle[df.Status == "Decrease"],
        hours_12,
        df.Height[df.Status == "Increase"],
        fill_color="red",
        line_color="red",
    )

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    cdn_css = CDN.css_files

    return render_template(
        "plot.html",
        script1=script1,
        div1=div1,
        cdn_js=cdn_js,
        cdn_css=cdn_css,
        company=company,
    )


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/settings/")
def settings():
    return render_template("settings.html")


if __name__ == "__main__":
    app.run(debug=True)
