from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from time import gmtime, strftime
import ast
import re
from helpers import prettify

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///user.db")
db2 = SQL("sqlite:///subtitles_cs50.db")

# ------------------------------------------------


# <-----------Query for Pos tag------------------>
@app.route("/", methods=["GET", "POST"])
# @login_required
def index():
    """Show query and search result"""
    if request.method == "POST":
        query = request.form.get("query")
        match = []
        if query:
            rows = db2.execute('''SELECT koPos.id, pos, tag, sentence
                                  FROM koPos
                                   JOIN koSentence ON koPos.id = koSentence.id''')
            flash("query | " + query + " | ")

            for i in range(0, len(rows)):                    # eg. rows[i]['tag'] is a stirng, could be   "[['SS'], ['XPN', 'NNG'], ['NNG', 'SS']]"
                tag_list = ast.literal_eval(rows[i]['tag'])  # eg. from string representation of a list to list: ['SS'], ['XPN', 'NNG'], ['NNG', 'SS']
                #if query.split() in tag_list:               # BUGGGGGG: 只會擷取有單獨存在的query : ['NNG'] 而不會有['XPN', ['NNG']，解法見下
                for j in tag_list:
                    if query in j:                           # eg. if "SS" in ['SS'] ? if in  ['XPN', 'NNG']? if in  ['NNG', 'SS'] ?
                        match.append(rows[i]['sentence'])
                        flash(i)
                        break                                # 這樣上面那個例子才不會 append兩次!!!!!!!
        else:
            return apology("query no result")

        if match:
            return render_template("index.html", len=len(match), match=match)
        else:
            return render_template("predicative.html", len=len(match))

    else:
        return render_template("index.html")

