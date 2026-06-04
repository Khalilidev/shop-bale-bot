# پروژه مدیریت دفتر حساب فروشگاه با ربات بله

رباتی برای مدیریت حساب مشتریان فروشگاه که امکان ثبت مشتری، مدیریت بدهی و دریافت گزارش PDF را فراهم می‌کند.


## مقدمه
این پروژه با تمرکز بر سادگی استفاده از ربات توسط فروشنده توسعه پیدا کرده است و تا حد امکان سعی شده فروشنده تعامل
ساده تر و موثر تری با ربات داشته باشد.


## ویژگی ها
- افزودن مشتری با استفاده از نام و شماره تلفن و مبلغ بدهی به همراه جزئیات لازم.

- امکان افزایش و کاهش بدهی مشتریان با وارد کردن  شماره تلفن

- دریافت فایل PDF گزارش از تمام مشتریان

- ذخیره همه ی اطلاعات در دیتابیس

## تکنولوژی‌های مورد استفاده

- Python 3.12
- balebot
- reportlab
- arabic_reshaper
- python-bidi


## نحوه نصب و استفاده
1- ایجاد محیط مجازی پایتون:


```python3 -m venv venv```

2- نصب پکیج ها در محیط مجازی:

```pip install -r requirements.txt```


3- نام کاربری ```@botfather``` را در بله جستجو کنید و یک توکن ربات دریافت کنید.
(ممکن است لازم باشد ارتقای سطح انجام دهید. که بهتر است این کار را انجام دهید) سپس توکن دریافتی را کپی کنید
و فایل ```config.py``` را باز کنید و توکن را آنجا در بخش مربوط قرار دهید و مطابق با راهنمایی همان فایل، مراحل را پیش ببرید.


4- در نهایت فایل ```main.py``` را در این مسیر و به این صورت اجرا کنید:

cd shop
python3 main.py


5- تبریک!. ربات اجرا شد و اکنون می توانید از آن استفاده کنید

## ساختار پروژه

shop/

├── callbacks/

│ ├── cb_main_menu_seller.py

│ └── cb_seller_account_book.py

│

├── core/

│ ├── bot.py

│ └── logging.py

│

├── databases/

│ └── init.py

│

├── handlers/

│ ├── add_customer_to_db.py

│ ├── customer_debt_report.py

│ ├── get_customer_debt.py

│ └── start_seller.py

│

├── keyboards/

│ ├── customer/

│ └── seller/

│ ├── account_book/

│ │ └── main_menu_account_book.py

│ └── main_menu_seller.py

│

├── texts/

│ └── seller_texts.py

│

├── configs.py

├── main.py

├── Vazir.ttf

└── README.md

## راه های ارتباطی
t.me   : @khalilidev


bale   : @khalilidev


Email : imaliasgharkhalili@gmail.com