import streamlit as st
import mysql.connector
from PIL import Image
import mysql.connector
import plotly.graph_objects as go
import plotly.express as px
from datetime import date
import hashlib

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

mydb = mysql.connector.connect(host="localhost",user="root",password="aryanag@5602",db = "SHOPPER")
c = mydb.cursor(buffered=True)

def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS usertable(username VARCHAR(255),password VARCHAR(255),state VARCHAR(255))')

def add_userdata(username,password,state):
    a = "INSERT INTO usertable(username,password,state) VALUES (%s,%s,%s)"
    val = (username,password,state)
    c.execute(a,val)
    mydb.commit()

def login_user(username,password):
    a = "SELECT * FROM usertable WHERE username = %s AND password = %s"
    val = (username,password)
    c.execute(a,val)
    data = c.fetchall()
    if len(data) > 0 :
        return True
    else:
        return False

def view_all_users():
    c.execute('SELECT * FROM usertable')
    data = c.fetchall()
    return data

def check(name):
    a = "SELECT * FROM usertable WHERE username = %s"
    val = name
    c.execute(a,(val,))
    res = c.fetchall()
    if (len(res) > 0):
        return False
    else:
        return True

def add_order(product_name,cate,pro,sql_pro,state,idd,dop):
    cat = cate
    product = product_name
    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME = %s"
    val = sql_pro
    c.execute(sql,(val,))
    myresult = c.fetchone()
    total = str(pro* int(myresult[0]))
    cost = str(myresult[0])
    quantity = pro
    query = "INSERT INTO TYU(ID,DOP,CATEGORY,PRODUCT,QUANTITY,COST,TOTAL,STATE) VALUES(%s,%s,%s,%s,%s,%s,%s,%s)"
    vals = (idd,dop,cat,product,quantity,cost,total,state)
    c.execute(query,vals)
    mydb.commit()

