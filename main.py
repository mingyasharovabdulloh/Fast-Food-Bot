from telegram import Update,ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup,LabeledPrice
from telegram.ext import Updater, CommandHandler,CallbackContext,MessageHandler, Filters, ConversationHandler,CallbackQueryHandler,PreCheckoutQueryHandler
import db,json

TOKEN="8665340690:AAGOCwXlpyEAC6uobAJyDJ8z0J8vGHbEY18"
PROVIDER_TOKEN='371317599:TEST:1789836758755'
ADMIN_LOGIN='admin_01'
ADMIN_PASSWORD='Admin112233'

(NAME,PHONE,LOCATION,MAIN_MENU,EDIT_NAME,EDIT_PHONE,SETTINGS_MENU,FOOD_MENU,CATEGORY_NAME,CATEGORY_CODE,IZOH)=range(11)
(ADMIN_LOGIN_STATE,ADMIN_PASSWORD_STATE,ADMIN_MENU) = range(11,14)
(LIST_PRODUCT,DELETE_CATEGORY,DELETE_PRODUCT) = range(14,17)
(PRODUCT_NAME,PRODUCT_PRICE,PRODUCT_IMAGE,PRODUCT_CATEGORY,PRODUCT_DESCRIPTION)=range(17,22)
(CHANGE_PRODUCT_DATA,CHANGE_DATA_MENU)=range(22,24)
(NEW_PRODUCT_NAME,NEW_PRODUCT_PRICE,NEW_PRODUCT_DESC,NEW_PRODUCT_IMAGE)=range(24,28)
(AD_IMAGE,AD_CAPTION,AD_CONFIRM)=range(28,31)

def start(update : Update, context : CallbackContext):
    user=db.get_user(update.effective_user.id)

    if user:
        return main_menu(update,context)

    update.message.reply_text(
        "Assalomu alaykum\n"
        "Ism Familyangzni kiriting : "
    )

    return NAME

def get_name(update : Update, context : CallbackContext):
    context.user_data["name"]=update.message.text
    update.message.reply_text(
        "Telefon raqamingizni kiriting : ",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Raqam yuborish",request_contact=True)]],
            resize_keyboard=True
        )
    )

    return PHONE

def get_phone(update : Update, context : CallbackContext):
    context.user_data["phone"]=update.message.contact.phone_number
    update.message.reply_text(
        "Joylashuvingizni yuboing : ",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton("Joylashuvingizni yuborish :",request_location=True)]],
            resize_keyboard=True
        )
    )

    return LOCATION

def get_location(update : Update, context : CallbackContext):
    loc=update.message.location

    db.add_user(
        update.effective_user.id,
        context.user_data["name"],
        context.user_data["phone"],
        loc.latitude,
        loc.longitude
    )

    update.message.reply_text("Ro'yhatdan o'tdingiz !")
    return main_menu(update,context)

def main_menu(update : Update, context : CallbackContext):
    update.message.reply_text(
        "Asosiy menu :",
        reply_markup=ReplyKeyboardMarkup(
            [
                ["📋 Menyu","🛒 Savat"],
                ["⚙️ Sozlamalar"],
                ["✍ Izoh qoldirish"]
            ],
            resize_keyboard=True
        )
    )

    return MAIN_MENU

def main_menu_select(update : Update, context : CallbackContext):
    text=update.message.text

    if text=="🛒 Savat":
        return show_cart(update,context)

    if text=="📋 Menyu":
        return food_menu(update,context)

    if text=="⚙️ Sozlamalar":
        return settings_menu(update,context)

    if text =="✍ Izoh qoldirish":
        update.message.reply_text("Izoh qoldiring !")
        return IZOH

def description(update : Update, context : CallbackContext):
    text=update.message.text
    id=update.effective_user.id
    data=[]

    data.append({
        "User ID" : id,
        "Description" : text
    })

    with open("Descriptions.json", mode='w', encoding='utf-8') as file:
        json.dump(data , file , indent=4 , ensure_ascii=False)

    update.message.reply_text(
        "Izohingiz uchun rahmat !"
    )
    return MAIN_MENU


