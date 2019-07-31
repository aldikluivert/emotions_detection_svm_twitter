from flask import Flask, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, validators, IntegerField
from analisis import analisis
from flask_bootstrap import Bootstrap
from datetime import date

app = Flask(__name__)
app.secret_key = 'hhh'
Bootstrap(app)

a = analisis()
today = date.today()

@app.route('/', methods=['GET', 'POST'])
def home():
    tanggal = today.strftime('%d %B %y')
    form = f()
    if form.validate_on_submit():
        if request.method=='POST':
            datas = (a.processing(keyword=form.keyword.data, jumlah=form.jumlah.data))
            clf_result = datas[0]
            persen = datas[1]
            count = len(datas[2])
            return render_template('output.html', clf_result=clf_result, keyword=form.keyword.data, persen=persen,
                                   tanggal=tanggal, count=count)
    return render_template('input.html', form=form)

class f(FlaskForm):
    keyword = StringField('keyword', validators=[validators.InputRequired(message='Form ini wajib diisi!')])
    jumlah = IntegerField('jumlah', validators=[validators.InputRequired(message='Form ini wajib diisi!'),
                                                validators.number_range
                                                (min=20, max=100, message='angka jumlah minimal 20 dan maximal 100')])

if __name__ == '__main__':
    app.run(debug=True)