def main():
    cursor = mydb.cursor(buffered=True)
    #img = Image.open('dbmsProjectImages\samsung.jpg')
    #st.image('dbmsProjectImages\SHOPPER.png', width=1000,height=300)#use_column_width=True)
    menu = ["Login","SignUp"]
    choice = st.sidebar.selectbox("Menu",menu)
    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password",type='password')
        if st.sidebar.checkbox("Login"):
            hashed_pswd = make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:
                if username == 'admin':
                    st.info('Logged in as admin')
                    cursor.execute("SELECT * FROM TYU")
                    myresult = cursor.fetchall()
                    # df = pd.DataFrame(myresult,
                    #                   columns=['ID', 'Date of Purchase', 'Category', 'Product', 'Quantity',
                    #                            'Unit Price', 'Total Cost',
                    #                            'State'])
                    # df['Total Cost'] = df['Total Cost'].astype('int')
                    # cursor.execute("CREATE TABLE TYU_SHOPPER (ID VARCHAR(255),DOP VARCHAR(255),CATEGORY VARCHAR(255),PRODUCT VARCHAR(255),QUANTITY VARCHAR(10),COST VARCHAR(10),TOTAL INT UNSIGNED,STATE VARCHAR(255));")
                    cursor.execute("ALTER TABLE TYU MODIFY COLUMN TOTAL int;")
                    cursor.execute("SELECT STATE, SUM(TOTAL) FROM TYU GROUP BY STATE;")

                    re = cursor.fetchall()
                    states = []
                    values = []
                    for i in re:
                        states.append(i[0])
                        values.append(i[1])
                    fig = go.Figure(go.Pie(labels=states, values=values, textinfo="percent"))
                    st.subheader("State-wise Revenue")
                    st.plotly_chart(fig)

                    cursor.execute("SELECT STATE, COUNT(TOTAL) FROM TYU GROUP BY STATE;")

                    re = cursor.fetchall()
                    states = []
                    values = []
                    for i in re:
                        states.append(i[0])
                        values.append(i[1])

                    fig = px.bar(x=states, y=values)
                    st.subheader("State-wise Number of Bills")
                    st.plotly_chart(fig)

                    cursor.execute("SELECT CATEGORY, SUM(TOTAL) FROM TYU GROUP BY CATEGORY;")
                    re = cursor.fetchall()
                    category = []
                    values = []
                    for i in re:
                        category.append(i[0])
                        values.append(i[1])

                    fig1 = px.bar(y=category, x=values, orientation='h', )
                    st.subheader("Category-wise Revenue")
                    st.plotly_chart(fig1)

                    cursor.execute("SELECT * FROM TYU;")
                    re = cursor.fetchall()
                    months = []
                    values = []
                    for i in re:
                        dat = i[1][::-1]
                        ind = dat.index("-")
                        l = int(len(dat))
                        rev = l - 5
                        x = dat[(ind + 1):rev]
                        x = x[::-1]
                        months.append(x)
                        values.append(i[6])
                    c = []
                    d = []
                    month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                    for x in months:
                        if x not in c:
                            c.append(x)
                    for i in range(len(c)):
                        total = 0
                        for j in range(len(months)):
                            if c[i] == months[j]:
                                total = total + values[j]
                        d.append(total)
                    fig2 = px.line(x=month, y=d)
                    st.subheader("Month-wise Revenue")
                    st.plotly_chart(fig2)
                    col1, col2, col3 = st.columns(3)
                    with col2:
                        delete = st.button("Delete Records")
                        if delete:
                            cursor.execute("TRUNCATE TABLE TYU;")
                else:
                    st.success("Logged In as {}".format(username))
                    a = "SELECT STATE FROM usertable WHERE username = %s;"
                    cursor.execute(a,(username,))
                    res = cursor.fetchall()
                    state = str(res[0][0])
                    a = "SELECT ID FROM TYU ORDER BY ID DESC LIMIT 1;"
                    cursor.execute(a)
                    res = cursor.fetchall()
                    idd = str(int(res[0][0]) + 1 )
                    dop = str(date.today())
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Mobiles')
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.subheader("Iphone")
                        img = Image.open('dbmsProjectImages\iphone.jpg')
                        st.image(img, use_column_width=True, caption="Rs. 89999/-")
                        iphone = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=41)
                    with col2:
                        st.subheader("Samsung")
                        img = Image.open('dbmsProjectImages\samsung.jpg')
                        st.image(img, use_column_width=True, caption="Rs. 69999/-")
                        samsung = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=42)
                    with col3:
                        st.subheader("OnePlus")
                        img = Image.open('dbmsProjectImages\oneplus.jpg')
                        st.image(img, use_column_width=True, caption="Rs. 39999/-")
                        onelpus = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=43)
                    col4, col5 = st.columns(2)
                    with col4:
                        st.subheader("Google")
                        img = Image.open('dbmsProjectImages\google.jpg')
                        st.image(img, width=225, caption="Rs. 49999/-")
                        google = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=44)
                    with col5:
                        st.subheader("Oppo")
                        img = Image.open('dbmsProjectImages\op.jpg')
                        st.image(img, width=300, caption="Rs. 19999/-")
                        oppo = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=45)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Electronics')
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.subheader("TV")
                        img = Image.open('dbmsProjectImages\mi.jpg')
                        st.image(img, use_column_width=True, caption="Rs. 50000/-")
                        tv = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=46)
                    with col2:
                        st.subheader("Monitor")
                        img = Image.open('dbmsProjectImages\monitor.jpg')
                        st.image(img, use_column_width=True, caption="Rs. 7500/-")
                        monitor = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=47)
                    with col3:
                        st.subheader("Camera")
                        img = Image.open('dbmsProjectImages\camera.jpg')
                        st.image(img, use_column_width=True, caption="Rs. 40000/-")
                        camera = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=48)
                    col4, col5 = st.columns(2)
                    with col4:
                        st.subheader("Laptop")
                        img = Image.open('dbmsProjectImages\laptop.jpg')
                        st.image(img,width=225, caption="Rs. 55000/-")
                        laptop = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=49)
                    with col5:
                        st.subheader("Fitness")
                        img = Image.open('dbmsProjectImages\watch.jpg')
                        st.image(img,width=225, caption="Rs. 4500/-")
                        fitness = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1, key=50)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Home Appliances')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("AC")
                        img = Image.open('DbmsProjectImages/Ac.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 35000/-")
                        ac = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=1)
                    with col2:
                        st.subheader("Mixer")
                        img = Image.open('DbmsProjectImages/mixer.png')
                        st.image(img,use_column_width=True,caption="Rs. 6000/-")
                        mixer = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=5)
                    with col3:
                        st.subheader("Microwave")
                        img = Image.open('DbmsProjectImages/oven.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 10000/-")
                        microwave = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=3)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("Fridge")
                        img = Image.open('DbmsProjectImages/fridge.jpg')
                        st.image(img,width=100,caption="Rs. 20000/-")
                        fridge = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=4)
                    with col5:
                        st.subheader("Wash")
                        img = Image.open('DbmsProjectImages/washing.jpg')
                        st.image(img,width=100,caption="Rs. 25000/-")
                        wash = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=2)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Home Decor')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Clock")
                        img = Image.open('DbmsProjectImages/clock.jpg')
                        st.image(img,use_column_width=True,caption="Rs 600/-")
                        clock = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=6)
                    with col2:
                        st.subheader("Curtian")
                        img = Image.open('DbmsProjectImages/curtain.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 699/-")
                        curtain = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=7)
                    with col3:
                        st.subheader("Table Decor")
                        img = Image.open('DbmsProjectImages/table.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 399/-")
                        table = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=8)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("Painting")
                        img = Image.open('DbmsProjectImages/paint.jpg')
                        st.image(img,width=100,caption="Rs. 400/-")
                        painting = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=9)
                    with col5:
                        st.subheader("Bedsheet")
                        img = Image.open('DbmsProjectImages/bedsheet.jpg')
                        st.image(img,width=100,caption="Rs. 1099/-")
                        bedsheet = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=10)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Sports & Outdoors')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Cricket Kit")
                        img = Image.open('DbmsProjectImages/cric.jpg')
                        st.image(img,width=200,caption="Rs. 9000/-")
                        cricket = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=11)
                    with col2:
                        st.subheader("Basketball")
                        img = Image.open('DbmsProjectImages/basket.jpg')
                        st.image(img,width=200,caption="Rs. 799/-")
                        basketball = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=12)
                    with col3:
                        st.subheader("Football")
                        img = Image.open('DbmsProjectImages/football resize.jpg')
                        st.image(img,width=200,caption="Rs. 899/-")
                        football = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=13)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("TT Table")
                        img = Image.open('DbmsProjectImages/tt.jpg')
                        st.image(img,width=100,caption="Rs. 8500/-")
                        tt = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=14)
                    with col5:
                        st.subheader("Golf")
                        img = Image.open('DbmsProjectImages/golf.jpg')
                        st.image(img,width=100,caption="Rs. 80000/-")
                        golf = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=15)
                    a,b,c = st.columns(3)
                    with b:
                        st.subheader('Clothing')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Tshirt Men")
                        img = Image.open('DbmsProjectImages/tshirt.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 500/-")
                        tshirt = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=16)
                    with col2:
                        st.subheader("Bottom Wear")
                        img = Image.open('DbmsProjectImages/jean.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 800/-")
                        bottom = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=17)
                    with col3:
                        st.subheader("Shirts(Men)")
                        img = Image.open('DbmsProjectImages/shirt.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 750/-")
                        shirt = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=18)
                    col4,col5,col6 = st.columns(3)
                    with col4:
                        st.subheader("Jacket")
                        img = Image.open('DbmsProjectImages/women.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 1000/-")
                        jacket = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=19)
                    with col5:
                        st.subheader("Kids Wear")
                        img = Image.open('DbmsProjectImages/kids.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 400/-")
                        kids = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=20)
                    with col6:
                        st.subheader("Accessories")
                        img = Image.open('DbmsProjectImages/access.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 650/-")
                        accessories = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=21)
                    col1,col2 = st.columns(2)
                    with col1 :
                        st.subheader("Women's Ethnic")
                        img = Image.open('DbmsProjectImages/ethnic.jpg')
                        st.image(img,width=100,caption="Rs. 600/-")
                        womenethnic = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=51)
                    with col2:
                        st.subheader("Women's Western")
                        img = Image.open('DbmsProjectImages/western.jpg')
                        st.image(img,width=100,caption="Rs. 700/-")
                        womenwestern = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=52)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Footwear')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Sports wear")
                        img = Image.open('DbmsProjectImages/sport shoe.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 1200/-")
                        sportshoe = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=211)
                    with col2:
                        st.subheader("Sandals")
                        img = Image.open('DbmsProjectImages/sandal.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 700/-")
                        sandal = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=22)
                    with col3:
                        st.subheader("Casual Shoes")
                        img = Image.open('DbmsProjectImages/casual shoes.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 600/-")
                        casualshoe = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=23)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("Flip Flops")
                        img = Image.open('DbmsProjectImages/flip.jpg')
                        st.image(img,width=100,caption="Rs. 300/-")
                        flipflop = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=24)
                    with col5:
                        st.subheader("School Shoes")
                        img = Image.open('DbmsProjectImages/school.jpg')
                        st.image(img,width=100,caption="Rs. 499/-")
                        schoolshoe = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=25)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Books')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Comics")
                        img = Image.open('DbmsProjectImages/comic.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 199/-")
                        comic = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=26)
                    with col2:
                        st.subheader("Sci-Fi")
                        img = Image.open('DbmsProjectImages/scienc.jpg')
                        st.image(img,use_column_width=True,caption="RS. 299/-")
                        scifi = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=27)
                    with col3:
                        st.subheader("History")
                        img = Image.open('DbmsProjectImages/history.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 249/-")
                        history = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=28)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("Biography")
                        img = Image.open('DbmsProjectImages/bio.jpg')
                        st.image(img,width=100,caption="Rs. 359/-")
                        biography = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=29)
                    with col5:
                        st.subheader("Literature")
                        img = Image.open('DbmsProjectImages/literature.jpg')
                        st.image(img,width=100,caption="Rs. 299/-")
                        literature = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=30)
                    a,b,c = st.columns(3)
                    with b:
                        st.subheader('Grocery')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Beverages")
                        img = Image.open('DbmsProjectImages/beverages.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 65/-")
                        beverage = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=31)
                    with col2:
                        st.subheader("Dairy")
                        img = Image.open('DbmsProjectImages/dairy.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 40/-")
                        dairy = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=32)
                    with col3:
                        st.subheader("fruits")
                        img = Image.open('DbmsProjectImages/fruits.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 100/-")
                        fruit = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=33)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("Vegetables")
                        img = Image.open('DbmsProjectImages/vege.jpg')
                        st.image(img,width=100,caption="Rs. 80/-")
                        vegetable = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=34)
                    with col5:
                        st.subheader("Packaged Foods")
                        img = Image.open('DbmsProjectImages/packed.jpg')
                        st.image(img,width=100,caption="Rs. 130/-")
                        packaged = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=35)
                    a,b,c = st.columns(3)
                    with b :
                        st.subheader('Beauty & Health')
                    col1,col2,col3 = st.columns(3)
                    with col1:
                        st.subheader("Sunscreen")
                        img = Image.open('DbmsProjectImages/unscreen.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 269/-")
                        sunscreen = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=36)
                    with col2:
                        st.subheader("Lipbalm")
                        img = Image.open('DbmsProjectImages/lipbalm.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 79/-")
                        lipbalm = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=37)
                    with col3:
                        st.subheader("Lipsticks")
                        img = Image.open('DbmsProjectImages/lipstick.jpg')
                        st.image(img,use_column_width=True,caption="Rs. 130/-")
                        lipstick = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=38)
                    col4,col5 = st.columns(2)
                    with col4:
                        st.subheader("Makeup Kit")
                        img = Image.open('DbmsProjectImages/makeup.jpg')
                        st.image(img,width=100,caption="Rs. 899/-")
                        makeup = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=39)
                    with col5:
                        st.subheader("Moisturizer")
                        img = Image.open('DbmsProjectImages/moisturizer.jpg')
                        st.image(img,width=100,caption="Rs. 349/-")
                        moist = st.number_input("Quantity", min_value=0, max_value=15, value=0, step=1,key=40)
                    total = 0
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='iphone'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + iphone* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='samsung'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + samsung* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='oneplus'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + onelpus* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='oppo'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + oppo* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='google'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + google* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='tv'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + tv* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='monitor'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + monitor* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='camera'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + camera* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='laptop'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + laptop* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='fitness'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + fitness* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='ac'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + ac* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='mixer'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + mixer* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='wash'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + wash* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='microwave'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + microwave* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='fridge'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + fridge* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='clock'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + clock* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='curtain'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + curtain* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='table'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + table* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='painting'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + painting* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='bedsheet'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + bedsheet* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='cricket'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + cricket* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='basketball'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + basketball* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='football'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + football* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='tt'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + tt* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='golf'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + golf* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='tshirt'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + tshirt* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='bottomwear'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + bottom* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='shirt'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + shirt* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='jacket'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + jacket* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='womenethnic'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + womenethnic* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='womenwestern'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + womenwestern* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='kids'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + kids* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='accessories'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + accessories* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='sportshoes'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + sportshoe* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='sandal'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + sandal* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='casualshoes'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + casualshoe* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='flipflop'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + flipflop* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='schoolshoes'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + schoolshoe* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='comic'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + comic* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='scifi'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + scifi* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='history'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + history* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='literature'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + literature* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='biography'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + biography* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='fruit'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + fruit* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='vegetable'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + vegetable* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='dairy'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + dairy* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='packaged'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + packaged* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='beverage'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + beverage* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='sunscreen'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + sunscreen* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='lipbalm'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + lipbalm* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='lipstick'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + lipstick* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='moisturizer'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + moist* int(myresult[0])
                    sql = "SELECT PRICE FROM PRODUCTS WHERE NAME ='makeupkit'"
                    cursor.execute(sql)
                    myresult = cursor.fetchone()
                    total = total + makeup* int(myresult[0])
                    st.info("Total cart value : {}".format(total))
                    col1,col2,col3 = st.columns(3)
                    with col2:
                        con = st.button('Confirm Order')
                        if con:
                            if iphone > 0:
                                add_order('Apple','Mobiles',iphone,'iphone',state,idd,dop)
                            if samsung > 0:
                                 add_order('Samsung','Mobiles',samsung,'samsung',state,idd,dop)
                            if onelpus > 0:
                                add_order('Oneplus','Mobiles',onelpus,'oneplus',state,idd,dop)
                            if google > 0:
                                add_order('Google','Mobiles',google,'google',state,idd,dop)
                            if oppo > 0:
                                add_order('Oppo','Mobiles',oppo,'oppo',state,idd,dop)
                            if tv > 0:
                                add_order('TV','Electronics',tv,'tv',state,idd,dop)
                            if monitor > 0:
                                add_order('Monitor','Electronics',monitor,'monitor',state,idd,dop)
                            if camera > 0:
                                add_order('Camera','Electronics',camera,'camera',state,idd,dop)
                            if laptop > 0:
                                add_order('Laptop','Electronics',laptop,'laptop',state,idd,dop)
                            if fitness > 0:
                                add_order('Fitness Tracker','Electronics',fitness,'fitness',state,idd,dop)
                            if ac > 0:
                                add_order('AC','Home Appliances',ac,'ac',state,idd,dop)
                            if fridge > 0:
                                add_order('Fridge','Home Appliances',fridge,'fridge',state,idd,dop)
                            if microwave > 0:
                                add_order('Microwave','Home Appliances',microwave,'microwave',state,idd,dop)
                            if mixer > 0:
                                add_order('Mixer','Home Appliances',mixer,'mixer',state,idd,dop)
                            if wash > 0:
                                add_order('Washing Machine','Home Appliances',wash,'wash',state,idd,dop)
                            if clock > 0:
                                add_order('Clock','Home Decor',clock,'clock',state,idd,dop)
                            if curtain > 0:
                                add_order('Curtain','Home Decor',curtain,'curtain',state,idd,dop)
                            if painting > 0 :
                                add_order('Painting','Home Decor',painting,'painting',state,idd,dop)
                            if table > 0:
                                add_order('Table Decor','Home Decor',table,'table',state,idd,dop)
                            if bedsheet > 0:
                                add_order('Bedsheet','Home Decor',bedsheet,'bedsheet',state,idd,dop)
                            if cricket > 0 :
                                add_order('Cricket kit','Sports & Outdoor',cricket,'cricket',state,idd,dop)
                            if football > 0 :
                                add_order('Football','Sports & Outdoor',football,'football',state,idd,dop)
                            if tt > 0:
                                add_order('TT Table set','Sports & Outdoor',tt,'tt',state,idd,dop)
                            if golf > 0 :
                                add_order('Golf set','Sports & Outdoor',golf,'golf',state,idd,dop)
                            if basketball > 0 :
                                add_order('Basketball','Sports & Outdoor',basketball,'basketball',state,idd,dop)
                            if tshirt > 0 :
                                add_order('Tshirt (men)','Clothing',tshirt,'tshirt',state,idd,dop)
                            if bottom > 0 :
                                add_order('Bottom wear (men)','Clothing',bottom,'bottomwear',state,idd,dop)
                            if shirt >0 :
                                add_order('Shirts (men)','Clothing',shirt,'shirt',state,idd,dop)
                            if jacket > 0 :
                                add_order('Jacket','Clothing',jacket,'jacket',state,idd,dop)
                            if kids  > 0 :
                                add_order('Kids','Clothing',kids,'kids',state,idd,dop)
                            if accessories > 0 :
                                add_order('Accessories','Clothing',accessories,'accessories',state,idd,dop)
                            if womenwestern > 0:
                                add_order('Women Western','Clothing',womenwestern,'womenwestern',state,idd,dop)
                            if womenethnic > 0 :
                                add_order('Women Ethnic','Clothing',womenethnic,'womenethnic',state,idd,dop)                                
                            if sportshoe > 0 :
                                add_order('Sports Shoes','Footwear',sportshoe,'sportshoes',state,idd,dop)
                            if casualshoe > 0 :
                                add_order('Casual Shoes','Footwear',casualshoe,'casualshoes',state,idd,dop)
                            if sandal > 0 :
                                add_order('Sandals','Footwear',sandal,'sandal',state,idd,dop)
                            if flipflop > 0 :
                                add_order('Flip-flops','Footwear',flipflop,'flipflop',state,idd,dop)
                            if schoolshoe > 0 :
                                add_order('School Shoes','Footwear',schoolshoe,'schoolshoes',state,idd,dop)
                            if comic > 0:
                                add_order('Comics','Books',comic,'comic',state,idd,dop)
                            if scifi > 0:
                                add_order('Sci-Fi','Books',scifi,'scifi',state,idd,dop)
                            if history > 0:
                                add_order('History','Books',history,'history',state,idd,dop)
                            if biography > 0 :
                                add_order('Biography','Books',biography,'biography',state,idd,dop)
                            if literature > 0 :
                                add_order('Literature','Books',literature,'literature',state,idd,dop)
                            if packaged > 0 :
                                add_order('Packaged Foods','Grocery',packaged,'packaged',state,idd,dop)
                            if fruit > 0 :
                                add_order('Fruits','Grocery',fruit,'fruit',state,idd,dop)
                            if vegetable > 0 :
                                add_order('Vegatables','Grocery',vegetable,'vegetable',state,idd,dop)
                            if dairy > 0 :
                                add_order('Dairy','Grocery',dairy,'dairy',state,idd,dop)
                            if beverage > 0 :
                                add_order('Beverages','Grocery',beverage,'beverage',state,idd,dop)
                            if lipstick > 0 :
                                add_order('Lipstick','Beauty & Health',lipstick,'lipstick',state,idd,dop)
                            if lipbalm > 0 :
                                add_order('Lipbalm','Beauty & Health',lipbalm,'lipbalm',state,idd,dop)
                            if moist > 0 :
                                add_order('Moisturizer','Beauty & Health',moist,'moisturizer',state,idd,dop)
                            if makeup > 0 :
                                add_order('Makeup kit','Beauty & Health',makeup,'makeupkit',state,idd,dop)
                            if sunscreen > 0:
                                add_order('Sunscreen','Beauty & Health',sunscreen,'sunscreen',state,idd,dop)
                            st.success('Order confirmed')
                            idd = str(int(idd) + 1)
            else:
                st.warning("Incorrect Username/Password")
                
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password',key=1000)
        new_password1 = st.text_input("Confirm Password", type='password',key=1001)
        stateList = ["Delhi", "Karnataka","Maharashtra","Tamil Nadu","West Bengal"]
        stateResiding = st.selectbox("State", stateList)
        if st.button("Signup"):
            ch = check(new_user)
            if ch == True:
                if(new_password==new_password1):
                    create_usertable()
                    add_userdata(new_user,make_hashes(new_password),stateResiding)
                    st.success("Account Created!")
                    st.info("Go to Login Menu to login")
                else:
                    st.warning('Password dont match')
            else:
                st.warning('Username already exists')

if __name__ == '__main__':
    main()