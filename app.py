from flask import Flask, render_template,request
from flask_wtf import FlaskForm
from wtforms import  SubmitField, SelectField
from wtforms.validators import DataRequired
import pandas as pd
from preprocessor import preprocess
from analysis import country_list, year_list, fetch_medal_tally, overall_analysis, participating_nations_over_time, most_successful_athletes,sports_list,country_wise_medal_tally, country_event_heatmap, most_successful_athletes_of_country, men_vs_women, weight_v_height
import plotly
import plotly.express as px
import plotly.figure_factory as ff
import json
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv('athlete_events.csv')
region_df = pd.read_csv('noc_regions.csv')
countries =[]
app = Flask(__name__)
app.config["SECRET_KEY"] = "secretkey"
preprocessed_df = pd.read_csv('processedfile.csv')

class Medals(FlaskForm):
    Country = SelectField('Select Country', choices=country_list(preprocess(df, region_df)),  validators=[DataRequired()])
    Years = SelectField('Select Year', choices=year_list(preprocess(df, region_df)), validators=[DataRequired()])
    submit = SubmitField('Submit')


class Sports(FlaskForm):
    Sport = SelectField('Select Sport', choices=sports_list(preprocess(df, region_df)),  validators=[DataRequired()])
    submit = SubmitField('Submit')

class countryForm(FlaskForm):
    Country = SelectField('Select Country', choices=country_list(preprocess(df, region_df)),  validators=[DataRequired()])
    submit = SubmitField('Submit')


class AthleteMedal(FlaskForm):
    Medal = SelectField('Select Medal', choices=['Gold', 'Silver'])
    submit = SubmitField('Submit')
    
@app.route('/')
def home():
    #return render_template('home.html', tables=[preprocessed_df.to_html()], titles=[''])
    return render_template('home.html')

@app.route('/medaltally',methods=['GET',"POST"])
def medalTally():
    form = Medals()
    if form.validate_on_submit():
        country = form.Country.data
        year = form.Years.data
        print("form",form.Country.data)
        medals_total, header = fetch_medal_tally(preprocessed_df, year, country)
    elif request.method == 'GET':
        medals_total,header = fetch_medal_tally(preprocessed_df,'Overall',"Overall")
    df_length = len(medals_total)
    print("Length",df_length)
    print(type(medalTally))
    return render_template('medaltally.html', form=form, header=header, medal_tally=medals_total,df_length=df_length)

@app.route('/overall',methods=['GET','POST'])
def overall():
    form = Sports()
    
    if form.validate_on_submit():
        sport = form.Sport.data
        analysis, header = overall_analysis(preprocessed_df)
        nations_over_time = participating_nations_over_time(preprocessed_df, 'region')
        fig = px.line(nations_over_time, x='Edition', y="region", labels={"Edition": "Year", "No of countries": "Number of Countries"})
        graph1Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        nations_over_time = participating_nations_over_time(preprocessed_df, 'Event')
        fig = px.line(nations_over_time, x='Edition', y="Event",labels={"Edition": "Year", "Event": "Event"})
        graph2Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        athletes_over_time = participating_nations_over_time(preprocessed_df, 'Name')
        fig = px.line(athletes_over_time, x='Edition', y="Name",labels={"Edition": "Year", "Name": "Athletes"})
        graph3Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

        fig, ax = plt.subplots(figsize=(15, 15))
        heatmap_df = df.drop_duplicates(['Year', 'Sport', 'Event'])
        ax = sns.heatmap(heatmap_df.pivot_table(index="Sport", columns="Year",values="Event", aggfunc="count").fillna(0).astype('int'), annot=True)
        plt.savefig('static/heatmap.png', bbox_inches='tight')

        successful_athletes = most_successful_athletes(preprocessed_df, sport)
        
    elif request.method == "GET":
        
        analysis,header = overall_analysis(preprocessed_df)
        nations_over_time = participating_nations_over_time(preprocessed_df,'region')
        fig = px.line(nations_over_time, x='Edition', y="region", labels={
                      "Edition": "Year", "No of countries": "Number of Countries"})
        graph1Json = json.dumps(fig,cls=plotly.utils.PlotlyJSONEncoder)
        
        nations_over_time = participating_nations_over_time(preprocessed_df, 'Event')
        fig = px.line(nations_over_time, x='Edition', y="Event", labels={"Edition": "Year", "Event": "Event"})
        graph2Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        athletes_over_time = participating_nations_over_time(preprocessed_df, 'Name')
        fig = px.line(athletes_over_time, x='Edition', y="Name",labels={"Edition": "Year", "Name": "Athletes"})
        graph3Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        fig,ax = plt.subplots(figsize=(15,15))
        heatmap_df = df.drop_duplicates(['Year', 'Sport', 'Event'])
        ax = sns.heatmap(heatmap_df.pivot_table(index="Sport", columns="Year",values="Event", aggfunc="count").fillna(0).astype('int'), annot=True)
        plt.savefig('static/heatmap.png', bbox_inches='tight')
        
        successful_athletes = most_successful_athletes(preprocessed_df, 'Overall')
    return render_template('overall.html', analysis=analysis, header=header, graph1JSON=graph1Json, graph2JSON=graph2Json, graph3JSON=graph3Json, successful_athletes=successful_athletes, form=form)
    