# <-----------Query for predicative case------------------>
@app.route("/predicative", methods=["GET", "POST"])
# @login_required
def predicative():

    """ if POST to user's Sentence Book """
    if request.method == "POST" and "sentence_book" in request.form:

        flash("Added to my sentence book")

        # access selected senteces numbers
        input_sentence_book = request.form.get("sentence_book")
        input_sentence_book = input_sentence_book.split(",")  # string "16,20" to list
        flash(input_sentence_book)

        # Settings for data UPDATE / READ
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        # UPDATE sentencebook table
        for i in input_sentence_book:
            print(i)
            rows3 = db.execute('''INSERT INTO sentencebook (id,sentence,time)
                                 VALUES (:id, :sentence, :time)''',
                                 id = 1995,
                                 sentence = i,
                                 time=time)


        return render_template("predicative.html")

    """Show query and search result"""
    if request.method == "POST":
        analyze query input """
        query = request.form.get("query")
        if query[-2:] == '하다':
            stem = query[:-2]
            stem_Regex = re.compile(stem + r"/NNG*")   # 之後查POS用，例如[['사랑/NNG', '하/XSV', '는/ETD'], ['이/NNG', '들/XSN', '의/JKG']]]
        elif query[-3:] == '스럽다':
            stem = query[:-3]
            stem_Regex = re.compile(stem + r"/NNG")   # 之後查POS用，例如　자연/NNG | 스럽/XSA | 죠/EFN |
        elif query[-1:] == '다':
            stem = query[:-1]
            stem_Regex = re.compile(stem + r"/V.*")    # 之後查POS用，例如　이러/VV | 고/ECE | 자/VV  排除남자, 자신....
        else:
            return apology(f"Please use basic form only")


        # Settings for data UPDATE / READ
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        match_ko = []
        match_en = []
        match_zh = []
        match_id = []

        """ UPDATE history table """
        """
        rows = db.execute('''INSERT INTO history (id,query,time)
                             VALUES (:id, :query, :time)''',
                             id = session["user_id"],
                             query = query,
                             time=time)
        """

        """ READ koPos table"""
        if stem:
            rows2 = db2.execute('''SELECT koPos.id, pos, tag, morphs, koSentence.sentence AS stn_ko,
                                         koSentence_en.sentence AS stn_en, koSentence_zh.sentence AS stn_zh
                                  FROM koPos
                                   JOIN koSentence ON koPos.id = koSentence.id
                                   JOIN koSentence_en ON koPos.id = koSentence_en.id
                                   JOIN koSentence_zh ON koPos.id = koSentence_zh.id''')


            flash("query | " + query)
            #flash("| stem | " + stem + " | ")

            for i in range(0, len(rows2)):                          # eg. rows2[i]['pos'] is a stirng, could be   "[['도깨비/NNG', '가/JKC'], ['되/VV', 'ㄴ단다/EFN']]"
                pos_list = ast.literal_eval(rows2[i]['pos'])  # eg. from string representation of a list to list: [['도깨비/NNG', '가/JKC'], ['되/VV', 'ㄴ단다/EFN']]
                for j in pos_list:                           # type(j) == list
                    for word in j:
                        if stem_Regex.search(word):                 # eg. if 되/VV in  [['도깨비/NNG', '가/JKC'], ['되/VV', 'ㄴ단다/EFN']] in rows[i]['pos'
                            # append Ko matched result to list
                            stn_ko = rows2[i]['stn_ko']
                            stn_ko = prettify(stn_ko)
                            match_ko.append(stn_ko)

                            # append eng matched result to list
                            stn_en = rows2[i]['stn_en']
                            stn_en = prettify(stn_en)
                            match_en.append(stn_en)

                            # append zh matched result to list
                            stn_zh = rows2[i]['stn_zh']
                            stn_zh = prettify(stn_zh)
                            match_zh.append(stn_zh)

                            # append matched sentence id to list
                            match_id.append(rows2[i]['id'])

                            #flash(i)
                            break                                      # 這樣上面那些例子才不會 append兩次!!!!!!!

        else:
            return apology("query no result")

        if match_ko:
            return render_template("predicative.html", len=len(match_ko), match_ko=match_ko, match_en=match_en, match_zh=match_zh, match_id=match_id, stem=stem)
        else:
            return render_template("predicative.html", len=len(match_ko))

    else:
        return render_template("predicative.html")

# <-----------Query for Noun case------------------>
@app.route("/noun", methods=["GET", "POST"])
# @login_required
def noun():
    """Show query and search result"""
    if request.method == "POST":
        query = request.form.get("query")
        match = []
        if query:
            rows = db2.execute('''SELECT koPos.id, tag, morphs, sentence
                                  FROM koPos
                                   JOIN koSentence ON koPos.id = koSentence.id''')



            flash("query | " + query + " | ")

            for i in range(0, len(rows)):
                    morphs_list = ast.literal_eval(rows[i]['morphs'])  # eg. from string to list: ['SS'] | ['XPN', 'NNG'] | ['NNG', 'SS']
                    for j in morphs_list:
                        if query in j:                           # eg. if "SS" in ['SS'] ? if in  ['XPN', 'NNG']? if in  ['NNG', 'SS'] ?
                            sentence = rows[i]['sentence']
                            sentence = prettify(sentence)
                            match.append(sentence)
                            break                                # 這樣上面那個例子才不會 append兩次!!!!!!!

        else:
            return apology("query no result")

        if match:
            return render_template("noun.html", len=len(match), match=match)
        else:
            return render_template("noun.html", len=len(match))

    else:
        return render_template("noun.html")


# ---------------------------------------------------------



@app.route("/sentencebook", methods=["GET", "POST"])
@login_required
def sentencebook():
    """Show favorite sentence stored by user"""

    # Settings for data UPDATE / READ
    match_ko = []
    match_en = []
    match_zh = []


    # READ combined sentnece table & koSentence
    # DANGUROUS: Sould conbine in same db
    # 目前暫時先分開DB ...(這樣太複雜，趕快合併吧！)
    # sentencebook.sentence 改成 sentencebook.sentence_id 應該會比較清楚
    rows = db.execute('''SELECT id, sentence, time
                                koSentence.sentence AS stn_ko,
                                koSentence_en.sentence AS stn_en,
                                koSentence_zh.sentence AS stn_zh
                        FROM sentencebook WHERE id=:id
                         JOIN koSentence ON sentencebook.sentence = koSentence.id
                         JOIN koSentence_en ON sentnecebook.sentence = koSentence_en.id
                         JOIN koSentence_zh ON sentnecebook.sentence = koSentence_zh.id''',
                        id=session["user_id"])

    for i in range(0, len(rows)):
        match_ko.append(rows[i]['stn_ko'])
        match_en.append(rows[i]['stn_en'])
        match_zh.append(rows[i]['stn_zh'])

    return render_template("sentencebook.html", len=len(rows), rows=rows, match_ko=match_ko, match_en=match_en, match_zh=match_zh)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute('''SELECT id,query,time
                        FROM history WHERE id=:id''',
                        id=session["user_id"])

    return render_template("history.html",len=len(rows),rows=rows)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Logged in")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Ensure two passwords is identical
        elif request.form.get("password2") != request.form.get("password2"):
            return apology("passwords must be same", 403)

        # Query database for UPDATE
        db.execute('''INSERT INTO users (username,hash)
                   VALUES (:username, :hash)''',
                   username=request.form.get("username"),
                   hash=generate_password_hash(request.form.get("password")))

        rows = db.execute("SELECT * FROM users WHERE username = :username", \
                           username=request.form.get("username"))

        # log user in
        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        flash("Registered")

        # Redirect user to home page
        return redirect("/")

    else:
        return render_template("register.html")


# ----------------------------------


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
