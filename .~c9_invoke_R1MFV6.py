from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

from time import gmtime, strftime

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
db = SQL("sqlite:///finance.db")

# ------------------------------------------------


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Current shares onhand
    rows = db.execute('''SELECT symbol, SUM(shares) as sharesTotal
                      FROM transactions
                        JOIN users ON transactions.id = users.id
                      WHERE transactions.id=:id
                      GROUP BY symbol
                      HAVING sharesTotal > 0''',
                      id=session["user_id"])

    # Look up name,current price of each stock symbol
    name = []
    latestPrice = []
    total = []
    for row in rows:
        lookUpDict = lookup(row["symbol"])
        name.append(lookUpDict["name"])
        latestPrice.append(usd(lookUpDict["price"]))
        total.append(lookUpDict["price"] * row["sharesTotal"])

    # Current cash onhand
    rowsCash = db.execute('''SELECT cash FROM users WHERE id=:id''', id=session["user_id"])
    cash = rowsCash[0]["cash"]

    # TODO
    return render_template("index.html", len=len(rows),
                            rows=rows, cash=cash,
                            name=name, latestPrice=latestPrice,
                            total=total, totalSum=sum(total) + cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbolBuy = request.form.get("symbolBuy")
        sharesBuy = int(request.form.get("sharesBuy"))
        if not symbolBuy or sharesBuy <= 0:
            return apology("must provide symbol and shares of stock.")

        # Look up current price
        try:
            price = lookup(symbolBuy)["price"]  #price type: float in Dictionary , or None if invalid symbol
            total = price * sharesBuy
        except TypeError:
            return apology("symbol not exist.")

        # Ready to UPDATE database
        rows = db.execute("SELECT * FROM users WHERE id = :id", id=session["user_id"])
        cash = rows[0]["cash"] - total
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())

        # Check affordability
        # UPDATE users table after bought
        # INSERT transactions table after bought
        if cash < 0:
            return apology("cash not enough.")
        else:
            db.execute("UPDATE users SET cash=:cash WHERE id =:id",
                       cash=cash-total,
                       id=session["user_id"])
            db.execute('''INSERT INTO transactions (id,symbol,shares,price,total,time)
                          VALUES (:id, :symbol, :shares, :price, :total, :time)''',
                          id=session["user_id"],
                          symbol=symbolBuy,
                          shares=sharesBuy,
                          price=price,
                          total=total,
                          time=time)

        flash("Bought")

        # Redirect user to home page
        return redirect("/")

    else:
        if request.args.get("symbol"):
            return render_template("buy.html", symbol=request.args.get("symbol"), shares = request.args.get("shares"))


        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    rows = db.execute('''SELECT symbol,shares,price,time
                        FROM transactions WHERE id=:id''',
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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("quote")
        if not symbol:
            return apology("must provide a symbol of stock")
        result = lookup(symbol) #type:Dictionary, or None if invalid symbol
        if result:
            return render_template("quote.html", result=result)
        else:
            return apology("symbol not exist")

    else:
        return render_template("quote.html")


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


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":
        symbolSell = request.form.get("symbolSell")
        sharesSell = int(request.form.get("sharesSell"))
        if sharesSell <= 0:
            return apology("must provide shares of stock.")

        # Look up current price
        price = lookup(symbolSell)["price"] #price type: float in Dictionary, or None if invalid symbol
        total = price * sharesSell


        # Ready to UPDATE database (set handy vaiables)
        rows = db.execute("SELECT * FROM users WHERE id=:id", id=session["user_id"])
        cash = rows[0]["cash"] + total
        time = strftime("%Y-%m-%d %H:%M:%S", gmtime())


        # Check saleable
        # UPDATE users table after sold
        # INSERT transactions table after sold
        sharesTotal = db.execute('''SELECT SUM(shares) FROM transactions WHERE id=:id AND symbol=:symbol''',
                                    id=session["user_id"], symbol=symbolSell)
        if int(sharesTotal[0]["SUM(shares)"]) < sharesSell:
            return apology("Shares not enough.")
        else:
            db.execute("UPDATE users SET cash=:cash WHERE id = :id",
                        cash=cash,
                        id=session["user_id"])
            db.execute('''INSERT INTO transactions (id,symbol,shares,price,total,time)
                         VALUES (:id, :symbol, :shares, :price, :total, :time)''',
                        id=session["user_id"],
                        symbol=symbolSell,
                        shares= -sharesSell,  # /... negative num means sell .../
                        price=price,
                        total=total,
                        time=time)

        flash("sold")

        return redirect("/")

    else:
        # set up elements in select menu
        symbols = db.execute('''SELECT symbol, SUM(shares) as sharesTotal
                                FROM transactions
                                WHERE id=:id
                                GROUP BY symbol
                                HAVING sharesTotal > 0''',
                                id = session["user_id"])

        if request.args.get("symbol"):
            return render_template("sell.html",
                                    symbols = symbols,
                                    symbol = request.args.get("symbol"),
                                    shares = request.args.get("shares") )

        return render_template("sell.html", symbols = symbols)

# ----------------------------------


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