def show_cart(update : Update, context : CallbackContext):
    cart=context.user_data.get("cart")

    if not cart:
        update.message.reply_text("Savat bo'sh !")
        return MAIN_MENU

    text="Savatingiz :\n"
    total=0

    for item in cart:
        summa=item['price'] * item['qty']
        total+=summa
        text+=f"{item['name']} x {item['qty']}= {summa} so'm\n"
    text+=f"Jami : {total} so'm"

    keyboard=InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Buyurtma berish",
                callback_data="order_confirm"
            ),
            InlineKeyboardButton(
                "❌ Bekor qilish",
                callback_data="order_cancel"
            )
        ]
    ])

    update.message.reply_text(text, reply_markup=keyboard)
    return MAIN_MENU

def food_menu(update : Update, context : CallbackContext):
    categories = db.get_category()

    if not categories:
        update.message.reply_text(
            "📭 Menyu hozircha bo'sh!"
        )
        return main_menu(update, context)

    keyboard = []

    for category in categories:
        keyboard.append([
            KeyboardButton(category[0])
        ])

    keyboard.append([
        KeyboardButton("⬅️ Orqaga")
    ])

    update.message.reply_text(
        "Menyulardan birini tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        )
    )

    return FOOD_MENU

def food_menu_select(update : Update, context : CallbackContext):
    text=update.message.text

    if text == "⬅️ Orqaga":
        return main_menu(update,context)

    category_code=db.get_category_code(text)

    product=db.get_product_by_category(category_code)

    if not product:
        update.message.reply_text(
            "Product xali mavjud emas !"
        )
        return FOOD_MENU

    keyboard=[
                [InlineKeyboardButton(p[1], callback_data=f"product_{p[0]}")]
                for p in product
            ]
    
    update.message.reply_text(f"{text} birini tanlang: ",
                              reply_markup=InlineKeyboardMarkup(keyboard))
    return FOOD_MENU


def settings_menu(update : Update, context : CallbackContext):
    update.message.reply_text("Ma'lumotlarni tahrirlash: ",
                              reply_markup=ReplyKeyboardMarkup(
                                  [
                                      ["Ism familya"],
                                      ["Telefon raqam"],
                                      ["⬅️ Orqaga"]
                                  ],
                                  resize_keyboard=True
                              ))

    return SETTINGS_MENU

def settings_select(update : Update, context : CallbackContext):
    text=update.message.text

    if text == "Ism familya":
        update.message.reply_text("Yangi ism kiriting : ")
        return EDIT_NAME

    if text == "Telefon raqam":
        update.message.reply_text("Yangi telefon raqam yuboring : ",
                                  reply_markup=ReplyKeyboardMarkup(
                                      [[KeyboardButton("Raqam yuborish",request_contact=True)]],resize_keyboard=True
                                  ))

    if text == "⬅️ Orqaga":
        return main_menu(update, context)

def edit_name(update : Update, context : CallbackContext):
    db.update_name(update._effective_user.id,update.message.text)
    update.message.reply_text("Ism familya o'zgartirildi !")
    return main_menu(update, context)

def edit_phone(update : Update, context : CallbackContext):
    db.update_phone(update.effective_user.id, update.message.contact.phone_number)
    update.message.reply_text("Telefon raqam o'zgartirildi !")
    return main_menu(update, context)

def product_callback(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    ol_msg_id=context.user_data.get("product_message_id")

    if ol_msg_id:
        try:
            context.bot.delete_message(
                chat_id=query.message.chat_id,
                message_id=ol_msg_id
            )
        except:
            pass

    product_id=int(query.data.split("_")[1])
    product=db.get_product(product_id)

    context.user_data["current_product"] = {
        "id" : product[0],
        "name" : product[1],
        "price" : product[2],
        "desc" : product[3],
        "image" : product[4]
    }

    context.user_data["qty"] = 1

    msg=query.message.reply_photo(
        photo=product[4],
        caption=(
            f"{product[1]}\n\n"
            f"Narxi : {product[2]} so'm\n"
            f"Miqdori : 1\n"
            f"{product[3]}"
        ),
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("-", callback_data="qty_minus"),
                InlineKeyboardButton("1", callback_data="noop"),
                InlineKeyboardButton("+", callback_data="qty_plus"),
            ],
            [
                InlineKeyboardButton(
                    "🛒 Savatga qo'shish",
                    callback_data="add_to_cart"
                )
            ]
        ])
    )

    context.user_data["product_message_id"]=msg.message_id

