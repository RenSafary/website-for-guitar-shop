from fastapi import FastAPI, Request, Form, HTTPException, Depends, File, UploadFile
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
import bcrypt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import os
import uuid

from .models import User, Order, Product, Category
from .config import UPLOAD_DIR
from .user import get_current_user

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def main_page(request: Request):
    user = get_current_user(request)

    # Пример данных изображений
    images = [{"url": "logo1.jpg"}, {"url": "logo2.jpg"}, {"url": "logo3.jpg"}]

    return templates.TemplateResponse(
        "main.html",
        {
            "request": request,
            "user": user or {},
            "images": images,
        },
    )


# Страница с авторазицией
@app.get("/authorization", response_class=HTMLResponse)
async def authorization(request: Request):
    return templates.TemplateResponse(
        "accounting/authorization_form.html", {"request": request}
    )


@app.post("/sign-in")
async def sign_in(
    request: Request, username: str = Form(...), password: str = Form(...)
):
    # Получаем пользователя из базы данных
    user = User.get_or_none(User.username == username)

    if user:
        password_bytes = password.encode("utf-8")
        hashed_password_bytes = user.password.encode("utf-8")

        # Проверяем, совпадает ли введенный пароль с хэшем
        if bcrypt.checkpw(password_bytes, hashed_password_bytes):
            request.session["user_id"] = user.id
            return RedirectResponse(url="/", status_code=303)

    # Если пользователь не найден или пароль не совпадает
    raise HTTPException(status_code=401, detail="Неверные учетные данные")


# Страница регистрации
@app.get("/sign-up", response_class=HTMLResponse)
async def sign_up(request: Request):
    return templates.TemplateResponse("accounting/sign-up.html", {"request": request})