@app.route('/country', methods=['GET', 'POST'])
def country():
    form = countryForm()
    header = "Country wise analysis"
    countryname = form.Country.data
    if form.validate_on_submit():
        header = "Analysis of " + countryname
        header2 = countryname + " medal tally over the years"
        header3 = countryname + " is good in following sports!!!"
        header4 = "Top 15 players of " + countryname
    
        medals_over_time = country_wise_medal_tally(preprocessed_df, countryname)
        fig = px.line(medals_over_time, x='Year', y="Medal")
        graph1Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        fig, ax = plt.subplots(figsize=(15, 15))
        heatmap_df = country_event_heatmap(preprocessed_df, countryname)
        ax = sns.heatmap(heatmap_df.pivot_table(index="Sport", columns="Year", values="Medal", aggfunc="count").fillna(0).astype('int'), annot=True, annot_kws={"size": 5})
        plt.savefig('static/heatmap_country.png', bbox_inches='tight')
        
        top15_athletes = most_successful_athletes_of_country(preprocessed_df, countryname)
                
    else:
        graph1Json = {}
        header2 = ""
        header3 = ""
        header4 = ""
        top15_athletes = pd.DataFrame()
    return render_template('country.html', form=form, header=header,header2 = header2,header3 = header3, header4 = header4, graph1JSON=graph1Json,top15_athletes=top15_athletes)


@app.route('/athelete', methods=['GET', 'POST'])
def athelete():
    form = AthleteMedal()
    form1 = Sports()

    athlete_df = preprocessed_df.drop_duplicates(subset=['Name', 'region'])
    header1 = "Distribution of age"
    x1 = athlete_df['Age'].dropna()
    x2 = athlete_df[athlete_df['Medal'] == 'Gold']['Age'].dropna()
    x3 = athlete_df[athlete_df['Medal'] == 'Silver']['Age'].dropna()
    x4 = athlete_df[athlete_df['Medal'] == 'Bronze']['Age'].dropna()
    
    fig = ff.create_distplot([x1, x2, x3, x4], ['Overall Age', 'Gold Medalist',
                                                'Silver Medalist', 'Bronze Medalist'], show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    
    graph1Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    
    x = []
    name = []
    famous_sports = ['Basketball', 'Judo', 'Football', 'Tug-Of-War', 'Athletics',
                     'Swimming', 'Badminton', 'Sailing', 'Gymnastics',
                     'Art Competitions', 'Handball', 'Weightlifting', 'Wrestling',
                     'Water Polo', 'Hockey', 'Rowing', 'Fencing',
                     'Shooting', 'Boxing', 'Taekwondo', 'Cycling', 'Diving', 'Canoeing',
                     'Tennis', 'Golf', 'Softball', 'Archery',
                     'Volleyball', 'Synchronized Swimming', 'Table Tennis', 'Baseball',
                     'Rhythmic Gymnastics', 'Rugby Sevens',
                     'Beach Volleyball', 'Triathlon', 'Rugby', 'Polo', 'Ice Hockey']
    if form.validate_on_submit():
        medal = form.Medal.data
    else:
        medal = "Gold"
    print("Amogh medal",medal)
    header2 = "Distribution of age with respect to sport for " + medal + " medal"
    for sport in famous_sports:
        temp_df = athlete_df[athlete_df['Sport'] == sport]
        x.append(temp_df[temp_df['Medal'] == medal]['Age'].dropna())
        name.append(sport)
        

    fig = ff.create_distplot(x, name, show_hist=False, show_rug=False)
    fig.update_layout(autosize=False, width=1000, height=600)
    graph2Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
  
    header3 = "Height vs Weight "
    
    if form1.validate_on_submit():
        temp_df = weight_v_height(preprocessed_df, form1.Sport.data)
    else:
        temp_df = weight_v_height(preprocessed_df, "Overall")
    fig, ax = plt.subplots(figsize=(15, 15))
    ax = sns.scatterplot(temp_df['Weight'], temp_df['Height'],hue=temp_df['Medal'], style=temp_df['Sex'], s=60)
    plt.savefig('static/scatter_sport.png', bbox_inches='tight')
    header4 = "Men vs Women participation over the years"
    final = men_vs_women(preprocessed_df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    fig.update_layout(autosize=False, width=1000, height=600)
    graph3Json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('athelete.html', form=form, form1=form1, graph1JSON=graph1Json, header1=header1, graph2JSON=graph2Json, header2=header2, header3=header3, graph3JSON=graph3Json, header4=header4)
'''
if __name__ == "__main__": 
    print(" * Going for dataset preprocessing")
    preprocessed_df = preprocess(df, region_df)
    print(" * Preprocessing completed!!! ")
    app.run(debug=True,port=5001)
'''