def send_product_card_first(query : Update, context: CallbackContext):
    product=context.user_data["current_product"]
    qty=context.user_data["qty"]

    keyboard=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➖", callback_data="qty_minus"),
                InlineKeyboardButton(str(qty), callback_data="noop"),
                InlineKeyboardButton("➕", callback_data="qty_plus"),
            ],
            [
                InlineKeyboardButton(
                    "🛒 Savatga qo'shish",
                    callback_data="add_to_cart"
                )
            ]
        ])

    caption=(
        f"{product['name']}\n"
        f"Narxi : {product['price']} so'm\n"
        f"Miqdori : {qty}\n"
        f"{product['desc']}"
    )

    query.edit_message_caption(
        photo=product['image'],
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )

def send_product_card_update(query : Update, context : CallbackContext):
    if not query.message.photo:
        return

    product=context.user_data.get("current_product")
    qty=context.user_data.get("qty",1)

    if not product:
        return

    keyboard=InlineKeyboardMarkup([
            [
                InlineKeyboardButton("➖", callback_data="qty_minus"),
                InlineKeyboardButton(str(qty), callback_data="noop"),
                InlineKeyboardButton("➕", callback_data="qty_plus"),
            ],
            [
                InlineKeyboardButton(
                    "🛒 Savatga qo'shish",
                    callback_data="add_to_cart"
                )
            ]
    ])

    caption=(
        f"{product['name']}\n"
        f"Narxi : {product['price']} so'm\n"
        f"Miqdori : {qty}\n"
        f"{product['desc']}"
    )

    query.edit_message_caption(
        caption=caption,
        parse_mode="HTML",
        reply_markup=keyboard
    )