# Получение данных и запись в бд
@app.post("/sign-up-create-user")
async def sign_up_create_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
):
    # хэширование пароля
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    # запись в бд
    user = User(
        email=email,
        username=username,
        password=hashed_password.decode("utf-8"),
        is_superuser=False,
    )
    user.save()

    request.session["user_id"] = user.id
    # перенаправление на главную страницу
    return RedirectResponse(url="/", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user_id", None)
    return RedirectResponse(url="/", status_code=303)


@app.get("/add-product", response_class=HTMLResponse)
async def add_product(request: Request):
    categories = Category.select()
    return templates.TemplateResponse(
        "adm_panel/product/add_product.html",
        {"request": request, "categories": categories},
    )


@app.post("/add-product/action")
async def add_product_action(
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    photo: UploadFile = File(...),
    category_id: int = Form(...),  # Добавляем выбор категории
):
    # Проверяем, существует ли категория
    try:
        category = Category.get_by_id(category_id)
    except Category.DoesNotExist:
        raise HTTPException(status_code=400, detail="Категория не найдена")

    # Проверяем, является ли файл изображением
    if not photo.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Файл должен быть изображением")

    # Генерируем уникальное имя файла
    file_extension = photo.filename.split(".")[-1]  # Получаем расширение файла
    unique_filename = (
        f"{uuid.uuid4().hex}.{file_extension}"  # Генерируем уникальное имя
    )
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Сохраняем файл на сервере
    with open(file_path, "wb") as buffer:
        buffer.write(await photo.read())

    # Сохраняем данные в базе данных
    product = Product(
        name=name,
        description=description,
        price=price,
        photo_url=unique_filename,  # Сохраняем только имя файла
        category=category,  # Связываем продукт с категорией
    )
    product.save()

    # Перенаправляем с сообщением об успешном добавлении
    return RedirectResponse(url=f"/?success=true", status_code=303)


@app.get("/edit-product", response_class=HTMLResponse)
async def edit_product(request: Request):
    categories = Category.select()
    products = Product.select()

    return templates.TemplateResponse(
        "adm_panel/product/edit_product.html",
        {"request": request, "categories": categories, "products": products},
    )


@app.post("/edit-product-action")
async def edit_product_action(request: Request):
    # Получаем данные формы
    form_data = await request.form()

    # Обрабатываем данные
    for key, value in form_data.items():
        if key.startswith("product_name_"):
            product_id = int(key.replace("product_name_", ""))
            name = value
            description = form_data.get(f"product_description_{product_id}")
            price = form_data.get(f"product_price_{product_id}")

            if not (name and description and price):
                raise HTTPException(status_code=400, detail="Invalid form data")

            # Обновляем продукт в базе данных
            product = Product.get_or_none(Product.id == product_id)
            if product:
                product.name = name
                product.description = description
                product.price = int(price)
                product.save()

    # Перенаправляем обратно на страницу редактирования
    return RedirectResponse(url="/edit-product", status_code=303)


@app.get("/delete_product/{product_id}")
async def delete_product(product_id: int):
    product = Product.get_or_none(Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.delete_instance()
    return RedirectResponse(url="/edit-product", status_code=303)


@app.get("/accoustic", response_class=HTMLResponse)
async def accoustic_guitars(request: Request):
    user = get_current_user(request)

    category = Category.get(name="Акустические гитары")
    products = Product.select().where(Product.category == category.id)

    return templates.TemplateResponse(
        "categories/accoustic.html",
        {
            "request": request,
            "category": category,
            "products": products,
            "user": user or {},
        },
    )


@app.post("/creating-order", response_class=HTMLResponse)
async def creating_order(
    request: Request,
    category: str = Form(...),
    product_name: str = Form(...),
):
    user = get_current_user(request)
    print(user)
    product = Product.get_or_none(name=product_name)
    print(product.name)
    if product and user:
        order = Order.create(ordered_by=user.id, product=product.id, amount=1)

    return RedirectResponse(url="/cart", status_code=303)


@app.get("/classic", response_class=HTMLResponse)
async def classic_guitars(request: Request):
    user = get_current_user(request)

    category = Category.get(name="Классические гитары")
    products = Product.select().where(Product.category == category.id)

    return templates.TemplateResponse(
        "categories/classic.html",
        {
            "request": request,
            "category": category,
            "products": products,
            "user": user or {},
        },
    )


@app.get("/electro", response_class=HTMLResponse)
async def electro_guitars(request: Request):
    user = get_current_user(request)

    category = Category.get(name="Электрические гитары")
    products = Product.select().where(Product.category == category.id)

    return templates.TemplateResponse(
        "categories/electro.html",
        {
            "request": request,
            "category": category,
            "products": products,
            "user": user or {},
        },
    )


@app.get("/accessories", response_class=HTMLResponse)
async def accessories(request: Request):
    user = get_current_user(request)

    category = Category.get(name="Аксессуары")
    products = Product.select().where(Product.category == category.id)

    return templates.TemplateResponse(
        "categories/accessories.html",
        {
            "request": request,
            "category": category,
            "products": products,
            "user": user or {},
        },
    )


@app.get("/adm-panel", response_class=HTMLResponse)
async def adm_panel(request: Request):
    user = get_current_user(request)
    if not user or not user.is_superuser:
        raise HTTPException(status_code=403, detail="Доступ запрещен")

    return templates.TemplateResponse(
        "adm_panel/adm_main_page.html",
        {
            "request": request,
            "user": user or {},
        },
    )


@app.get("/control_users", response_class=HTMLResponse)
async def control_users(request: Request):
    users = User.select()
    return templates.TemplateResponse(
        "adm_panel/control users/users.html",
        {
            "request": request,
            "users": users,
        },
    )


@app.get("/delete-user/{user_id}", response_class=HTMLResponse)
async def delete_user(user_id: int, request: Request):
    user = User.get_or_none(User.id == user_id)
    if user:
        user.delete_instance()
    return RedirectResponse(url="/control_users", status_code=303)


@app.get("/make-admin/{user_id}", response_class=HTMLResponse)
async def make_admin(user_id: int, request: Request):
    user = User.get_or_none(User.id == user_id)
    if user:
        User.update(is_superuser=True).where(User.id == user_id).execute()
    return RedirectResponse(url="/control_users", status_code=303)


@app.get("/cart", response_class=HTMLResponse)
async def cart(request: Request):
    user = get_current_user(request)

    if not user:
        # Пользователь не залогинен
        return RedirectResponse(url="/authorization", status_code=303)

    orders = Order.select().where(Order.ordered_by == user.id)
    products = [order.product for order in orders]
    total_sum = sum(
        product.price * order.amount for product, order in zip(products, orders)
    )

    return templates.TemplateResponse(
        "cart/cart.html",
        {
            "request": request,
            "products": products,
            "user": user or {},
            "total_sum": total_sum,
        },
    )


@app.post("/delete-from-cart", response_class=RedirectResponse)
async def delete_from_cart(
    request: Request,
    product: int = Form(...),
):
    user = get_current_user(request)

    order = Order.get_or_none(product=product, ordered_by=user.id)
    if order:
        order.delete_instance()

    return RedirectResponse(url="/cart", status_code=303)


@app.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request):
    user = get_current_user(request)

    if not user:
        return RedirectResponse(url="/authorization", status_code=303)

    # Пример очистки корзины
    orders = Order.select().where(Order.ordered_by == user.id)
    for order in orders:
        order.delete_instance()

    return templates.TemplateResponse(
        "cart/checkout.html",
        {"request": request},
    )