def cart_callback(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    if not query.message.photo:
        return

    product=context.user_data.get("current_product")

    if not product:
        return

    qty=context.user_data.get("qty",1)

    if query.data == "qty_plus":
        qty+=1

    elif query.data == "qty_minus":
        if qty > 1 :
            qty-=1

    elif query.data == "add_to_cart":
        context.user_data.setdefault("cart",[]).append({
            "id" : product['id'],
            "name" : product['name'],
            "price" : product['price'],
            "qty" : qty
        })
        query.message.reply_text("Mahsulot savatga qo'shildi ✅")
        return

    context.user_data['qty'] = qty

    keyboard = [
            [
                InlineKeyboardButton("➖", callback_data="qty_minus"),
                InlineKeyboardButton(str(qty), callback_data="noop"),
                InlineKeyboardButton("➕", callback_data="qty_plus"),
            ],
            [
                InlineKeyboardButton(
                    "🛒 Savatga qo'shish",
                    callback_data="add_to_cart"
                )
            ]
        ]
    
    query.edit_message_caption(
            caption=(
                f"{product['name']}\n\n"
                f"Narxi: {product['price']} so'm\n"
                f"Miqdori: {qty}\n\n"
                f"{product['desc']}"
            ),
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
def order_callback(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    if query.data == "order_confirm":
        cart=context.user_data.get("cart",[])

        if not cart:
            query.message.reply_text("Savat bo'sh")
            return

        prices=[]
        total=0

        for item in cart:
            amount=item["price"]*item["qty"]
            total+=amount
            prices.append(
                LabeledPrice(
                    label=f"{item['name']} x {item['qty']}",
                    amount=amount * 100
                )
            )

        context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title="Buyurtma uchun to'lov",
            description="Buyurtmani qabul qilish uchun jarayonni davom ettiring !",
            payload="order_payment_payload",
            provider_token=PROVIDER_TOKEN,
            currency="UZS",
            prices=prices,
            start_parameter="food_order"
        )

    elif query.data == "order_cancel":
        context.user_data['cart'] = []
        query.message.delete()
        query.message.chat.send_message("Buyurtma bekor qilindi !")

def precheckout_callback(update : Update, context : CallbackContext):
    query=update.pre_checkout_query

    if query.invoice_payload != "order_payment_payload":
        query.answer(
            ok=False,
            error_message="Buyurtma ma'lumotlari notog'ri!"
        )
        return

    query.answer(ok=True)

    print("Pre Checkout Accepted !!!")

def succesful_payment_callback(update : Update, context : CallbackContext):
    payment=update.message.successful_payment

    context.user_data["cart"]=[]

    update.message.reply_text(
        "✅ To'lov muvaffaqiyatli amalga oshirildi!\n"
        f"Summa : {payment.total_amount / 100 : ,.0f} so'm\n"
        f"Payment ID : {payment.telegram_payment_charge_id}"
    )

def admin_start(update : Update, context : CallbackContext):
    update.message.reply_text(
        "Admin loginini kiriting :"
    )

    return ADMIN_LOGIN_STATE

def check_login(update : Update, context : CallbackContext):
    text=update.message.text

    if text == ADMIN_LOGIN:
        update.message.reply_text(
            "Parolni kiriting :"
        )
        return ADMIN_PASSWORD_STATE

    update.message.reply_text(
        "Login xato ❌"
    )

    return ConversationHandler.END

def check_password(update : Update, context : CallbackContext):
    text=update.message.text

    if text == ADMIN_PASSWORD:
        update.message.reply_text(
            "Admin paneliga xush kelibsiz ✅"
        )
        return admin_menu(update,context)

    update.message.reply_text("Parol xato ❌")

def admin_callback(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    if query.data == "add_new_product":
        categories = db.get_category()

        if not categories:
            query.message.reply_text(
                "Productni qo'shish uchun category mavjud emas ❌"
            )
            return admin_menu(update,context)

        keyboard = [
            [
                InlineKeyboardButton(
                    name,
                    callback_data=f"product_category_{code}"
                )
            ]
            for name, code in categories
        ]

        query.message.reply_text(
            "Qaysi categoryga product qo'shmoqchisiz : ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return PRODUCT_CATEGORY
    
    if query.data == "add_new_category":
        query.message.reply_text(
            "Category uchun yangi name kiriting : "
        )
        return CATEGORY_NAME

    if query.data == "list_categories":
        categories=db.list_categories()

        if not categories:
            query.message.reply_text(
                "Category list ni ko'rish uchun ma'lumot mavjud emas ❌"
            )
            return admin_menu(update,context)

        text=  "=====================\n"
        text+= "||       Categories           ||\n"
        text+= "=====================\n"

        for category in categories:
            name=category[0]
            text+=f"||   {name :<20}    ||\n"
            text+= "=====================\n"

        query.message.reply_text(
            text
        )
        return admin_menu(update,context)
        

    if query.data == "list_products":
        categories=db.get_category()

        if not categories:
            query.message.reply_text(
                "Productni list ni ko'rish uchun ma'lumot mavjud emas ❌"
            )
            return admin_menu(update,context)
        
        keyboard=[
                [
                    InlineKeyboardButton(
                        name,
                        callback_data=f"list_{code}"
                    )
                ]
                for name , code in categories
        ]

        query.message.reply_text(
            "Qaysi cartegory dagi productlarni ko'rmoqchisiz : ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return LIST_PRODUCT

    if query.data == "del_category":
        categories=db.get_category()

        if not categories:
            query.message.reply_text(
                "Category list ni o'chirish uchun ma'lumot mavjud emas ❌"
            )
            return admin_menu(update,context)
        
        keyboard=[
                [
                    InlineKeyboardButton(
                        name,
                        callback_data=f"del_cat_{code}"
                    )
                ]
                for name , code in categories
        ]

        keyboard.append([
        InlineKeyboardButton(
            "⬅️ Orqaga",
            callback_data="admin_back"
            )
        ])

        query.message.reply_text(
            "Qaysi cartegory ni o'chirmoqchisiz : ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return DELETE_CATEGORY

    if query.data == "del_product":
        categories = db.get_category()

        if not categories:
            query.message.reply_text(
                "Product list ni o'chirish uchun ma'lumot mavjud emas ❌"
            )
            return admin_menu(update,context)

        keyboard = [
            [
                InlineKeyboardButton(
                    name,
                    callback_data=f"delete_product_category_{code}"
                )
            ]
            for name, code in categories
        ]

        keyboard.append([
            InlineKeyboardButton(
                "⬅️ Orqaga",
                callback_data="admin_back"
            )
        ])

        query.message.reply_text(
            "Qaysi categorydagi productni o'chirmoqchisiz?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        return DELETE_PRODUCT

    if query.data=="change_data":
        categories=db.get_category()

        if not categories:
            query.message.reply_text(
                "Product ni datasini o'zgartirish uchun ma'lumot mavjud emas ❌",
            )
            return admin_menu(update,context)

        keyboard = [
                    [
                        InlineKeyboardButton(
                            name,
                            callback_data=f"change_product_data_{code}"
                        )
                    ]
                    for name, code in categories
                ]
        
        keyboard.append([
                    InlineKeyboardButton(
                        "⬅️ Orqaga",
                        callback_data="admin_back"
                    )
                ])

        query.message.reply_text(
            "Qaysi category dagi product ni data sini change qilmoqchisiz : ",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CHANGE_PRODUCT_DATA

    if query.data == "add_ads":
        query.message.reply_text(
            "Reklama qo'shish uchun image yuboring :"
        )
        return AD_IMAGE

def admin_menu(update, context):
    update.effective_message.reply_text(
        "⬇️ Quyidagi kategoriyalardan birini tanlang ⬇️",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Yangi category qo'shish",
                    callback_data="add_new_category"
                ),
                InlineKeyboardButton(
                    "Yangi product qo'shish",
                    callback_data="add_new_product"
                )
            ],
            [
                InlineKeyboardButton(
                    "List categories",
                    callback_data="list_categories"
                ),
                InlineKeyboardButton(
                    "List products",
                    callback_data="list_products"
                )
            ],
            [
                InlineKeyboardButton(
                    "Categoryni o'chirish",
                    callback_data="del_category"
                ),
                InlineKeyboardButton(
                    "Productni o'chirish",
                    callback_data="del_product"
                )
            ],
            [
                InlineKeyboardButton(
                    "Change product data",
                    callback_data='change_data'
                ),
                InlineKeyboardButton(
                    "Reklama qo'shish",
                    callback_data="add_ads"
                )
            ]
        ])
    )

    return ADMIN_MENU

def get_category_name(update : Update, context : CallbackContext):
    context.user_data["category_name"] = update.message.text

    update.message.reply_text(
        "Category uchun code ni kiriting : \n"
        "Masalan : Burger"
    )

    return CATEGORY_CODE

def get_category_code(update : Update, context : CallbackContext):
    code=update.message.text
    name=context.user_data["category_name"]

    db.add_category(name,code)

    update.message.reply_text(
        "Yangi category muvaffaqiyatli qo'shildi ✅"
    )
    return admin_menu(update,context)            

def get_product_name(update : Update, context : CallbackContext):
    context.user_data["product_name"] = update.message.text

    update.message.reply_text(
        "Product uchun price ni kiriting UZS da :"
    )

    return PRODUCT_PRICE

def get_product_price(update : Update, context : CallbackContext):
    context.user_data["product_price"] = update.message.text

    update.message.reply_text(
        "Product uchun description kiriting :"
    )
    return PRODUCT_DESCRIPTION

def get_product_description(update : Update, context : CallbackContext):
    context.user_data["product_description"] = update.message.text

    update.message.reply_text(
        "Product uchun image yuboring : "
    )
    return PRODUCT_IMAGE

def get_product_image(update : Update, context : CallbackContext):
    context.user_data["product_image"] = update.message.photo[-1].file_id

    db.add_product(
        context.user_data["product_name"],
        context.user_data["product_price"],
        context.user_data["product_description"],
        context.user_data["product_image"],
        context.user_data["category_code"]
    )

    update.message.reply_text(
        "Yangi product muvaffaqiyatli qo'shildi ✅"
    )

    return admin_menu(update, context)

def product_category_callback(update : Update, context : CallbackContext):
    query = update.callback_query
    query.answer()

    category_code = query.data.split("_")[2]

    context.user_data["category_code"] = category_code

    query.message.reply_text(
        "Product uchun yangi name kiriting : "
    )

    return PRODUCT_NAME

def list_products_callback(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    list_code=query.data.split("_")[1]

    products=db.list_products(list_code)

    if not products:
        query.message.reply_text(
            "Bu categoryda product mavjud emas ❌"
        )
        return admin_menu(update, context)

    
    text=  "=====================\n"
    text+= "||       Products           ||\n"
    text+= "=====================\n"

    for product in products:
        name=product[0]
        text+=f"||   {name :<20}    ||\n"
        text+= "=====================\n"

    query.message.reply_text(
        text
    )
    return admin_menu(update,context)

def delete_category(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    if query.data == "admin_back":
        return admin_menu(update,context)

    del_cat_code=query.data.split("_")[2]

    db.del_category(del_cat_code)

    query.message.reply_text(
        "Siz aytgan category o'chirildi ✅"
    )
    return admin_menu(update, context)

def delete_product_category_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    category_code = query.data.split("_")[3]

    products = db.list_products(category_code)

    if not products:
        query.message.reply_text(
            "Bu categoryda product mavjud emas ❌"
        )
        return admin_menu(update, context)

    keyboard = [
        [
            InlineKeyboardButton(
                product[0],
                callback_data=f"delete_product_{product[0]}"
            )
        ]
        for product in products
    ]

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Orqaga",
            callback_data="admin_back"
        )
    ])

    query.message.reply_text(
        "Qaysi productni o'chirmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return DELETE_PRODUCT

def delete_product_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    if query.data == "admin_back":
        return delete_product_category_callback(update,context)

    product_name = query.data.split("_", 2)[2]

    db.del_products(product_name)

    query.message.reply_text(
        f"{product_name} muvaffaqiyatli o'chirildi ✅"
    )

    return admin_menu(update, context)

def change_product_data(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    # Category tanlanganda
    if query.data.startswith("change_product_data_"):
        category_code = query.data.split("_")[3]

        # Categoryni saqlab qo'yamiz
        context.user_data["change_category_code"] = category_code

    # back_to_products bosilganda
    elif query.data == "back_to_products":
        category_code = context.user_data.get("change_category_code")

    else:
        return admin_menu(update, context)

    if not category_code:
        return admin_menu(update, context)

    products = db.list_products(category_code)

    if not products:
        query.message.reply_text(
            "Bu categoryda product mavjud emas ❌"
        )
        return admin_menu(update, context)

    keyboard = [
        [
            InlineKeyboardButton(
                product[0],
                callback_data=f"change_product_{product[0]}"
            )
        ]
        for product in products
    ]

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Orqaga",
            callback_data="admin_back"
        )
    ])

    query.message.reply_text(
        "Qaysi productni o'zgartirmoqchisiz?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHANGE_PRODUCT_DATA

def change_product_data_callback(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    if query.data == "admin_back":
        return change_product_data(update,context)

    product_name = query.data.split("_", 2)[2]

    context.user_data["old_name"] = product_name
    
    keyboard=[
            [
                InlineKeyboardButton(
                    "Ismni o'zgartirish",
                    callback_data="change_product_name"
                ),
                InlineKeyboardButton(
                    "Narxni o'zgartirish",
                    callback_data="change_product_price"
                )
            ],
            [
                InlineKeyboardButton(
                    "Description ni o'zgartirish",
                    callback_data="change_product_desc"
                ),
                InlineKeyboardButton(
                    "Image ni o'zgartirish",
                    callback_data="change_product_image"
                )
            ]
        ]

    keyboard.append([
        InlineKeyboardButton(
            "⬅️ Orqaga",
            callback_data="back_to_products"
        )
    ])

    query.message.reply_text(
        "Qaysi data ni o'zgartirmoqchisiz : ",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    return CHANGE_DATA_MENU

def change_data_specific(update :Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    if query.data=="change_product_name":
        query.message.reply_text(
            "Product uchun yangi name kiriting : " 
        )
        return NEW_PRODUCT_NAME

    if query.data=="change_product_price":
        query.message.reply_text(
            "Product uchun yangi price kiriting : " 
        )
        return NEW_PRODUCT_PRICE

    if query.data=="change_product_desc":
        query.message.reply_text(
            "Product uchun yangi description kiriting : " 
        )
        return NEW_PRODUCT_DESC

    if query.data=="change_product_image":
        query.message.reply_text(
            "Product uchun yangi image yuboring : " 
        )
        return NEW_PRODUCT_IMAGE

    if query.data =="back_to_products":
        return change_product_data(update,context)
    
def change_new_name(update : Update, context : CallbackContext):
    text=update.message.text
    old_name=context.user_data["old_name"]

    if not old_name:
        return admin_menu(update,context)

    db.change_product_name(text,old_name)

    update.message.reply_text(
        "Product name yangilandi ✅"
    )
    return CHANGE_DATA_MENU

def change_new_price(update : Update, context : CallbackContext):
    text=update.message.text
    old_name=context.user_data["old_name"]

    if not old_name:
        return admin_menu(update,context)

    db.change_product_price(text,old_name)

    update.message.reply_text(
        "Product price yangilandi ✅"
    )
    return CHANGE_DATA_MENU

def change_new_desc(update : Update, context : CallbackContext):
    text=update.message.text
    old_name=context.user_data["old_name"]

    if not old_name:
        return admin_menu(update,context)

    db.change_product_desc(text,old_name)

    update.message.reply_text(
        "Product desc yangilandi ✅"
    )
    return CHANGE_DATA_MENU

def change_new_image(update : Update, context : CallbackContext):
    text=update.message.photo[-1].file_id
    old_name=context.user_data["old_name"]

    if not old_name:
        return admin_menu(update,context)

    db.change_product_image(text,old_name)

    update.message.reply_text(
        "Product image yangilandi ✅"
    )
    return CHANGE_DATA_MENU

def add_advertisement_image(update : Update, context : CallbackContext):
    image=update.message.photo[-1].file_id

    context.user_data["image"]=image
    update.message.reply_text(
        "Reklama captionini yuboring :"
    )
    return AD_CAPTION

def add_advertisement_caption(update : Update, context : CallbackContext):
    text=update.message.text

    context.user_data["caption"]=text
    update.message.reply_text(
        "Sizning reklamangiz tayyor ✅\n"
        "Yuborishni tasdiqlaysizmi ?",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Yuborish ✅",
                    callback_data="send_ad"
                ),
                InlineKeyboardButton(
                    "Bekor qilish ❌",
                    callback_data="cancel_ad"
                )
            ]
        ])
    )

    return AD_CONFIRM

def send_advertisement(update : Update, context : CallbackContext):
    query=update.callback_query
    query.answer()

    users=db.get_all_users()

    success=[]
    failed=[]

    image=context.user_data["image"]
    caption=context.user_data['caption']

    if not image or not caption:
        query.message.reply_text(
            "Reklama ma'lumotlari topilmadi ❌"
        )
        return ADMIN_MENU

    for user in users:
        tg_id=user[0]

        try:
            context.bot.send_photo(
                chat_id=tg_id,
                photo=image,
                caption=caption
            )

            success.append({
                "ID" : {tg_id},
                "Status" : "Yuborildi ✅"
            })

        except Exception as e:
            failed.append({
                "ID" : tg_id,
                "Status" : "Yuborilmadi ❌"
            })

    text=(
        "📊 Reklama natijasi\n\n"
        f"👥 Jami user: {len(users)}\n"
        f"✅ Yuborildi: {len(success)}\n"
        f"❌ Yuborilmadi: {len(failed)}"
    )

    query.message.reply_text(text)

    query.message.reply_text(
        "File da qaysi userlarga reklama borgan yoki bormaganini ko'rishingiz mumkin ❗️"
    )

    with open("advertisement_result.txt", mode="w",encoding="utf-8") as file:

        file.write("📊 REKLAMA NATIJASI\n\n")

        file.write(f"Jami user: {len(users)}\n")
        file.write(f"Yuborildi: {len(success)}\n")
        file.write(f"Yuborilmadi: {len(failed)}\n\n")

        file.write("================================\n")
        file.write("REKLAMA BORGAN USERLAR ✅\n")
        file.write("================================\n\n")

        for tg_id in success:
            file.write(f"{tg_id}\n")

        file.write("\n================================\n")
        file.write("REKLAMA BORMAGAN USERLAR ❌\n")
        file.write("================================\n\n")

        for tg_id in failed:
            file.write(f"{tg_id}\n")

    with open("advertisement_result.txt",mode="rb") as file:
        context.bot.send_document(
            chat_id=query.message.chat_id,
            document=file
        )

    return admin_menu(update,context)

def cancel_advertisement(update : Update, context : CallbackContext):
    query= update.callback_query
    query.answer()

    context.user_data.pop("image",None)
    context.user_data.pop("caption",None)

    query.message.reply_text(
        "Reklama yuborish bekor qilindi ❌"
    )
    return admin_menu(update,context)
    
def main():
    db.create_table()

    updater=Updater(TOKEN)
    dp=updater.dispatcher

    conv=ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("admin",admin_start)
            ],
        states={
            NAME : [MessageHandler(Filters.text,get_name)],
            PHONE : [MessageHandler(Filters.contact,get_phone)],
            LOCATION : [MessageHandler(Filters.location, get_location)],

            MAIN_MENU : [MessageHandler(Filters.text,main_menu_select)],
            SETTINGS_MENU : [MessageHandler(Filters.text,settings_select)],
            FOOD_MENU : [MessageHandler(Filters.text & ~ Filters.command,food_menu_select)],

            EDIT_NAME : [MessageHandler(Filters.text,edit_name)],
            EDIT_PHONE : [MessageHandler(Filters.contact, edit_phone)],

            IZOH : [MessageHandler(Filters.text & ~ Filters.command,description)],

            ADMIN_LOGIN_STATE : [MessageHandler(Filters.text & ~ Filters.command,check_login)],
            ADMIN_PASSWORD_STATE : [MessageHandler(Filters.text & ~ Filters.command,check_password)],
            ADMIN_MENU : [CallbackQueryHandler(admin_callback)],

            CATEGORY_NAME : [MessageHandler(Filters.text & ~ Filters.command,get_category_name)],
            CATEGORY_CODE : [MessageHandler(Filters.text & ~ Filters.command,get_category_code)],

            PRODUCT_NAME : [MessageHandler(Filters.text & ~ Filters.command,get_product_name)],
            PRODUCT_PRICE : [MessageHandler(Filters.text & ~ Filters.command,get_product_price)],
            PRODUCT_DESCRIPTION : [MessageHandler(Filters.text & ~ Filters.command,get_product_description)],
            PRODUCT_IMAGE : [MessageHandler(Filters.photo,get_product_image)],

            PRODUCT_CATEGORY : [CallbackQueryHandler(product_category_callback,pattern="^product_category_")],
            LIST_PRODUCT : [CallbackQueryHandler(list_products_callback,pattern="^list_")],
            DELETE_CATEGORY : [CallbackQueryHandler(delete_category,pattern="^(del_cat_|admin_back)$")],

            DELETE_PRODUCT : [
                CallbackQueryHandler(
                    delete_product_category_callback,
                    pattern="^delete_product_category_"
                ),
                CallbackQueryHandler(
                    delete_product_callback,
                    pattern="^delete_product_"
                ),
                CallbackQueryHandler(
                    delete_category,
                    pattern="^admin_back$"
                )
            ],

            CHANGE_PRODUCT_DATA : [
                CallbackQueryHandler(
                    change_product_data,
                    pattern="^change_product_data_"
                ),
                CallbackQueryHandler(
                    change_product_data_callback,
                    pattern="^change_product_"
                ),
                CallbackQueryHandler(
                    lambda u, c: admin_menu(u, c),
                    pattern="^admin_back$"
                )
            ],

            CHANGE_DATA_MENU : [CallbackQueryHandler(change_data_specific,pattern="^(change_product_name|change_product_price|change_product_desc|change_product_image|back_to_products)$")],

            NEW_PRODUCT_NAME : [MessageHandler(Filters.text & ~ Filters.command,change_new_name)],
            NEW_PRODUCT_PRICE : [MessageHandler(Filters.text & ~ Filters.command,change_new_price)],
            NEW_PRODUCT_DESC : [MessageHandler(Filters.text & ~ Filters.command,change_new_desc)],
            NEW_PRODUCT_IMAGE : [MessageHandler(Filters.photo,change_new_image)],

            AD_IMAGE : [MessageHandler(Filters.photo,add_advertisement_image)],
            AD_CAPTION : [MessageHandler(Filters.text & ~ Filters.command,add_advertisement_caption)],
            AD_CONFIRM : [CallbackQueryHandler(send_advertisement,pattern='^send_ad$'),CallbackQueryHandler(cancel_advertisement,pattern="^cancel_ad$")],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("admin", admin_start)
        ]
    )

    dp.add_handler(conv)

    dp.add_handler(CallbackQueryHandler(lambda u, c : u.callback_query.answer(),pattern="^noop$"))
    dp.add_handler(CallbackQueryHandler(product_callback,pattern="^product_"))
    dp.add_handler(CallbackQueryHandler(cart_callback,pattern="^(qty_|add_to_cart)"))
    dp.add_handler(CallbackQueryHandler(order_callback,pattern="^order_"))

    dp.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    dp.add_handler(MessageHandler(Filters.successful_payment, succesful_payment_callback))

    updater.start_polling()
    updater.idle()

if __name__=="__main__":
    print("Bot ishga tushdi...")
    main()